-- =====================================================================
-- CLOUD-BASED STUDENT ATTENDANCE & PERFORMANCE ANALYTICS SYSTEM
-- Sample Seed Data Script (MySQL / Amazon RDS)
-- All demo user passwords are:
-- Admin: Admin@123 | Faculty: Faculty@123 | Student: Student@123
-- =====================================================================

USE student_analytics;

-- 1. System Settings
INSERT INTO system_settings (`key`, `value`, description) VALUES
('ATTENDANCE_THRESHOLD', '75.0', 'Minimum required attendance percentage (%)'),
('ACADEMIC_PASS_THRESHOLD', '40.0', 'Academic passing threshold score (%)'),
('ACADEMIC_GOOD_THRESHOLD', '75.0', 'Academic excellence benchmark (%)')
ON DUPLICATE KEY UPDATE `value`=VALUES(`value`);

-- 2. Departments
INSERT INTO departments (id, name, code, description) VALUES
(1, 'Computer Science & Engineering', 'CSE', 'Department of Computer Science and Engineering'),
(2, 'Information Technology', 'IT', 'Department of Information Technology')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 3. Courses
INSERT INTO courses (id, name, code, department_id, duration_years) VALUES
(1, 'B.Tech Computer Science & Engineering', 'BTECH-CSE', 1, 4),
(2, 'B.Tech Information Technology', 'BTECH-IT', 2, 4)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 4. Semesters
INSERT INTO semesters (course_id, semester_number, academic_year) VALUES
(1, 5, '2026-2027'),
(2, 5, '2026-2027')
ON DUPLICATE KEY UPDATE academic_year=VALUES(academic_year);

-- 5. Subjects
INSERT INTO subjects (id, name, code, semester, department_id, credits) VALUES
(1, 'Cloud Computing & Distributed Systems', 'CS501', 5, 1, 4),
(2, 'Database Management Systems', 'CS502', 5, 1, 4),
(3, 'Machine Learning & Data Mining', 'CS503', 5, 1, 4),
(4, 'Computer Networks & Security', 'CS504', 5, 1, 3),
(5, 'Software Engineering & Agile', 'CS505', 5, 1, 3)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 6. Users (Admin, Faculty, Students)
-- Hash generated via werkzeug scrypt
INSERT INTO users (id, name, email, password_hash, role, phone, active) VALUES
(1, 'Dr. Arthur Vance (Dean)', 'admin@demo.com', 'scrypt:32768:8:1$1uWv6Z6Zk9b7DqN3$ad0035a720e98583483df235be6b4eb5adabf65d1d6a8ad8d7c492ee7caeeea79fa18a221fcae13bc3f1f33777598801ce703cf93652db740879c3558b813f8c', 'admin', '+91 98765 43210', 1),
(2, 'Prof. Marcus Thorne', 'faculty@demo.com', 'scrypt:32768:8:1$9Kj2L9m0p8Q1vX3Y$7a56114eb91eb336c1e956bc9b6e838efca88713f0449582ad65da24c04207908b98eb6cbfd5f66144e590fa38392cf99a8bcba4304856f64264fe4bdf67b4df', 'faculty', '+91 98765 00001', 1),
(3, 'Dr. Elena Rostova', 'elena@demo.com', 'scrypt:32768:8:1$9Kj2L9m0p8Q1vX3Y$7a56114eb91eb336c1e956bc9b6e838efca88713f0449582ad65da24c04207908b98eb6cbfd5f66144e590fa38392cf99a8bcba4304856f64264fe4bdf67b4df', 'faculty', '+91 98765 00002', 1),
(4, 'Demo Student', 'student@demo.com', 'scrypt:32768:8:1$4Bn3M8q1r9T2uW4Z$12ef669da61bcbb982d61f1e8a937a0eb52efbeeb57f7ebf88e360980ff69be29304910cf917300c144e590fa38392cf99a8bcba4304856f64264fe4bdf67b4df', 'student', '+91 91234 56701', 1),
(5, 'Emma Watson', 'emma@demo.com', 'scrypt:32768:8:1$4Bn3M8q1r9T2uW4Z$12ef669da61bcbb982d61f1e8a937a0eb52efbeeb57f7ebf88e360980ff69be29304910cf917300c144e590fa38392cf99a8bcba4304856f64264fe4bdf67b4df', 'student', '+91 91234 56702', 1),
(6, 'Rahul Sharma (Att Risk)', 'rahul@demo.com', 'scrypt:32768:8:1$4Bn3M8q1r9T2uW4Z$12ef669da61bcbb982d61f1e8a937a0eb52efbeeb57f7ebf88e360980ff69be29304910cf917300c144e590fa38392cf99a8bcba4304856f64264fe4bdf67b4df', 'student', '+91 91234 56704', 1),
(7, 'John Doe (Acad Risk)', 'john@demo.com', 'scrypt:32768:8:1$4Bn3M8q1r9T2uW4Z$12ef669da61bcbb982d61f1e8a937a0eb52efbeeb57f7ebf88e360980ff69be29304910cf917300c144e590fa38392cf99a8bcba4304856f64264fe4bdf67b4df', 'student', '+91 91234 56706', 1),
(8, 'Vikram Singh (High Risk)', 'vikram@demo.com', 'scrypt:32768:8:1$4Bn3M8q1r9T2uW4Z$12ef669da61bcbb982d61f1e8a937a0eb52efbeeb57f7ebf88e360980ff69be29304910cf917300c144e590fa38392cf99a8bcba4304856f64264fe4bdf67b4df', 'student', '+91 91234 56708', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 7. Faculty Details
INSERT INTO faculty (id, user_id, employee_id, department_id, designation, qualification, status) VALUES
(1, 2, 'FAC101', 1, 'Professor & Head', 'Ph.D. in Computer Science', 'Active'),
(2, 3, 'FAC102', 1, 'Associate Professor', 'Ph.D. in Computer Engineering', 'Active')
ON DUPLICATE KEY UPDATE employee_id=VALUES(employee_id);

-- 8. Faculty Subject Assignments
INSERT INTO faculty_subjects (faculty_id, subject_id, academic_year, semester) VALUES
(1, 1, '2026-2027', 5),
(2, 2, '2026-2027', 5)
ON DUPLICATE KEY UPDATE academic_year=VALUES(academic_year);

-- 9. Student Details
INSERT INTO students (id, user_id, roll_no, department_id, course, semester, admission_year, account_status) VALUES
(1, 4, 'CSE2024001', 1, 'B.Tech Computer Science', 5, 2024, 'Active'),
(2, 5, 'CSE2024002', 1, 'B.Tech Computer Science', 5, 2024, 'Active'),
(3, 6, 'CSE2024004', 1, 'B.Tech Computer Science', 5, 2024, 'Active'),
(4, 7, 'CSE2024006', 1, 'B.Tech Computer Science', 5, 2024, 'Active'),
(5, 8, 'CSE2024008', 1, 'B.Tech Computer Science', 5, 2024, 'Active')
ON DUPLICATE KEY UPDATE roll_no=VALUES(roll_no);
