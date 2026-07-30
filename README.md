# QR Attendance & Task Management System

A production-ready web application built with Python Flask for automated attendance tracking using QR codes and task management.

## Features

### Authentication & User Management
- User registration with password hashing
- Secure login with session management
- Role-based access control (Admin/User)
- Unique QR code generation for each user

### Attendance Management
- QR code-based attendance marking
- Webcam-based QR scanner integration
- Duplicate attendance prevention
- Date and time stamp for each attendance
- Real-time attendance tracking

### Task Management
- Add, view, complete, and delete tasks
- Task status tracking (Pending/Completed)
- Task prioritization (Low/Medium/High)
- Due date management

### Admin Dashboard
- User management (view/activate/deactivate)
- Attendance monitoring
- Task oversight
- Comprehensive statistics

### Reports & Analytics
- Attendance report generation
- CSV export functionality
- User-wise and date-wise filtering

## Technology Stack

### Backend
- Python 3.11+
- Flask 2.3.2
- SQLAlchemy ORM
- Flask-Login for authentication

### Frontend
- HTML5, CSS3
- Bootstrap 5
- JavaScript/jQuery
- Font Awesome Icons

### Database
- SQLite (development)
- Supports PostgreSQL/MySQL (production ready)

### Libraries
- OpenCV - QR code scanning
- Pyzbar - QR code decoding
- Qrcode - QR code generation
- Pandas - Report generation

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)
- Webcam (for QR scanning)

