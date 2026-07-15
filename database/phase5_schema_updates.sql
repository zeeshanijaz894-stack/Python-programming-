-- Phase 5: Student Management, Attendance & Leave System
-- Database Schema Updates

-- ===========================
-- STUDENT MANAGEMENT TABLES
-- ===========================

-- Enhanced Students Table with more details
ALTER TABLE students ADD COLUMN IF NOT EXISTS enrollment_date DATE;
ALTER TABLE students ADD COLUMN IF NOT EXISTS status ENUM('active', 'inactive', 'suspended', 'graduated') DEFAULT 'active';
ALTER TABLE students ADD COLUMN IF NOT EXISTS admission_number VARCHAR(50) UNIQUE;
ALTER TABLE students ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE students ADD COLUMN IF NOT EXISTS gender ENUM('M', 'F', 'Other');
ALTER TABLE students ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE students ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20);
ALTER TABLE students ADD COLUMN IF NOT EXISTS email VARCHAR(100) UNIQUE;
ALTER TABLE students ADD COLUMN IF NOT EXISTS father_name VARCHAR(100);
ALTER TABLE students ADD COLUMN IF NOT EXISTS mother_name VARCHAR(100);
ALTER TABLE students ADD COLUMN IF NOT EXISTS guardian_phone VARCHAR(20);
ALTER TABLE students ADD COLUMN IF NOT EXISTS blood_group VARCHAR(5);
ALTER TABLE students ADD COLUMN IF NOT EXISTS medical_conditions TEXT;
ALTER TABLE students ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE students ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- ===========================
-- ATTENDANCE TABLES
-- ===========================

-- Daily Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT NOT NULL,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('present', 'absent', 'late', 'leave', 'excused') NOT NULL,
    remarks TEXT,
    marked_by INT,
    marked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE KEY unique_attendance (student_id, attendance_date, class_id),
    INDEX idx_school_date (school_id, attendance_date),
    INDEX idx_student_date (student_id, attendance_date)
);

-- Attendance Policies Table
CREATE TABLE IF NOT EXISTS attendance_policies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT NOT NULL,
    policy_name VARCHAR(100),
    max_late_minutes INT DEFAULT 15,
    min_present_percentage DECIMAL(5,2) DEFAULT 75.00,
    warning_threshold INT DEFAULT 5,
    action_on_absence_days INT DEFAULT 10,
    academic_impact_days INT DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id),
    UNIQUE KEY unique_policy (school_id)
);

-- ===========================
-- LEAVE MANAGEMENT TABLES
-- ===========================

-- Leave Types Table
CREATE TABLE IF NOT EXISTS leave_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT NOT NULL,
    leave_name VARCHAR(100) NOT NULL,
    leave_code VARCHAR(20) UNIQUE,
    max_days INT DEFAULT 5,
    requires_approval BOOLEAN DEFAULT TRUE,
    applicable_to ENUM('students', 'staff', 'both') DEFAULT 'students',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id),
    UNIQUE KEY unique_leave_type (school_id, leave_name)
);

-- Leave Applications Table
CREATE TABLE IF NOT EXISTS leave_applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT NOT NULL,
    student_id INT NOT NULL,
    leave_type_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    no_of_days INT NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'cancelled') DEFAULT 'pending',
    approved_by INT,
    approval_remarks TEXT,
    approved_date TIMESTAMP NULL,
    submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (leave_type_id) REFERENCES leave_types(id),
    FOREIGN KEY (approved_by) REFERENCES users(id),
    INDEX idx_student_status (student_id, status),
    INDEX idx_date_range (start_date, end_date)
);

-- ===========================
-- ATTENDANCE ANALYTICS TABLES
-- ===========================

-- Monthly Attendance Summary
CREATE TABLE IF NOT EXISTS monthly_attendance_summary (
    id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT NOT NULL,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    total_days INT,
    present_days INT,
    absent_days INT,
    late_days INT,
    leave_days INT,
    percentage DECIMAL(5,2),
    status ENUM('good', 'satisfactory', 'poor', 'critical') DEFAULT 'good',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE KEY unique_summary (student_id, month, year),
    INDEX idx_monthly_report (school_id, month, year)
);

-- ===========================
-- INDEXES FOR PERFORMANCE
-- ===========================

CREATE INDEX IF NOT EXISTS idx_student_status ON students(status, school_id);
CREATE INDEX IF NOT EXISTS idx_student_class ON students(class_id, school_id);
CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status, school_id);
CREATE INDEX IF NOT EXISTS idx_leave_status ON leave_applications(status, school_id);

-- ===========================
-- DEFAULT DATA
-- ===========================

-- Default Leave Types
INSERT INTO leave_types (school_id, leave_name, leave_code, max_days, description)
SELECT id, 'Casual Leave', 'CL', 10, 'General casual leave for students' FROM schools
WHERE id NOT IN (SELECT school_id FROM leave_types WHERE leave_code = 'CL')
LIMIT 1;

INSERT INTO leave_types (school_id, leave_name, leave_code, max_days, description)
SELECT id, 'Medical Leave', 'ML', 15, 'Leave due to medical reasons' FROM schools
WHERE id NOT IN (SELECT school_id FROM leave_types WHERE leave_code = 'ML')
LIMIT 1;

INSERT INTO leave_types (school_id, leave_name, leave_code, max_days, description)
SELECT id, 'Emergency Leave', 'EL', 5, 'Emergency leave for urgent situations' FROM schools
WHERE id NOT IN (SELECT school_id FROM leave_types WHERE leave_code = 'EL')
LIMIT 1;

-- Default Attendance Policies
INSERT INTO attendance_policies (school_id, policy_name, max_late_minutes, min_present_percentage, warning_threshold, action_on_absence_days)
SELECT id, 'Default Policy', 15, 75.00, 5, 10 FROM schools
WHERE id NOT IN (SELECT school_id FROM attendance_policies)
LIMIT 1;
