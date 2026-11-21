# Cloud-Based Student Attendance & Performance Analytics System

An enterprise-grade, cloud-architected academic management and intelligence web platform built with **Python Flask**, **Amazon RDS (MySQL)**, **Amazon S3**, **AWS Lambda**, **Amazon EventBridge**, **Amazon SNS**, **Chart.js**, and **Bootstrap 5**.
i am abc
---

## 📌 Executive Overview

The **Cloud-Based Student Attendance & Performance Analytics System** solves systemic challenges in higher education administration by digitizing attendance logging, internal assessment tracking, automated low-attendance warnings, and student academic risk surveillance.
avfd...
### Key Capabilities
- **Role-Based Access Control (RBAC):** Dedicated, secure dashboards for **Admin**, **Faculty**, and **Students**.
- **Accurate Attendance Management:** Real-time logging with strict duplicate entry prevention `(student_id, subject_id, date, session)`.
- **Academic Performance & Marks Tracking:** Internal assessment and examination score calculation, grade generation ($A^+$, $A$, $B^+$, $B$, $C$, $D$, $F$), and percentage metrics.
- **Rule-Based Academic Risk Identification:** Early warning categorization ($GOOD$, $ATTENDANCE\ RISK$, $ACADEMIC\ RISK$, $HIGH\ RISK$, $MODERATE$) with configurable administrative thresholds.
- **Official Reports Engine:** Instant download of signed **PDF reports** (via ReportLab) and **Excel master sheets** (via OpenPyXL), stored in **Amazon S3** with time-limited presigned URLs.
- **Automated Cloud Surveillance:** Daily serverless execution via **Amazon EventBridge** triggering an **AWS Lambda** function to publish **Amazon SNS** multi-channel alerts to students with attendance deficits ($< 75\%$).

---

## 🏗️ Technology Architecture

```
                                  +-----------------------------+
                                  |     Amazon EventBridge      |
                                  | (Daily 17:30 IST Schedule)  |
                                  +--------------+--------------+
                                                 |
                                                 v
                                  +-----------------------------+
                                  |         AWS Lambda          |
                                  |  (Attendance Check Function)|
                                  +-------+--------------+------+
                                          |              |
                                          v              v
+-----------------------+         +---------------+ +----+--------------------+
|  Client Browser       |         |   Amazon SNS  | | Amazon RDS (MySQL)      |
| (Bootstrap 5 / Charts)|         | (Alert Topic) | | - users, students       |
+-----------+-----------+         +---------------+ | - attendance, marks     |
            |                                       | - system_settings       |
            v                                       +----+--------------------+
+-----------------------+                                |
|    Amazon EC2         |                                |
|  - Nginx (Port 80)    |                                |
|  - Gunicorn WSGI      |                                |
|  - Flask Application  +--------------------------------+
+-----------+-----------+
            |
            v
+-----------------------+
|      Amazon S3        |
| (Encrypted PDF/Excel) |
+-----------------------+
```

| Layer | Technologies & Services |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4 |
| **Backend** | Python 3.10+, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Werkzeug |
| **Database** | MySQL 8.0, Amazon RDS MySQL, SQLite (offline development fallback) |
| **Cloud (AWS)** | Amazon EC2, Amazon RDS, Amazon S3, AWS Lambda, Amazon EventBridge, Amazon SNS, Amazon CloudWatch, AWS IAM |
| **Document Processing** | ReportLab (vector PDF generation), OpenPyXL (Excel spreadsheets), Pandas, NumPy |

---
## ⚡ Quick Start & Local Setup

### 1. Clone & Enter Repository
```bash
git clone <repository_url>
cd student_analytics_cloud
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*Note: By default, the application runs out-of-the-box using local SQLite (`student_analytics.db`) and local document storage. To connect Amazon RDS or Amazon S3, update the credentials in `.env`.*

### 4. Run Application
```bash
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 🔑 Demo Access Credentials

