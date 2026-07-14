import mysql.connector
from mysql.connector import Error
from datetime import datetime
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class School:
    @staticmethod
    def create_school(school_data):
        """Create a new school account"""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME']
            )
            cursor = connection.cursor()
            
            query = """
            INSERT INTO schools 
            (school_name, school_code, admin_email, admin_password, phone, address, city, state, postal_code, website)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                school_data.get('school_name'),
                school_data.get('school_code'),
                school_data.get('admin_email'),
                school_data.get('admin_password'),
                school_data.get('phone'),
                school_data.get('address'),
                school_data.get('city'),
                school_data.get('state'),
                school_data.get('postal_code'),
                school_data.get('website')
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            return {
                'success': True,
                'school_id': cursor.lastrowid,
                'message': 'School created successfully'
            }
        except Error as err:
            logger.error(f"Error creating school: {err}")
            return {
                'success': False,
                'error': str(err)
            }
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_school(school_id):
        """Get school details"""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME']
            )
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM schools WHERE id = %s AND is_active = TRUE"
            cursor.execute(query, (school_id,))
            
            school = cursor.fetchone()
            return school
        except Error as err:
            logger.error(f"Error fetching school: {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def update_school(school_id, updates):
        """Update school information"""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME']
            )
            cursor = connection.cursor()
            
            set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
            query = f"UPDATE schools SET {set_clause} WHERE id = %s"
            
            values = list(updates.values()) + [school_id]
            cursor.execute(query, values)
            connection.commit()
            
            return {
                'success': True,
                'message': 'School updated successfully'
            }
        except Error as err:
            logger.error(f"Error updating school: {err}")
            return {
                'success': False,
                'error': str(err)
            }
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class User:
    @staticmethod
    def create_user(user_data):
        """Create a new user"""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME']
            )
            cursor = connection.cursor()
            
            query = """
            INSERT INTO users 
            (school_id, username, email, password, full_name, user_type, phone, date_of_birth, gender, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                user_data.get('school_id'),
                user_data.get('username'),
                user_data.get('email'),
                user_data.get('password'),
                user_data.get('full_name'),
                user_data.get('user_type'),
                user_data.get('phone'),
                user_data.get('date_of_birth'),
                user_data.get('gender'),
                user_data.get('address')
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            return {
                'success': True,
                'user_id': cursor.lastrowid,
                'message': 'User created successfully'
            }
        except Error as err:
            logger.error(f"Error creating user: {err}")
            return {
                'success': False,
                'error': str(err)
            }
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_user(user_id, school_id):
        """Get user details"""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME']
            )
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM users WHERE id = %s AND school_id = %s AND is_active = TRUE"
            cursor.execute(query, (user_id, school_id))
            
            user = cursor.fetchone()
            return user
        except Error as err:
            logger.error(f"Error fetching user: {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
