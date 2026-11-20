# Database Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o| STUDENTS : "has profile"
    USERS ||--o| FACULTY : "has profile"
    USERS ||--o{ NOTIFICATIONS : "receives"
    USERS ||--o{ ACADEMIC_REPORTS : "generates"
    USERS ||--o{ ATTENDANCE : "marks"

    DEPARTMENTS ||--o{ COURSES : "offers"
    DEPARTMENTS ||--o{ SUBJECTS : "belongs to"
    DEPARTMENTS ||--o{ FACULTY : "employs"
    DEPARTMENTS ||--o{ STUDENTS : "enrolls"

    COURSES ||--o{ SEMESTERS : "contains"

    FACULTY ||--o{ FACULTY_SUBJECTS : "teaches"
    SUBJECTS ||--o{ FACULTY_SUBJECTS : "assigned to"

    STUDENTS ||--o{ ATTENDANCE : "attends"
    SUBJECTS ||--o{ ATTENDANCE : "conducted for"

    STUDENTS ||--o{ MARKS : "scored by"
    SUBJECTS ||--o{ MARKS : "evaluated in"

    USERS {
        int id PK
        string name
        string email UK
        string password_hash
        string role
        string phone
        boolean active
        datetime created_at
    }

    DEPARTMENTS {
        int id PK
        string name UK
        string code UK
        text description
    }

    COURSES {
        int id PK
        string name
        string code UK
        int department_id FK
        int duration_years
    }

    SEMESTERS {
        int id PK
        int course_id FK
        int semester_number
        string academic_year
    }

    SUBJECTS {
        int id PK
        string name
        string code UK
        int semester
        int department_id FK
        int credits
    }

    FACULTY {
        int id PK
        int user_id FK,UK
        string employee_id UK
        int department_id FK
        string designation
        string qualification
        string status
    }

    FACULTY_SUBJECTS {
        int id PK
        int faculty_id FK
        int subject_id FK
        string academic_year
        int semester
    }

    STUDENTS {
        int id PK
        int user_id FK,UK
        string roll_no UK
        int department_id FK
        string course
        int semester
        int admission_year
        string account_status
    }

    ATTENDANCE {
        int id PK
        int student_id FK
        int subject_id FK
        date date
        string session
        string status
        int marked_by FK
        string remarks
    }

    MARKS {
        int id PK
        int student_id FK
        int subject_id FK
        string exam_type
        float marks_obtained
        float max_marks
        date exam_date
        string remarks
    }

    NOTIFICATIONS {
        int id PK
        int user_id FK
        string title
        string message
        string type
        boolean is_read
        boolean sent_via_sns
    }

    ACADEMIC_REPORTS {
        int id PK
        string title
        string report_type
        string file_name
        string s3_key
        string s3_url
        float file_size_kb
        int generated_by FK
    }

    SYSTEM_SETTINGS {
        int id PK
        string key UK
        string value
        string description
    }
```
