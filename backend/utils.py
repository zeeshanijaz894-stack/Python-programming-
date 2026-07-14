import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class PasswordUtil:
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        try:
            salt, pwd_hash = password_hash.split('$')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return new_hash.hex() == pwd_hash
        except:
            return False

class JWTUtil:
    @staticmethod
    def generate_token(user_id, school_id, user_type):
        """Generate JWT token"""
        try:
            payload = {
                'user_id': user_id,
                'school_id': school_id,
                'user_type': user_type,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(
                payload,
                current_app.config['JWT_SECRET'],
                algorithm=current_app.config['JWT_ALGORITHM']
            )
            return token
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            return None
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET'],
                algorithms=[current_app.config['JWT_ALGORITHM']]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}

class ValidationUtil:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        import re
        pattern = r'^[0-9]{10,15}$'
        return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain digit"
        return True, "Password is strong"

class ReportUtil:
    @staticmethod
    def generate_result_card(student_data, results_data, template):
        """Generate result card from template"""
        # This will be implemented with ReportLab for PDF generation
        pass
    
    @staticmethod
    def generate_fee_voucher(student_data, fee_data, template):
        """Generate fee voucher from template"""
        # This will be implemented with ReportLab for PDF generation
        pass