The database automatically seeds realistic college demo data on the first run with **11 students** across all risk profiles, **3 faculty members**, and an **admin dean**.

| Role | Email Address | Password | Primary Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@demo.com` | `Admin@123` | Institutional dashboard, student/faculty CRUD, curriculum, threshold settings, audits |
| **Faculty** | `faculty@demo.com` | `Faculty@123` | Teaching dashboard, daily attendance marking, examination marks entry, student roster |
| **Student** | `student@demo.com` | `Student@123` | Personal attendance tracking, subject breakdown, examination scores, verified PDF downloads |

*The login screen includes quick one-click credential auto-fill buttons for demonstration purposes.*

---

## 📊 Academic Risk Classification Logic

The system utilizes an explainable, deterministic rule-based surveillance model governed by configurable administrative thresholds:

$$\text{Attendance Rate} = \left( \frac{\text{Attended Classes}}{\text{Total Conducted Classes}} \right) \times 100$$

$$\text{Academic Score} = \left( \frac{\text{Total Marks Obtained}}{\text{Total Maximum Marks}} \right) \times 100$$

| Category | Attendance Rate ($\%$) | Academic Score ($\%$) | Automated System Response |
| :--- | :---: | :---: | :--- |
| **GOOD** | $\ge 75\%$ | $\ge 75\%$ | Eligible for dean's list and academic distinction. |
| **ATTENDANCE RISK** | $< 75\%$ | $\ge 75\%$ | Warning notice dispatched; mentor counseling required. |
| **ACADEMIC RISK** | $\ge 75\%$ | $< 40\%$ | Remedial tutorial assignment and peer-tutoring enrollments. |
| **HIGH RISK** | $< 75\%$ | $< 40\%$ | Urgent parental notification and academic probation review. |
| **MODERATE** | $\ge 75\%$ | $40\% \le \text{Score} < 75\%$ | Standard passing progress; encouraged to join exam reviews. |

---

## ☁️ AWS Cloud Deployment Guide

### A. Amazon RDS (MySQL)
1. In the AWS Console, create a **MySQL 8.0** RDS db instance (`db.t3.micro` for Free Tier).
2. Attach it to your private VPC subnet with inbound port `3306` permitted from your EC2 Security Group.
3. Import the initial database schema:
   ```bash
   mysql -h your-rds-endpoint.amazonaws.com -u dbadmin -p student_analytics < database/schema.sql
   mysql -h your-rds-endpoint.amazonaws.com -u dbadmin -p student_analytics < database/sample_data.sql
   ```
4. Set `DATABASE_URL` in `.env`:
   `mysql+pymysql://dbadmin:YourPassword@your-rds-endpoint.amazonaws.com:3306/student_analytics`

### B. Amazon S3 (Encrypted Document Bucket)
1. Create a private bucket: `student-analytics-reports-xxxx`.
2. Block all public access (enabled by default).
3. Enable server-side encryption (SSE-S3).
4. The application generates **time-limited presigned URLs** (default expiration: 3600 seconds) for authorized report downloads.

### C. AWS Lambda & Amazon EventBridge
1. Create a Lambda function with Python 3.10+ runtime using `aws/lambda/attendance_alert.py`.
2. Add environment variables:
   - `SNS_TOPIC_ARN=arn:aws:sns:ap-south-1:xxxx:student-attendance-alerts`
   - `ATTENDANCE_THRESHOLD=75.0`
3. In **Amazon EventBridge**, configure a rule with schedule expression `cron(0 12 * * ? *)` (runs daily at 17:30 IST) targeting the Lambda function.

### D. Amazon EC2 Deployment
1. Launch an Ubuntu 22.04 LTS instance with an attached IAM Role matching `aws/iam_policies.json`.
2. Open Security Group inbound ports: `80` (HTTP), `443` (HTTPS), and `22` (SSH).
3. Execute the automated provisioning script:
   ```bash
   chmod +x aws/deployment/ec2_setup.sh
   ./aws/deployment/ec2_setup.sh
   ```

