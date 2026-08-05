"""
Phase 5: Attendance Model
Attendance Management System with analytics
"""

from datetime import datetime, timedelta
from config import db

class Attendance:
    """Attendance model for database operations"""
    
    @staticmethod
    def mark_attendance(school_id, student_id, class_id, attendance_date, status, marked_by, remarks=None):
        """Mark attendance for a student"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            INSERT INTO attendance (
                school_id, student_id, class_id, attendance_date, status, 
                remarks, marked_by, marked_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                status = VALUES(status),
                remarks = VALUES(remarks),
                marked_by = VALUES(marked_by),
                marked_at = NOW()
            """
            
            values = (
                school_id, student_id, class_id, attendance_date, status, remarks, marked_by
            )
            
            cursor.execute(query, values)
            db.get_connection().commit()
            
            return {
                'success': True,
                'message': 'Attendance marked successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def bulk_mark_attendance(school_id, class_id, attendance_date, attendance_data, marked_by):
        """Bulk mark attendance for entire class"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            INSERT INTO attendance (
                school_id, student_id, class_id, attendance_date, status, 
                marked_by, marked_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                status = VALUES(status),
                marked_by = VALUES(marked_by),
                marked_at = NOW()
            """
            
            count = 0
            errors = []
            
            for record in attendance_data:
                try:
                    values = (
                        school_id,
                        record.get('student_id'),
                        class_id,
                        attendance_date,
                        record.get('status'),  # present, absent, late, leave, excused
                        marked_by
                    )
                    
                    cursor.execute(query, values)
                    count += 1
                except Exception as e:
                    errors.append({
                        'student_id': record.get('student_id'),
                        'error': str(e)
                    })
            
            db.get_connection().commit()
            
            return {
                'success': True,
                'marked': count,
                'failed': len(errors),
                'errors': errors,
                'message': f'Successfully marked attendance for {count} students'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_student_attendance(school_id, student_id, start_date=None, end_date=None):
        """Get attendance records for a student"""
        try:
            cursor = db.get_connection().cursor()
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).date()
            if not end_date:
                end_date = datetime.now().date()
            
            query = """
            SELECT * FROM attendance 
            WHERE school_id = %s AND student_id = %s 
            AND attendance_date BETWEEN %s AND %s
            ORDER BY attendance_date DESC
            """
            
            cursor.execute(query, (school_id, student_id, start_date, end_date))
            results = cursor.fetchall()
            
            return {
                'success': True,
                'records': [dict(row) for row in results],
                'start_date': str(start_date),
                'end_date': str(end_date)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_class_attendance(school_id, class_id, attendance_date):
        """Get attendance for entire class"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT a.*, s.first_name, s.last_name, s.roll_number 
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.school_id = %s AND a.class_id = %s AND a.attendance_date = %s
            ORDER BY s.roll_number ASC
            """
            
            cursor.execute(query, (school_id, class_id, attendance_date))
            results = cursor.fetchall()
            
            return {
                'success': True,
                'records': [dict(row) for row in results],
                'date': str(attendance_date),
                'total': len(results)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_attendance_report(school_id, student_id, month, year):
        """Get detailed attendance report for a month"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT 
                status,
                COUNT(*) as count
            FROM attendance
            WHERE school_id = %s AND student_id = %s 
            AND MONTH(attendance_date) = %s AND YEAR(attendance_date) = %s
            GROUP BY status
            """
            
            cursor.execute(query, (school_id, student_id, month, year))
            results = cursor.fetchall()
            
            summary = {}
            total_days = 0
            for row in results:
                summary[row['status']] = row['count']
                total_days += row['count']
            
            present_days = summary.get('present', 0)
            percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            return {
                'success': True,
                'student_id': student_id,
                'month': month,
                'year': year,
                'summary': summary,
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': summary.get('absent', 0),
                'late_days': summary.get('late', 0),
                'leave_days': summary.get('leave', 0),
                'percentage': round(percentage, 2),
                'status': 'good' if percentage >= 75 else 'satisfactory' if percentage >= 60 else 'poor'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def generate_monthly_summary(school_id, month, year):
        """Generate monthly attendance summary for all students"""
        try:
            cursor = db.get_connection().cursor()
            
            # Get all students
            student_query = """
            SELECT id, class_id FROM students 
            WHERE school_id = %s AND status = 'active'
            """
            
            cursor.execute(student_query, (school_id,))
            students = cursor.fetchall()
            
            summary_query = """
            SELECT 
                COUNT(*) as total_days,
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_days,
                SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent_days,
                SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as late_days,
                SUM(CASE WHEN status = 'leave' THEN 1 ELSE 0 END) as leave_days
            FROM attendance
            WHERE school_id = %s AND student_id = %s 
            AND MONTH(attendance_date) = %s AND YEAR(attendance_date) = %s
            """
            
            insert_query = """
            INSERT INTO monthly_attendance_summary (
                school_id, student_id, class_id, month, year,
                total_days, present_days, absent_days, late_days, leave_days,
                percentage, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                total_days = VALUES(total_days),
                present_days = VALUES(present_days),
                absent_days = VALUES(absent_days),
                late_days = VALUES(late_days),
                leave_days = VALUES(leave_days),
                percentage = VALUES(percentage),
                status = VALUES(status),
                generated_at = CURRENT_TIMESTAMP
            """
            
            count = 0
            for student in students:
                student_id = student['id']
                class_id = student['class_id']
                
                cursor.execute(summary_query, (school_id, student_id, month, year))
                result = cursor.fetchone()
                
                if result and result['total_days']:
                    total_days = result['total_days']
                    present_days = result['present_days'] or 0
                    percentage = (present_days / total_days * 100)
                    status = 'good' if percentage >= 75 else 'satisfactory' if percentage >= 60 else 'poor'
                    
                    cursor.execute(insert_query, (
                        school_id, student_id, class_id, month, year,
                        total_days, present_days, result['absent_days'], 
                        result['late_days'], result['leave_days'],
                        round(percentage, 2), status
                    ))
                    count += 1
            
            db.get_connection().commit()
            
            return {
                'success': True,
                'message': f'Generated summary for {count} students',
                'students_processed': count
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_attendance_analytics(school_id, class_id=None):
        """Get attendance analytics for school or class"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT 
                status,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM attendance 
                    WHERE school_id = %s """ + ("AND class_id = %s" if class_id else "") + """), 2) as percentage
            FROM attendance
            WHERE school_id = %s """ + ("AND class_id = %s" if class_id else "") + """
            AND attendance_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY status
            """
            
            params = [school_id, school_id]
            if class_id:
                params.insert(1, class_id)
                params.append(class_id)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            analytics = {}
            for row in results:
                analytics[row['status']] = {
                    'count': row['count'],
                    'percentage': row['percentage']
                }
            
            return {
                'success': True,
                'analytics': analytics,
                'period': 'Last 30 days'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
