"""
Phase 5: Attendance and Leave Service Functions
Business logic and utilities
"""

from datetime import datetime, timedelta
from models.attendance import Attendance
from models.leave import Leave

class AttendanceService:
    """Service class for attendance operations"""
    
    @staticmethod
    def mark_bulk_attendance_with_validation(school_id, class_id, attendance_date, records):
        """Mark bulk attendance with validation"""
        validated_records = []
        errors = []
        
        for record in records:
            # Validate status
            valid_statuses = ['present', 'absent', 'late', 'leave', 'excused']
            if record.get('status') not in valid_statuses:
                errors.append({
                    'student_id': record.get('student_id'),
                    'error': f"Invalid status: {record.get('status')}"
                })
                continue
            
            validated_records.append(record)
        
        if validated_records:
            result = Attendance.bulk_mark_attendance(
                school_id=school_id,
                class_id=class_id,
                attendance_date=attendance_date,
                attendance_data=validated_records,
                marked_by=None
            )
            result['validation_errors'] = errors
            return result
        else:
            return {
                'success': False,
                'message': 'No valid records to mark',
                'errors': errors
            }
    
    @staticmethod
    def get_attendance_percentage(school_id, student_id, days=30):
        """Calculate attendance percentage"""
        result = Attendance.get_student_attendance(
            school_id=school_id,
            student_id=student_id
        )
        
        if not result['success']:
            return result
        
        records = result['records']
        if not records:
            return {'percentage': 0, 'total_days': 0}
        
        present_days = sum(1 for r in records if r['status'] == 'present')
        total_days = len(records)
        
        percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        return {
            'percentage': round(percentage, 2),
            'present_days': present_days,
            'total_days': total_days,
            'status': 'good' if percentage >= 75 else 'satisfactory' if percentage >= 60 else 'poor'
        }
    
    @staticmethod
    def generate_attendance_report(school_id, start_date, end_date):
        """Generate comprehensive attendance report"""
        try:
            from config import db
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT 
                c.id as class_id,
                c.name as class_name,
                s.id as student_id,
                s.first_name,
                s.last_name,
                COUNT(*) as total_days,
                SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) as absent,
                SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END) as late,
                ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100 / COUNT(*), 2) as percentage
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            JOIN classes c ON a.class_id = c.id
            WHERE a.school_id = %s AND a.attendance_date BETWEEN %s AND %s
            GROUP BY c.id, s.id
            ORDER BY c.name, s.roll_number
            """
            
            cursor.execute(query, (school_id, start_date, end_date))
            results = cursor.fetchall()
            
            return {
                'success': True,
                'report': [dict(row) for row in results],
                'period': f"{start_date} to {end_date}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class LeaveService:
    """Service class for leave operations"""
    
    @staticmethod
    def validate_leave_application(school_id, student_id, leave_type, start_date, end_date):
        """Validate leave application"""
        errors = []
        
        # Check leave balance
        balance_result = Leave.get_leave_balance(school_id, student_id)
        if balance_result['success']:
            balance = balance_result['leave_balance'].get(leave_type)
            if balance and balance['remaining'] <= 0:
                errors.append(f"No remaining {leave_type} leave days")
        
        # Check dates
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start > end:
                errors.append("Start date cannot be after end date")
            
            if start < datetime.now().date():
                errors.append("Cannot apply for past dates")
            
            days_requested = (end - start).days + 1
            balance = balance_result['leave_balance'].get(leave_type)
            if balance and days_requested > balance['remaining']:
                errors.append(f"Requested {days_requested} days but only {balance['remaining']} days available")
        except ValueError:
            errors.append("Invalid date format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def get_leave_summary(school_id, month, year):
        """Get leave summary for month"""
        return Leave.get_leave_statistics(school_id, month, year)
    
    @staticmethod
    def check_overlapping_leave(student_id, start_date, end_date, exclude_leave_id=None):
        """Check if leave overlaps with existing leaves"""
        try:
            from config import db
            cursor = db.get_connection().cursor()
            
            query = """
            SELECT COUNT(*) as count FROM leaves
            WHERE student_id = %s AND status != 'rejected'
            AND (
                (start_date <= %s AND end_date >= %s) OR
                (start_date >= %s AND start_date <= %s)
            )
            """
            
            params = [student_id, end_date, start_date, start_date, end_date]
            
            if exclude_leave_id:
                query += " AND id != %s"
                params.append(exclude_leave_id)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            return result['count'] > 0
        except Exception as e:
            return False
    
    @staticmethod
    def auto_approve_leave(leave_id):
        """Auto approve leave based on policies"""
        # Implement auto-approval logic if needed
        pass