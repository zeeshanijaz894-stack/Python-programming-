"""
Phase 5: Student Model
Student Management System with enhanced details
"""

from datetime import datetime
from config import db

class Student:
    """Student model for database operations"""
    
    @staticmethod
    def create_student(school_id, data):
        """Create new student"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            INSERT INTO students (
                school_id, class_id, roll_number, first_name, last_name,
                admission_number, enrollment_date, date_of_birth, gender,
                address, phone_number, email, father_name, mother_name,
                guardian_phone, blood_group, medical_conditions, status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            values = (
                school_id,
                data.get('class_id'),
                data.get('roll_number'),
                data.get('first_name'),
                data.get('last_name'),
                data.get('admission_number'),
                data.get('enrollment_date', datetime.now().date()),
                data.get('date_of_birth'),
                data.get('gender'),
                data.get('address'),
                data.get('phone_number'),
                data.get('email'),
                data.get('father_name'),
                data.get('mother_name'),
                data.get('guardian_phone'),
                data.get('blood_group'),
                data.get('medical_conditions'),
                'active'
            )
            
            cursor.execute(query, values)
            db.get_connection().commit()
            
            return {
                'success': True,
                'student_id': cursor.lastrowid,
                'message': 'Student created successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_student(student_id, school_id):
        """Get student details"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT * FROM students 
            WHERE id = %s AND school_id = %s
            """
            
            cursor.execute(query, (student_id, school_id))
            result = cursor.fetchone()
            
            if result:
                return {
                    'success': True,
                    'student': dict(result)
                }
            return {'success': False, 'error': 'Student not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_all_students(school_id, class_id=None, status='active', page=1, limit=50):
        """Get all students with filters"""
        try:
            cursor = db.get_connection().cursor()
            offset = (page - 1) * limit
            
            query = "SELECT * FROM students WHERE school_id = %s AND status = %s"
            params = [school_id, status]
            
            if class_id:
                query += " AND class_id = %s"
                params.append(class_id)
            
            query += " ORDER BY first_name ASC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Get total count
            count_query = "SELECT COUNT(*) as count FROM students WHERE school_id = %s AND status = %s"
            count_params = [school_id, status]
            if class_id:
                count_query += " AND class_id = %s"
                count_params.append(class_id)
            
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()['count']
            
            return {
                'success': True,
                'students': [dict(row) for row in results],
                'total': total,
                'page': page,
                'limit': limit,
                'pages': (total + limit - 1) // limit
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def update_student(student_id, school_id, data):
        """Update student information"""
        try:
            cursor = db.get_connection().cursor()
            
            # Build dynamic update query
            allowed_fields = [
                'class_id', 'roll_number', 'first_name', 'last_name',
                'date_of_birth', 'gender', 'address', 'phone_number',
                'email', 'father_name', 'mother_name', 'guardian_phone',
                'blood_group', 'medical_conditions', 'status'
            ]
            
            update_fields = []
            values = []
            
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    values.append(data[field])
            
            if not update_fields:
                return {'success': False, 'error': 'No fields to update'}
            
            values.extend([student_id, school_id])
            
            query = f"""
            UPDATE students SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND school_id = %s
            """
            
            cursor.execute(query, values)
            db.get_connection().commit()
            
            return {
                'success': True,
                'message': 'Student updated successfully',
                'affected_rows': cursor.rowcount
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def delete_student(student_id, school_id):
        """Soft delete student (change status to inactive)"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            UPDATE students SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND school_id = %s
            """
            
            cursor.execute(query, (student_id, school_id))
            db.get_connection().commit()
            
            return {
                'success': True,
                'message': 'Student deactivated successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def search_students(school_id, search_term):
        """Search students by name, email, or admission number"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT * FROM students 
            WHERE school_id = %s AND (
                first_name LIKE %s OR 
                last_name LIKE %s OR 
                email LIKE %s OR 
                admission_number LIKE %s
            ) AND status = 'active'
            LIMIT 20
            """
            
            search_param = f"%{search_term}%"
            cursor.execute(query, (school_id, search_param, search_param, search_param, search_param))
            results = cursor.fetchall()
            
            return {
                'success': True,
                'students': [dict(row) for row in results]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def bulk_import_students(school_id, students_data):
        """Bulk import students from CSV or JSON"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            INSERT INTO students (
                school_id, class_id, roll_number, first_name, last_name,
                admission_number, enrollment_date, date_of_birth, gender,
                address, phone_number, email, father_name, mother_name,
                guardian_phone, blood_group, medical_conditions, status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active'
            )
            """
            
            count = 0
            errors = []
            
            for student_data in students_data:
                try:
                    values = (
                        school_id,
                        student_data.get('class_id'),
                        student_data.get('roll_number'),
                        student_data.get('first_name'),
                        student_data.get('last_name'),
                        student_data.get('admission_number'),
                        student_data.get('enrollment_date', datetime.now().date()),
                        student_data.get('date_of_birth'),
                        student_data.get('gender'),
                        student_data.get('address'),
                        student_data.get('phone_number'),
                        student_data.get('email'),
                        student_data.get('father_name'),
                        student_data.get('mother_name'),
                        student_data.get('guardian_phone'),
                        student_data.get('blood_group'),
                        student_data.get('medical_conditions')
                    )
                    
                    cursor.execute(query, values)
                    count += 1
                except Exception as e:
                    errors.append({
                        'row': student_data,
                        'error': str(e)
                    })
            
            db.get_connection().commit()
            
            return {
                'success': True,
                'imported': count,
                'failed': len(errors),
                'errors': errors,
                'message': f'Successfully imported {count} students'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
