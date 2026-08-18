"""
Phase 5: Attendance Routes
API endpoints for attendance management
"""

from flask import Blueprint, request, jsonify
from utils.auth import token_required
from utils.validators import validate_request
from models.attendance import Attendance

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@attendance_bp.route('/mark', methods=['POST'])
@token_required
def mark_attendance(current_user):
    """Mark attendance for a student"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'student_id', 'class_id', 'attendance_date', 'status']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = Attendance.mark_attendance(
            school_id=data['school_id'],
            student_id=data['student_id'],
            class_id=data['class_id'],
            attendance_date=data['attendance_date'],
            status=data['status'],
            marked_by=current_user['id'],
            remarks=data.get('remarks')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/bulk-mark', methods=['POST'])
@token_required
def bulk_mark_attendance(current_user):
    """Bulk mark attendance"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'class_id', 'attendance_date', 'attendance_data']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = Attendance.bulk_mark_attendance(
            school_id=data['school_id'],
            class_id=data['class_id'],
            attendance_date=data['attendance_date'],
            attendance_data=data['attendance_data'],
            marked_by=current_user['id']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_attendance(current_user, student_id):
    """Get attendance for a student"""
    try:
        school_id = request.args.get('school_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not school_id:
            return jsonify({'error': 'school_id is required'}), 400
        
        result = Attendance.get_student_attendance(
            school_id=school_id,
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/class/<int:class_id>', methods=['GET'])
@token_required
def get_class_attendance(current_user, class_id):
    """Get attendance for a class"""
    try:
        school_id = request.args.get('school_id')
        attendance_date = request.args.get('attendance_date')
        
        if not school_id or not attendance_date:
            return jsonify({'error': 'school_id and attendance_date are required'}), 400
        
        result = Attendance.get_class_attendance(
            school_id=school_id,
            class_id=class_id,
            attendance_date=attendance_date
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/report/<int:student_id>', methods=['GET'])
@token_required
def get_attendance_report(current_user, student_id):
    """Get attendance report for a student"""
    try:
        school_id = request.args.get('school_id')
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not school_id or not month or not year:
            return jsonify({'error': 'school_id, month, and year are required'}), 400
        
        result = Attendance.get_attendance_report(
            school_id=school_id,
            student_id=student_id,
            month=month,
            year=year
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/analytics', methods=['GET'])
@token_required
def get_attendance_analytics(current_user):
    """Get attendance analytics"""
    try:
        school_id = request.args.get('school_id')
        class_id = request.args.get('class_id')
        
        if not school_id:
            return jsonify({'error': 'school_id is required'}), 400
        
        result = Attendance.get_attendance_analytics(
            school_id=school_id,
            class_id=class_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/summary/<int:student_id>', methods=['GET'])
@token_required
def get_monthly_summary(current_user, student_id):
    """Get monthly attendance summary"""
    try:
        school_id = request.args.get('school_id')
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not school_id or not month or not year:
            return jsonify({'error': 'school_id, month, and year are required'}), 400
        
        # Generate summary
        Attendance.generate_monthly_summary(school_id, month, year)
        
        # Fetch the summary
        result = Attendance.get_attendance_report(
            school_id=school_id,
            student_id=student_id,
            month=month,
            year=year
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500