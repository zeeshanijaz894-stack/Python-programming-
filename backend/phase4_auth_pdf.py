# Phase 4: Advanced Features - PDF Generation, Templates & Authentication

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from functools import wraps
import jwt
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import json
from config import Config
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# ==================== Authentication ====================

def token_required(f):
    """Decorator to check JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
            request.user_id = payload['user_id']
            request.school_id = payload['school_id']
            request.user_type = payload['user_type']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# ==================== Authentication Routes ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        school_code = data.get('school_code')
        
        if not email or not password or not school_code:
            return jsonify({'error': 'Email, password, and school code required'}), 400
        
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = connection.cursor(dictionary=True)
        
        # Get school
        query = "SELECT id FROM schools WHERE school_code = %s AND is_active = TRUE"
        cursor.execute(query, (school_code,))
        school = cursor.fetchone()
        
        if not school:
            return jsonify({'error': 'Invalid school code'}), 401
        
        # Get user
        query = "SELECT * FROM users WHERE school_id = %s AND email = %s AND is_active = TRUE"
        cursor.execute(query, (school['id'], email))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password (in production, use proper hashing)
        if user['password'] != password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        payload = {
            'user_id': user['id'],
            'school_id': user['school_id'],
            'user_type': user['user_type'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'user_type': user['user_type']
            }
        }), 200
        
    except Error as err:
        logger.error(f"Database error: {err}")
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/auth/register-school', methods=['POST'])
def register_school():
    """Register new school"""
    try:
        data = request.get_json()
        
        required_fields = ['school_name', 'school_code', 'admin_email', 'admin_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = connection.cursor()
        
        try:
            # Create school
            school_query = """
            INSERT INTO schools (school_name, school_code, admin_email, admin_password, is_active, subscription_plan, subscription_expires)
            VALUES (%s, %s, %s, %s, TRUE, 'basic', DATE_ADD(NOW(), INTERVAL 30 DAY))
            """
            
            cursor.execute(school_query, (
                data['school_name'],
                data['school_code'],
                data['admin_email'],
                data['admin_password']  # In production, hash this!
            ))
            
            school_id = cursor.lastrowid
            connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'School registered successfully',
                'school_id': school_id
            }), 201
            
        except mysql.connector.Error as err:
            connection.rollback()
            if err.errno == 1062:  # Duplicate entry
                return jsonify({'error': 'School code or email already exists'}), 400
            raise
        finally:
            cursor.close()
            connection.close()
            
    except Error as err:
        logger.error(f"Registration error: {err}")
        return jsonify({'error': 'Registration failed'}), 500

# ==================== PDF Generation for Result Card ====================

def generate_result_card_pdf(student_data, results_data, template_data=None):
    """Generate result card PDF"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('0B5345'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('1B6E54'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # Header
        story.append(Paragraph("RESULT CARD", title_style))
        story.append(Spacer(1, 0.1*inch))
        
        # School Info
        if template_data and template_data.get('header_text'):
            story.append(Paragraph(template_data['header_text'], styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Student Info
        student_info = [
            ['Student Name:', student_data.get('name', 'N/A')],
            ['Roll Number:', student_data.get('roll_number', 'N/A')],
            ['Class:', student_data.get('class', 'N/A')],
            ['Academic Year:', student_data.get('academic_year', 'N/A')]
        ]
        
        student_table = Table(student_info, colWidths=[2*inch, 2*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('E8F5E9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('1B6E54'))
        ]))
        
        story.append(student_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Results Table
        story.append(Paragraph("Results", heading_style))
        
        result_data = [['Subject', 'Marks Obtained', 'Total Marks', 'Percentage', 'Grade']]
        
        for result in results_data:
            percentage = (result['marks_obtained'] / result['total_marks'] * 100) if result['total_marks'] > 0 else 0
            result_data.append([
                result.get('subject', 'N/A'),
                str(result.get('marks_obtained', 'N/A')),
                str(result.get('total_marks', 'N/A')),
                f"{percentage:.1f}%",
                result.get('grade', 'N/A')
            ])
        
        results_table = Table(result_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1*inch, 0.8*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('0B5345')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('E8F5E9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('1B6E54')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('E8F5E9')])
        ]))
        
        story.append(results_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        if template_data and template_data.get('footer_text'):
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            story.append(Paragraph(template_data['footer_text'], footer_style))
        
        # Generate PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        logger.error(f"Error generating result card: {e}")
        return None

# ==================== PDF Generation for Fee Voucher ====================

def generate_fee_voucher_pdf(student_data, fee_data, template_data=None):
    """Generate fee voucher PDF"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('0B5345'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Header
        story.append(Paragraph("FEE VOUCHER", title_style))
        story.append(Spacer(1, 0.1*inch))
        
        # School Info from template
        if template_data and template_data.get('header_text'):
            story.append(Paragraph(template_data['header_text'], styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Voucher Details
        voucher_info = [
            ['Voucher No:', fee_data.get('id', 'N/A'), 'Date:', datetime.now().strftime('%Y-%m-%d')],
            ['Student Name:', student_data.get('name', 'N/A'), 'Roll No:', student_data.get('roll_number', 'N/A')],
            ['Class:', student_data.get('class', 'N/A'), 'Academic Year:', fee_data.get('academic_year', 'N/A')]
        ]
        
        voucher_table = Table(voucher_info, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        voucher_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(voucher_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Fee Details
        fee_details = [
            ['Fee Type', 'Amount', 'Due Date', 'Status'],
            [fee_data.get('fee_type', 'N/A'), 
             f"Rs. {fee_data.get('amount', 0)}",
             str(fee_data.get('due_date', 'N/A')),
             fee_data.get('status', 'N/A')]
        ]
        
        fee_table = Table(fee_details, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        fee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('0B5345')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('1B6E54')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('E8F5E9'))
        ]))
        
        story.append(fee_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Amount Summary
        amount_due = fee_data.get('amount', 0) - fee_data.get('paid_amount', 0)
        summary = [
            ['Total Amount:', f"Rs. {fee_data.get('amount', 0)}"],
            ['Amount Paid:', f"Rs. {fee_data.get('paid_amount', 0)}"],
            ['Amount Due:', f"Rs. {amount_due}"]
        ]
        
        summary_table = Table(summary, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('E8F5E9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('6FCF97'))
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Footer
        if template_data and template_data.get('footer_text'):
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER
            )
            story.append(Paragraph(template_data['footer_text'], footer_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        logger.error(f"Error generating fee voucher: {e}")
        return None

# ==================== API Endpoints for PDF Generation ====================

@app.route('/api/generate-result-card/<int:student_id>', methods=['GET'])
@token_required
def generate_result_card(student_id):
    """Generate and download result card PDF"""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = connection.cursor(dictionary=True)
        
        # Get student info
        query = """
        SELECT s.*, u.full_name as name, c.class_name as class
        FROM students s
        JOIN users u ON s.user_id = u.id
        JOIN classes c ON s.class_id = c.id
        WHERE s.id = %s AND s.school_id = %s
        """
        cursor.execute(query, (student_id, request.school_id))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get results
        query = """
        SELECT sub.subject_name as subject, r.marks_obtained, r.total_marks, r.grade
        FROM results r
        JOIN subjects sub ON r.subject_id = sub.id
        WHERE r.student_id = %s AND r.school_id = %s
        ORDER BY sub.subject_name
        """
        cursor.execute(query, (student_id, request.school_id))
        results = cursor.fetchall()
        
        # Get template
        query = "SELECT * FROM result_card_templates WHERE school_id = %s LIMIT 1"
        cursor.execute(query, (request.school_id,))
        template = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # Generate PDF
        pdf_buffer = generate_result_card_pdf(student, results, template)
        
        if pdf_buffer:
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"ResultCard_{student['roll_number']}.pdf"
            )
        else:
            return jsonify({'error': 'PDF generation failed'}), 500
            
    except Error as err:
        logger.error(f"Error: {err}")
        return jsonify({'error': 'Error generating PDF'}), 500

@app.route('/api/generate-fee-voucher/<int:fee_id>', methods=['GET'])
@token_required
def generate_fee_voucher(fee_id):
    """Generate and download fee voucher PDF"""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = connection.cursor(dictionary=True)
        
        # Get fee info
        query = """
        SELECT sf.*, s.roll_number, u.full_name as name, c.class_name as class, fs.fee_type
        FROM student_fees sf
        JOIN students s ON sf.student_id = s.id
        JOIN users u ON s.user_id = u.id
        JOIN classes c ON s.class_id = c.id
        JOIN fee_structure fs ON sf.fee_structure_id = fs.id
        WHERE sf.id = %s AND sf.school_id = %s
        """
        cursor.execute(query, (fee_id, request.school_id))
        fee = cursor.fetchone()
        
        if not fee:
            return jsonify({'error': 'Fee record not found'}), 404
        
        # Get template
        query = "SELECT * FROM fee_voucher_templates WHERE school_id = %s LIMIT 1"
        cursor.execute(query, (request.school_id,))
        template = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # Generate PDF
        pdf_buffer = generate_fee_voucher_pdf(fee, fee, template)
        
        if pdf_buffer:
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"FeeVoucher_{fee['roll_number']}.pdf"
            )
        else:
            return jsonify({'error': 'PDF generation failed'}), 500
            
    except Error as err:
        logger.error(f"Error: {err}")
        return jsonify({'error': 'Error generating PDF'}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)