"""
Phase 5: Leave Routes
API endpoints for leave management
"""

from flask import Blueprint, request, jsonify
from utils.auth import token_required
from utils.validators import validate_request
from models.leave import Leave

leave_bp = Blueprint('leave', __name__, url_prefix='/api/leave')

@leave_bp.route('/apply', methods=['POST'])
@token_required
def apply_leave(current_user):
    """Apply for leave"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'student_id', 'leave_type', 'start_date', 'end_date', 'reason']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = Leave.apply_leave(
            school_id=data['school_id'],
            student_id=data['student_id'],
            leave_type=data['leave_type'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            reason=data['reason'],
            documents=data.get('documents')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_leaves(current_user, student_id):
    """Get leaves for a student"""
    try:
        school_id = request.args.get('school_id')
        status = request.args.get('status')
        
        if not school_id:
            return jsonify({'error': 'school_id is required'}), 400
        
        result = Leave.get_student_leaves(
            school_id=school_id,
            student_id=student_id,
            status=status
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/approve/<int:leave_id>', methods=['PUT'])
@token_required
def approve_leave(current_user, leave_id):
    """Approve a leave"""
    try:
        data = request.get_json()
        
        result = Leave.approve_leave(
            leave_id=leave_id,
            approved_by=current_user['id'],
            remarks=data.get('remarks')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/reject/<int:leave_id>', methods=['PUT'])
@token_required
def reject_leave(current_user, leave_id):
    """Reject a leave"""
    try:
        data = request.get_json()
        
        if 'reason' not in data:
            return jsonify({'error': 'reason is required'}), 400
        
        result = Leave.reject_leave(
            leave_id=leave_id,
            rejected_by=current_user['id'],
            reason=data['reason']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/pending', methods=['GET'])
@token_required
def get_pending_leaves(current_user):
    """Get pending leaves"""
    try:
        school_id = request.args.get('school_id')
        class_id = request.args.get('class_id')
        
        if not school_id:
            return jsonify({'error': 'school_id is required'}), 400
        
        result = Leave.get_pending_leaves(
            school_id=school_id,
            class_id=class_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/balance/<int:student_id>', methods=['GET'])
@token_required
def get_leave_balance(current_user, student_id):
    """Get leave balance"""
    try:
        school_id = request.args.get('school_id')
        
        if not school_id:
            return jsonify({'error': 'school_id is required'}), 400
        
        result = Leave.get_leave_balance(
            school_id=school_id,
            student_id=student_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/statistics', methods=['GET'])
@token_required
def get_leave_statistics(current_user):
    """Get leave statistics"""
    try:
        school_id = request.args.get('school_id')
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not school_id:
            return jsonify({'error': 'school_id is required'}), 400
        
        result = Leave.get_leave_statistics(
            school_id=school_id,
            month=month,
            year=year
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/policy', methods=['POST'])
@token_required
def create_leave_policy(current_user):
    """Create leave policy"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'leave_type', 'max_days']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = Leave.create_leave_policy(
            school_id=data['school_id'],
            leave_type=data['leave_type'],
            max_days=data['max_days'],
            description=data.get('description')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/policies', methods=['GET'])
@token_required
def get_leave_policies(current_user):
    """Get leave policies"""
    try:
        school_id = request.args.get('school_id')
        
        if not school_id:
            return jsonify({'error': 'school_id is required'}), 400
        
        result = Leave.get_leave_policies(school_id=school_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500