from datetime import date, datetime
from sqlalchemy import func
from app import db
from app.models import Student, Subject, Attendance, Department, User

class AttendanceService:
    @staticmethod
    def mark_attendance(student_id: int, subject_id: int, att_date: date,
                        session: str, status: str, marked_by: int, remarks: str = None) -> tuple[Attendance, bool]:
        """
        Marks or updates attendance for a student.
        Prevents duplicate records using unique constraint (student_id, subject_id, date, session).
        Returns (attendance_record, created_boolean).
        """
        existing = Attendance.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            date=att_date,
            session=session
        ).first()

        if existing:
            existing.status = status
            existing.marked_by = marked_by
            if remarks is not None:
                existing.remarks = remarks
            existing.updated_at = datetime.utcnow()
            db.session.commit()
            return existing, False
        else:
            new_record = Attendance(
                student_id=student_id,
                subject_id=subject_id,
                date=att_date,
                session=session,
                status=status,
                marked_by=marked_by,
                remarks=remarks
            )
            db.session.add(new_record)
            db.session.commit()
            return new_record, True

    @staticmethod
    def get_student_attendance_summary(student_id: int) -> dict:
        """
        Calculates attendance percentage using:
        Attendance Percentage = (Present Classes / Total Conducted Classes) * 100
        Returns comprehensive breakdown including subject-wise stats and monthly trends.
        """
        records = Attendance.query.filter_by(student_id=student_id).all()
        total_classes = len(records)
        present_classes = sum(1 for r in records if r.status in ("Present", "Late"))
        absent_classes = sum(1 for r in records if r.status == "Absent")
        overall_percentage = round((present_classes / total_classes) * 100, 2) if total_classes > 0 else 0.0

        # Subject-wise calculation
        subjects = Subject.query.join(Attendance, Attendance.subject_id == Subject.id)\
            .filter(Attendance.student_id == student_id).distinct().all()
        
        subject_wise = []
        for sub in subjects:
            sub_records = [r for r in records if r.subject_id == sub.id]
            sub_total = len(sub_records)
            sub_present = sum(1 for r in sub_records if r.status in ("Present", "Late"))
            sub_pct = round((sub_present / sub_total) * 100, 2) if sub_total > 0 else 0.0
            subject_wise.append({
                "subject_id": sub.id,
                "name": sub.name,
                "code": sub.code,
                "semester": sub.semester,
                "credits": sub.credits,
                "conducted": sub_total,
                "attended": sub_present,
                "absent": sub_total - sub_present,
                "percentage": sub_pct
            })

        # Monthly breakdown
        monthly_map = {}
        for r in records:
            m_key = r.date.strftime("%b %Y")
            if m_key not in monthly_map:
                monthly_map[m_key] = {"conducted": 0, "present": 0}
            monthly_map[m_key]["conducted"] += 1
            if r.status in ("Present", "Late"):
                monthly_map[m_key]["present"] += 1

        monthly_trends = []
        for m_key, counts in monthly_map.items():
            pct = round((counts["present"] / counts["conducted"]) * 100, 1) if counts["conducted"] > 0 else 0.0
            monthly_trends.append({
                "month": m_key,
                "conducted": counts["conducted"],
                "present": counts["present"],
                "percentage": pct
            })

        return {
            "total_conducted": total_classes,
            "total_present": present_classes,
            "total_absent": absent_classes,
            "overall_percentage": overall_percentage,
            "subject_wise": subject_wise,
            "monthly_trends": monthly_trends,
            "recent_records": sorted(records, key=lambda x: x.date, reverse=True)[:15]
        }

    @staticmethod
    def get_subject_attendance_summary(subject_id: int) -> dict:
        records = Attendance.query.filter_by(subject_id=subject_id).all()
        total_sessions = db.session.query(Attendance.date, Attendance.session)\
            .filter_by(subject_id=subject_id).distinct().count()
        total_entries = len(records)
        present_entries = sum(1 for r in records if r.status in ("Present", "Late"))
        avg_pct = round((present_entries / total_entries) * 100, 2) if total_entries > 0 else 0.0

        return {
            "subject_id": subject_id,
            "total_sessions": total_sessions,
            "total_entries": total_entries,
            "present_entries": present_entries,
            "average_percentage": avg_pct
        }

    @staticmethod
    def get_low_attendance_students(threshold: float = 75.0, department_id: int = None, semester: int = None) -> list:
        """
        Returns list of students whose overall attendance percentage is below threshold.
        """
        query = Student.query
        if department_id:
            query = query.filter_by(department_id=department_id)
        if semester:
            query = query.filter_by(semester=semester)

        students = query.all()
        low_att_list = []

        for st in students:
            summary = AttendanceService.get_student_attendance_summary(st.id)
            if summary["total_conducted"] > 0 and summary["overall_percentage"] < threshold:
                low_att_list.append({
                    "student": st,
                    "roll_no": st.roll_no,
                    "name": st.user.name if st.user else "Unknown",
                    "email": st.user.email if st.user else "",
                    "department": st.department.name if st.department else "",
                    "semester": st.semester,
                    "conducted": summary["total_conducted"],
                    "present": summary["total_present"],
                    "percentage": summary["overall_percentage"]
                })

        return sorted(low_att_list, key=lambda x: x["percentage"])

attendance_service = AttendanceService()
