import os
import base64
from io import BytesIO
from flask import current_app
import pandas as pd
import qrcode
from datetime import datetime

try:
    import cv2
    import numpy as np
    from pyzbar.pyzbar import decode
    OPENCV_AVAILABLE = True
except:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None
    decode = None

def generate_qr_code(user_id):
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(str(user_id))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f'{user_id}.png')
        img.save(qr_path)
        return True
    except Exception as e:
        print(f"QR Error: {e}")
        return False

def generate_attendance_report(attendances):
    """Generate attendance report as CSV with Excel-friendly date format"""
    data = []
    for att in attendances:
        data.append({
            'User ID': att.user_id,
            'User Name': att.user.name,
            'Email': att.user.email,
            'Date': att.date.strftime('%d-%b-%Y'),  # Excel-friendly: 30-Jul-2024
            'Time': att.time.strftime('%H:%M:%S'),
            'Status': att.status
        })
    
    df = pd.DataFrame(data)
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer

def get_qr_code_data(user_id):
    qr_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f'{user_id}.png')
    if os.path.exists(qr_path):
        with open(qr_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    return None