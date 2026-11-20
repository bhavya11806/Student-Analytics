-- =====================================================================
-- CLOUD-BASED STUDENT ATTENDANCE & PERFORMANCE ANALYTICS SYSTEM
-- Complete Relational Database Schema (MySQL / Amazon RDS)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS student_analytics
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE student_analytics;

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'faculty', 'student') NOT NULL DEFAULT 'student',
    phone VARCHAR(20) NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB;

-- 2. DEPARTMENTS TABLE
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dept_code (code)
) ENGINE=InnoDB;

-- 3. COURSES TABLE
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    department_id INT NOT NULL,
    duration_years INT NOT NULL DEFAULT 4,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    INDEX idx_course_dept (department_id)
) ENGINE=InnoDB;

-- 4. SEMESTERS TABLE
CREATE TABLE IF NOT EXISTS semesters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    semester_number INT NOT NULL,
    academic_year VARCHAR(20) NOT NULL DEFAULT '2026-2027',
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    CONSTRAINT uq_course_sem_year UNIQUE (course_id, semester_number, academic_year),
    INDEX idx_sem_course (course_id)
) ENGINE=InnoDB;

-- 5. SUBJECTS TABLE
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(30) NOT NULL UNIQUE,
    semester INT NOT NULL DEFAULT 1,
    department_id INT NOT NULL,
    credits INT NOT NULL DEFAULT 4,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    INDEX idx_subject_code (code),
    INDEX idx_subject_dept (department_id),
    INDEX idx_subject_sem (semester)
) ENGINE=InnoDB;

-- 6. FACULTY TABLE
CREATE TABLE IF NOT EXISTS faculty (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    employee_id VARCHAR(30) NOT NULL UNIQUE,
    department_id INT NOT NULL,
    designation VARCHAR(80) NOT NULL DEFAULT 'Assistant Professor',
    qualification VARCHAR(100) NOT NULL DEFAULT 'M.Tech / Ph.D',
    phone VARCHAR(20) NULL,
    status ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT,
    INDEX idx_faculty_emp (employee_id),
    INDEX idx_faculty_dept (department_id)
) ENGINE=InnoDB;

-- 7. FACULTY_SUBJECTS (TEACHING ASSIGNMENTS)
CREATE TABLE IF NOT EXISTS faculty_subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    subject_id INT NOT NULL,
    academic_year VARCHAR(20) NOT NULL DEFAULT '2026-2027',
    semester INT NOT NULL DEFAULT 1,
    assigned_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    CONSTRAINT uq_faculty_subject_year UNIQUE (faculty_id, subject_id, academic_year),
    INDEX idx_fs_faculty (faculty_id),
    INDEX idx_fs_subject (subject_id)
) ENGINE=InnoDB;

-- 8. STUDENTS TABLE
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    roll_no VARCHAR(40) NOT NULL UNIQUE,
    department_id INT NOT NULL,
    course VARCHAR(80) NOT NULL DEFAULT 'B.Tech Computer Science',
    semester INT NOT NULL DEFAULT 5,
    admission_year INT NOT NULL DEFAULT 2024,
    phone VARCHAR(20) NULL,
    account_status ENUM('Active', 'Inactive', 'Graduated') NOT NULL DEFAULT 'Active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT,
    INDEX idx_student_roll (roll_no),
    INDEX idx_student_dept (department_id),
    INDEX idx_student_sem (semester)
) ENGINE=InnoDB;

-- 9. ATTENDANCE TABLE (PREVENTS DUPLICATES)
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    date DATE NOT NULL,
    session VARCHAR(30) NOT NULL DEFAULT 'Regular',
    status ENUM('Present', 'Absent', 'Late') NOT NULL,
    marked_by INT NOT NULL,
    remarks VARCHAR(200) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT uq_attendance_student_sub_date_session UNIQUE (student_id, subject_id, date, session),
    INDEX idx_att_student (student_id),
    INDEX idx_att_subject (subject_id),
    INDEX idx_att_date (date)
) ENGINE=InnoDB;

-- 10. MARKS TABLE
CREATE TABLE IF NOT EXISTS marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    exam_type VARCHAR(60) NOT NULL,
    marks_obtained FLOAT NOT NULL,
    max_marks FLOAT NOT NULL,
    exam_date DATE NOT NULL,
    remarks VARCHAR(200) NULL,
    entered_by INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (entered_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_marks_student (student_id),
    INDEX idx_marks_subject (subject_id),
    INDEX idx_marks_exam (exam_type)
) ENGINE=InnoDB;

-- 11. NOTIFICATIONS TABLE (IN-APP & SNS ALERTS)
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(120) NOT NULL,
    message VARCHAR(500) NOT NULL,
    type VARCHAR(30) NOT NULL DEFAULT 'attendance_warning',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    sent_via_sns BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notif_user (user_id),
    INDEX idx_notif_read (is_read)
) ENGINE=InnoDB;

-- 12. ACADEMIC REPORTS TABLE (S3 STORAGE METADATA)
CREATE TABLE IF NOT EXISTS academic_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    report_type VARCHAR(40) NOT NULL,
    file_name VARCHAR(150) NOT NULL,
    file_path VARCHAR(255) NULL,
    s3_key VARCHAR(255) NULL,
    s3_url VARCHAR(500) NULL,
    file_size_kb FLOAT NOT NULL DEFAULT 0.0,
    generated_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_report_type (report_type)
) ENGINE=InnoDB;

-- 13. SYSTEM SETTINGS TABLE (ADMIN CONFIGURABLE THRESHOLDS)
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(50) NOT NULL UNIQUE,
    `value` VARCHAR(100) NOT NULL,
    description VARCHAR(255) NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_setting_key (`key`)
) ENGINE=InnoDB;