---

## 🧪 Test Suite Execution

Execute the comprehensive automated test suite covering authentication, RBAC, attendance duplicate prevention, marks validations, risk algorithms, and PDF/Excel generation:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

All 17 integration and unit tests execute in under 60 seconds with 100% pass rate.

---

## 📂 Project Structure

```
student_analytics_cloud/
├── app/
│   ├── __init__.py               # Flask application factory & database seeder
│   ├── models/                   # Relational SQLAlchemy models (12 tables)
│   │   ├── user.py, student.py, faculty.py, department.py
│   │   ├── subject.py, attendance.py, marks.py, settings.py
│   ├── routes/                   # Modular blueprint controllers
│   │   ├── auth.py, admin.py, faculty.py, student.py
│   │   ├── attendance.py, marks.py, analytics.py, reports.py
│   ├── services/                 # Business logic, S3, SNS, PDF & Excel generation
│   │   ├── attendance_service.py, analytics_service.py
│   │   ├── notification_service.py, report_service.py, s3_service.py
│   ├── templates/                # Jinja2 responsive templates (Bootstrap 5)
│   ├── static/                   # CSS stylesheets and Chart.js scripts
│   └── utils/                    # Role decorators & input validators
├── aws/                          # AWS Cloud infrastructure assets
│   ├── lambda/attendance_alert.py
│   ├── eventbridge/schedule_setup.md
│   ├── deployment/ec2_setup.sh, nginx.conf, student_analytics.service
│   └── iam_policies.json, cloudwatch_setup.md
├── database/                     # MySQL schema, sample data & ER diagram
│   ├── schema.sql, sample_data.sql, er_diagram.md
├── docs/                         # Academic documentation & viva presentation outline
│   ├── college_project_documentation.md, presentation_outline.md
├── tests/                        # Automated unit & integration tests
│   ├── test_auth.py, test_attendance.py, test_marks.py, test_analytics.py, test_reports.py
├── config/config.py              # Environment configuration
├── requirements.txt              # Production Python package manifest
├── run.py                        # WSGI entrypoint
└── README.md
``` file
---│   ├── models/                   # Relational SQLAlchemy models (12 tables)
│   │   ├── user.py, student.py, faculty.py, department.py
│   │   ├── subject.py, attendance.py, marks.py, settings.py
│   ├── routes/                   # Modular blueprint controllers
│   │   ├── auth.py, admin.py, faculty.py, student.py
│   │   ├── attendance.py, marks.py, analytics.py, reports.py
│   ├── services/                 # Business logic, S3, SNS, PDF & Excel generation
│   │   ├── attendance_service.py, analytics_service.py
│   │   ├── notification_service.py, report_service.py, s3_service.py
│   ├── templates/                # Jinja2 responsive templates (Bootstrap 5)
│   ├── static/                   # CSS stylesheets and Chart.js scripts
│   └── utils/                    # Role decorators & input validators
├── aws/                          # AWS Cloud infrastructure assets
│   ├── lambda/attendance_alert.py
│   ├── eventbridge/schedule_setup.md
│   ├── deployment/ec2_setup.sh, nginx.conf, student_analytics.service
│   └── iam_policies.json, cloudwatch_setup.md
├── database/                     # MySQL schema, sample data & ER diagram
│   ├── schema.sql, sample_data.sql, er_diagram.md
├── docs/                         # Academic documentation & viva presentation outline
│   ├── college_project_documentation.md, presentation_outline.md
├── tests/                        # Automated unit & integration tests
│   ├── test_auth.py, test_attendance.py, test_marks.py, test_analytics.py, test_reports.py
├── config/config.py              # Environment configuration
├── requirements.txt              # Production Python package manifest
├── run.py                        # WSGI entrypoint
└── README.md
``` file
---

## 📜 License & Academic Integrity
Developed as a Capstone Engineering College Project. Built in compliance with enterprise cloud security best practices and modern Software Engineering standards.
