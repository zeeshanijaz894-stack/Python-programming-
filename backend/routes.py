from flask import Blueprint, request, jsonify, session
from models import School, User
import logging

logger = logging.getLogger(__name__)

# Create blueprint
school_bp = Blueprint('school', __name__, url_prefix='/api/school')

# Create school endpoint
@school_bp.route('/create', methods=['POST'])
def create_school():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['school_name', 'school_code', 'admin_email', 'admin_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        result = School.create_school(data)
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error in create_school: {e}")
        return jsonify({'error': str(e)}), 500

# Get school endpoint
@school_bp.route('/<int:school_id>', methods=['GET'])
def get_school(school_id):
    try:
        school = School.get_school(school_id)
        if school:
            return jsonify({
                'success': True,
                'data': school
            }), 200
        else:
            return jsonify({'error': 'School not found'}), 404
    except Exception as e:
        logger.error(f"Error in get_school: {e}")
        return jsonify({'error': str(e)}), 500

# Update school endpoint
@school_bp.route('/<int:school_id>', methods=['PUT'])
def update_school(school_id):
    try:
        data = request.get_json()
        
        # Allowed fields to update
        allowed_fields = ['school_name', 'phone', 'address', 'city', 'state', 'postal_code', 'website']
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        result = School.update_school(school_id, updates)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Error in update_school: {e}")
        return jsonify({'error': str(e)}), 500

# User routes
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# Create user endpoint
@user_bp.route('/create', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['school_id', 'username', 'email', 'password', 'full_name', 'user_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        result = User.create_user(data)
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error in create_user: {e}")
        return jsonify({'error': str(e)}), 500

# Get user endpoint
@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        school_id = session.get('school_id')
        if not school_id:
            return jsonify({'error': 'School ID not found in session'}), 401
        
        user = User.get_user(user_id, school_id)
        if user:
            return jsonify({
                'success': True,
                'data': user
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error in get_user: {e}")
        return jsonify({'error': str(e)}), 500
