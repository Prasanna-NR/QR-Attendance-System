from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Attendance, Task
from app.utils import generate_qr_code, generate_attendance_report, get_qr_code_data, OPENCV_AVAILABLE
from datetime import datetime, date

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

# ==================== AUTH ====================
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        generate_qr_code(user.id)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is inactive. Please contact admin.', 'danger')
                return render_template('login.html')
            
            user.is_logged_in = True
            user.last_login = datetime.utcnow()
            user.last_activity = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    current_user.is_logged_in = False
    current_user.session_id = None
    db.session.commit()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# ==================== MAIN ====================
@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    today_attendance = Attendance.query.filter_by(user_id=current_user.id, date=today).first()
    
    return render_template('dashboard.html',
        is_marked=today_attendance is not None,
        total_attendance=Attendance.query.filter_by(user_id=current_user.id).count(),
        pending_tasks=Task.query.filter_by(user_id=current_user.id, status='pending').count(),
        completed_tasks=Task.query.filter_by(user_id=current_user.id, status='completed').count(),
        recent_attendances=Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.date.desc(), Attendance.time.desc()).limit(5).all(),
        qr_data=get_qr_code_data(current_user.id),
        opencv_available=OPENCV_AVAILABLE
    )

@main.route('/scan_qr')
@login_required
def scan_qr():
    qr_data = get_qr_code_data(current_user.id)
    return render_template('scan_qr.html', 
                         opencv_available=OPENCV_AVAILABLE,
                         qr_data=qr_data)

@main.route('/mark_attendance', methods=['POST'])
@login_required
def mark_attendance():
    try:
        data = request.get_json()
        user_id = data.get('user_id') if data else None
        
        if not user_id:
            user_id = current_user.id
        else:
            user_id = int(user_id)
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'success': False, 'message': 'User account is inactive'}), 400
        
        today = date.today()
        existing = Attendance.query.filter_by(user_id=user_id, date=today).first()
        if existing:
            return jsonify({'success': False, 'message': f'Attendance already marked for {user.name} today'}), 400
        
        now = datetime.now()
        attendance = Attendance(user_id=user_id, date=today, time=now.time(), status='present')
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Attendance marked successfully',
            'user': user.name,
            'time': now.strftime('%H:%M:%S')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/mark_manual_attendance')
@login_required
def mark_manual_attendance():
    try:
        today = date.today()
        existing = Attendance.query.filter_by(user_id=current_user.id, date=today).first()
        if existing:
            flash('Attendance already marked for today.', 'warning')
            return redirect(url_for('main.dashboard'))
        
        now = datetime.now()
        attendance = Attendance(
            user_id=current_user.id,
            date=today,
            time=now.time(),
            status='present'
        )
        db.session.add(attendance)
        db.session.commit()
        
        flash(f'✅ Attendance marked successfully at {now.strftime("%H:%M:%S")}', 'success')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error marking attendance: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

@main.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        title = request.form.get('title')
        if not title:
            flash('Task title is required.', 'danger')
            return redirect(url_for('main.tasks'))
        
        task = Task(
            user_id=current_user.id,
            title=title,
            description=request.form.get('description', ''),
            priority=request.form.get('priority', 'medium'),
            status='pending'
        )
        due_date = request.form.get('due_date')
        if due_date:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task added successfully!', 'success')
        return redirect(url_for('main.tasks'))
    
    return render_template('tasks.html',
        pending_tasks=Task.query.filter_by(user_id=current_user.id, status='pending').order_by(Task.created_at.desc()).all(),
        completed_tasks=Task.query.filter_by(user_id=current_user.id, status='completed').order_by(Task.completed_at.desc()).all()
    )

@main.route('/task/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.tasks'))
    
    task.status = 'completed'
    task.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash('Task completed!', 'success')
    return redirect(url_for('main.tasks'))

@main.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.tasks'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'success')
    return redirect(url_for('main.tasks'))

@main.route('/attendance_report')
@login_required
def attendance_report():
    if current_user.role == 'admin':
        attendances = Attendance.query.all()
    else:
        attendances = Attendance.query.filter_by(user_id=current_user.id).all()
    return render_template('attendance_report.html', attendances=attendances)

@main.route('/export_attendance')
@login_required
def export_attendance():
    if current_user.role == 'admin':
        attendances = Attendance.query.all()
    else:
        attendances = Attendance.query.filter_by(user_id=current_user.id).all()
    
    csv_buffer = generate_attendance_report(attendances)
    return send_file(csv_buffer, mimetype='text/csv', as_attachment=True, download_name=f'attendance_report_{datetime.now().strftime("%Y%m%d")}.csv')

# ==================== PWA ROUTES ====================
@main.route('/manifest.json')
def manifest():
    """Serve PWA manifest file"""
    try:
        return send_from_directory('static', 'manifest.json', mimetype='application/json')
    except Exception as e:
        print(f"Error serving manifest: {e}")
        return jsonify({'error': 'Manifest not found'}), 404

@main.route('/service-worker.js')
def service_worker():
    """Serve PWA service worker file"""
    try:
        return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')
    except Exception as e:
        print(f"Error serving service worker: {e}")
        return jsonify({'error': 'Service worker not found'}), 404

@main.route('/offline')
def offline():
    """Show offline page when user has no internet"""
    return render_template('offline.html')

@main.route('/offline-attendance', methods=['POST'])
@login_required
def offline_attendance():
    """Handle offline attendance marking"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') if data else None
        
        if not user_id:
            user_id = current_user.id
        else:
            user_id = int(user_id)
        
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Check if already marked today
        today = date.today()
        existing = Attendance.query.filter_by(user_id=user_id, date=today).first()
        if existing:
            return jsonify({'success': False, 'message': f'Attendance already marked for {user.name} today'}), 400
        
        # Mark attendance
        now = datetime.now()
        attendance = Attendance(
            user_id=user_id,
            date=today,
            time=now.time(),
            status='present'
        )
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Attendance marked successfully',
            'user': user.name,
            'time': now.strftime('%H:%M:%S')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ADMIN ROUTES ====================
@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    logged_in_users = User.query.filter_by(is_logged_in=True).all()
    
    return render_template('admin_dashboard.html',
        total_users=User.query.count(),
        total_attendance=Attendance.query.count(),
        total_tasks=Task.query.count(),
        pending_tasks=Task.query.filter_by(status='pending').count(),
        completed_tasks=Task.query.filter_by(status='completed').count(),
        recent_attendance=Attendance.query.order_by(Attendance.marked_at.desc()).limit(10).all(),
        users=User.query.all(),
        logged_in_users=logged_in_users
    )

@main.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    return render_template('admin_users.html', users=User.query.all())

@main.route('/admin/logged_in_users')
@login_required
def admin_logged_in_users():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    logged_in_users = User.query.filter_by(is_logged_in=True).all()
    return render_template('admin_logged_in_users.html', logged_in_users=logged_in_users)

@main.route('/admin/user/<int:user_id>/toggle')
@login_required
def toggle_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot toggle own account'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': user.is_active})