"""
Phase 5: Database Schema - Attendance and Leave Tables
"""

# SQL Schema for Phase 5 - Attendance and Leave Management

ATTENDANCE_TABLE = """
CREATE TABLE IF NOT EXISTS attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT NOT NULL,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('present', 'absent', 'late', 'leave', 'excused') NOT NULL,
    remarks TEXT,
    marked_by INT,
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_attendance (school_id, student_id, class_id, attendance_date),
    FOREIGN KEY (school_id) REFERENCES schools(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (marked_by) REFERENCES users(id),
    INDEX idx_school (school_id),
    INDEX idx_student (student_id),
    INDEX idx_class (class_id),
    INDEX idx_date (attendance_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

MONTHLY_ATTENDANCE_SUMMARY_TABLE = """
CREATE TABLE IF NOT EXISTS monthly_attendance_summary (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT NOT NULL,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    total_days INT DEFAULT 0,
    present_days INT DEFAULT 0,
    absent_days INT DEFAULT 0,
    late_days INT DEFAULT 0,
    leave_days INT DEFAULT 0,
    percentage DECIMAL(5, 2) DEFAULT 0,
    status ENUM('good', 'satisfactory', 'poor') DEFAULT 'satisfactory',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_summary (school_id, student_id, month, year),
    FOREIGN KEY (school_id) REFERENCES schools(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    INDEX idx_school (school_id),
    INDEX idx_student (student_id),
    INDEX idx_month_year (month, year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

LEAVES_TABLE = """
CREATE TABLE IF NOT EXISTS leaves (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT NOT NULL,
    student_id INT NOT NULL,
    leave_type ENUM('medical', 'casual', 'emergency', 'parental', 'other') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'cancelled') DEFAULT 'pending',
    documents JSON,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INT,
    approved_at TIMESTAMP NULL,
    remarks TEXT,
    rejected_by INT,
    rejected_at TIMESTAMP NULL,
    rejection_reason TEXT,
    FOREIGN KEY (school_id) REFERENCES schools(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (approved_by) REFERENCES users(id),
    FOREIGN KEY (rejected_by) REFERENCES users(id),
    INDEX idx_school (school_id),
    INDEX idx_student (student_id),
    INDEX idx_status (status),
    INDEX idx_dates (start_date, end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

LEAVE_POLICIES_TABLE = """
CREATE TABLE IF NOT EXISTS leave_policies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT NOT NULL,
    leave_type VARCHAR(50) NOT NULL,
    max_days INT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_policy (school_id, leave_type),
    FOREIGN KEY (school_id) REFERENCES schools(id),
    INDEX idx_school (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

def init_phase5_schema(cursor):
    """Initialize Phase 5 database schema"""
    try:
        cursor.execute(ATTENDANCE_TABLE)
        cursor.execute(MONTHLY_ATTENDANCE_SUMMARY_TABLE)
        cursor.execute(LEAVES_TABLE)
        cursor.execute(LEAVE_POLICIES_TABLE)
        
        # Create default leave policies
        default_policies = [
            ("medical", 10, "Medical leave for health reasons"),
            ("casual", 8, "Casual/personal leave"),
            ("emergency", 3, "Emergency leave"),
            ("parental", 15, "Parental leave"),
            ("other", 2, "Other approved leave")
        ]
        
        for leave_type, max_days, description in default_policies:
            cursor.execute("""
                INSERT IGNORE INTO leave_policies (school_id, leave_type, max_days, description)
                SELECT id, %s, %s, %s FROM schools
            """, (leave_type, max_days, description))
        
        return True
    except Exception as e:
        print(f"Error initializing Phase 5 schema: {str(e)}")
        return False