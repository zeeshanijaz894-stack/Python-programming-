"""
Phase 5: Leave Model
Student Leave Management System
"""

from datetime import datetime
from config import db

class Leave:
    """Leave model for database operations"""
    
    @staticmethod
    def apply_leave(school_id, student_id, leave_type, start_date, end_date, reason, documents=None):
        """Apply for leave"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            INSERT INTO leaves (
                school_id, student_id, leave_type, start_date, end_date,
                reason, status, documents, applied_at
            ) VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s, NOW())
            """
            
            values = (
                school_id, student_id, leave_type, start_date, end_date,
                reason, documents
            )
            
            cursor.execute(query, values)
            db.get_connection().commit()
            leave_id = cursor.lastrowid
            
            return {
                'success': True,
                'leave_id': leave_id,
                'message': 'Leave application submitted successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_student_leaves(school_id, student_id, status=None):
        """Get all leave applications for a student"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT * FROM leaves
            WHERE school_id = %s AND student_id = %s
            """
            
            params = [school_id, student_id]
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY applied_at DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return {
                'success': True,
                'leaves': [dict(row) for row in results],
                'total': len(results)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def approve_leave(leave_id, approved_by, remarks=None):
        """Approve a leave application"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            UPDATE leaves
            SET status = 'approved', approved_by = %s, remarks = %s, approved_at = NOW()
            WHERE id = %s
            """
            
            cursor.execute(query, (approved_by, remarks, leave_id))
            db.get_connection().commit()
            
            return {
                'success': True,
                'message': 'Leave approved successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def reject_leave(leave_id, rejected_by, reason):
        """Reject a leave application"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            UPDATE leaves
            SET status = 'rejected', rejected_by = %s, rejection_reason = %s, rejected_at = NOW()
            WHERE id = %s
            """
            
            cursor.execute(query, (rejected_by, reason, leave_id))
            db.get_connection().commit()
            
            return {
                'success': True,
                'message': 'Leave rejected successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_pending_leaves(school_id, class_id=None):
        """Get all pending leave applications"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT l.*, s.first_name, s.last_name, s.roll_number, c.name as class_name
            FROM leaves l
            JOIN students s ON l.student_id = s.id
            JOIN classes c ON s.class_id = c.id
            WHERE l.school_id = %s AND l.status = 'pending'
            """
            
            params = [school_id]
            
            if class_id:
                query += " AND s.class_id = %s"
                params.append(class_id)
            
            query += " ORDER BY l.applied_at ASC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return {
                'success': True,
                'pending_leaves': [dict(row) for row in results],
                'total': len(results)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_leave_balance(school_id, student_id):
        """Get leave balance for a student"""
        try:
            cursor = db.get_connection().cursor()
            
            # Get approved leaves count
            query = """
            SELECT leave_type, COUNT(*) as count
            FROM leaves
            WHERE school_id = %s AND student_id = %s AND status = 'approved'
            AND YEAR(start_date) = YEAR(CURDATE())
            GROUP BY leave_type
            """
            
            cursor.execute(query, (school_id, student_id))
            results = cursor.fetchall()
            
            leave_usage = {}
            for row in results:
                leave_usage[row['leave_type']] = row['count']
            
            # Get leave policy
            policy_query = """
            SELECT leave_type, max_days FROM leave_policies
            WHERE school_id = %s
            """
            
            cursor.execute(policy_query, (school_id,))
            policies = cursor.fetchall()
            
            balance = {}
            for policy in policies:
                leave_type = policy['leave_type']
                max_days = policy['max_days']
                used = leave_usage.get(leave_type, 0)
                balance[leave_type] = {
                    'max_days': max_days,
                    'used': used,
                    'remaining': max_days - used
                }
            
            return {
                'success': True,
                'leave_balance': balance,
                'year': datetime.now().year
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_leave_statistics(school_id, month=None, year=None):
        """Get leave statistics"""
        try:
            cursor = db.get_connection().cursor()
            
            if not month:
                month = datetime.now().month
            if not year:
                year = datetime.now().year
            
            query = """
            SELECT 
                leave_type,
                status,
                COUNT(*) as count
            FROM leaves
            WHERE school_id = %s 
            AND MONTH(start_date) = %s AND YEAR(start_date) = %s
            GROUP BY leave_type, status
            """
            
            cursor.execute(query, (school_id, month, year))
            results = cursor.fetchall()
            
            statistics = {}
            for row in results:
                leave_type = row['leave_type']
                if leave_type not in statistics:
                    statistics[leave_type] = {}
                statistics[leave_type][row['status']] = row['count']
            
            return {
                'success': True,
                'statistics': statistics,
                'month': month,
                'year': year
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def create_leave_policy(school_id, leave_type, max_days, description=None):
        """Create leave policy"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            INSERT INTO leave_policies (
                school_id, leave_type, max_days, description
            ) VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                max_days = VALUES(max_days),
                description = VALUES(description)
            """
            
            cursor.execute(query, (school_id, leave_type, max_days, description))
            db.get_connection().commit()
            
            return {
                'success': True,
                'message': 'Leave policy created successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()

    @staticmethod
    def get_leave_policies(school_id):
        """Get all leave policies for school"""
        try:
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT * FROM leave_policies
            WHERE school_id = %s
            ORDER BY leave_type ASC
            """
            
            cursor.execute(query, (school_id,))
            results = cursor.fetchall()
            
            return {
                'success': True,
                'policies': [dict(row) for row in results],
                'total': len(results)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()