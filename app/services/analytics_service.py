from sqlalchemy import func
from app import db
from app.models import Student, Subject, Attendance, Mark, Faculty, Department, SystemSetting
from app.services.attendance_service import attendance_service

class AnalyticsService:
    @staticmethod
    def get_thresholds() -> dict:
        att = float(SystemSetting.get_value("ATTENDANCE_THRESHOLD", "75.0"))
        pass_mark = float(SystemSetting.get_value("ACADEMIC_PASS_THRESHOLD", "40.0"))
        good_mark = float(SystemSetting.get_value("ACADEMIC_GOOD_THRESHOLD", "75.0"))
        return {
            "attendance_threshold": att,
            "academic_pass_threshold": pass_mark,
            "academic_good_threshold": good_mark
        }

    @staticmethod
    def update_thresholds(att: float, pass_mark: float, good_mark: float) -> dict:
        SystemSetting.set_value("ATTENDANCE_THRESHOLD", str(att), "Minimum required attendance percentage")
        SystemSetting.set_value("ACADEMIC_PASS_THRESHOLD", str(pass_mark), "Academic passing mark percentage")
        SystemSetting.set_value("ACADEMIC_GOOD_THRESHOLD", str(good_mark), "Academic excellence threshold percentage")
        return AnalyticsService.get_thresholds()

    @staticmethod
    def calculate_grade(pct: float) -> str:
        if pct >= 90.0: return "A+"
        if pct >= 80.0: return "A"
        if pct >= 70.0: return "B+"
        if pct >= 60.0: return "B"
        if pct >= 50.0: return "C"
        if pct >= 40.0: return "D"
        return "F"

    @staticmethod
    def get_student_academic_summary(student_id: int) -> dict:
        """
        Calculates student's marks and performance across all exams and subjects.
        Performance Percentage = (Total Marks Obtained / Total Maximum Marks) * 100
        """
        marks = Mark.query.filter_by(student_id=student_id).all()
        if not marks:
            return {
                "total_exams": 0,
                "total_obtained": 0.0,
                "total_max": 0.0,
                "overall_percentage": 0.0,
                "grade": "N/A",
                "subject_wise_performance": []
            }

        total_obtained = sum(m.marks_obtained for m in marks)
        total_max = sum(m.max_marks for m in marks)
        overall_pct = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0.0

        # Group by subject
        subject_dict = {}
        for m in marks:
            if m.subject_id not in subject_dict:
                subject_dict[m.subject_id] = {
                    "subject": m.subject,
                    "obtained": 0.0,
                    "max": 0.0,
                    "records": []
                }
            subject_dict[m.subject_id]["obtained"] += m.marks_obtained
            subject_dict[m.subject_id]["max"] += m.max_marks
            subject_dict[m.subject_id]["records"].append(m)

        subject_wise = []
        for s_id, s_data in subject_dict.items():
            sub = s_data["subject"]
            s_pct = round((s_data["obtained"] / s_data["max"]) * 100, 2) if s_data["max"] > 0 else 0.0
            subject_wise.append({
                "subject_id": s_id,
                "name": sub.name if sub else "Unknown",
                "code": sub.code if sub else "",
                "total_obtained": s_data["obtained"],
                "total_max": s_data["max"],
                "percentage": s_pct,
                "grade": AnalyticsService.calculate_grade(s_pct),
                "exam_count": len(s_data["records"])
            })

        return {
            "total_exams": len(marks),
            "total_obtained": round(total_obtained, 1),
            "total_max": round(total_max, 1),
            "overall_percentage": overall_pct,
            "grade": AnalyticsService.calculate_grade(overall_pct),
            "subject_wise_performance": sorted(subject_wise, key=lambda x: x["percentage"], reverse=True)
        }

    @staticmethod
    def classify_student_risk(student_id: int) -> dict:
        """
        Classifies students into risk categories based on configurable thresholds:
        - GOOD: Attendance >= 75% and Performance >= 75%
        - ATTENDANCE RISK: Attendance < 75% and Performance >= 75%
        - ACADEMIC RISK: Attendance >= 75% and Performance < 40%
        - HIGH RISK: Attendance < 75% and Performance < 40%
        - MODERATE PROGRESS: Others (e.g., Attendance >= 75% and 40% <= Performance < 75%)
        """
        thresholds = AnalyticsService.get_thresholds()
        att_threshold = thresholds["attendance_threshold"]
        pass_threshold = thresholds["academic_pass_threshold"]
        good_threshold = thresholds["academic_good_threshold"]

        att_summary = attendance_service.get_student_attendance_summary(student_id)
        acad_summary = AnalyticsService.get_student_academic_summary(student_id)

        att_pct = att_summary["overall_percentage"]
        acad_pct = acad_summary["overall_percentage"]

        if att_pct >= att_threshold and acad_pct >= good_threshold:
            category = "GOOD"
            badge_class = "success"
            icon = "bi-check-circle-fill"
            description = "Consistently high attendance and strong academic scores."
            action = "Eligible for honors and academic merit recognitions."
        elif att_pct < att_threshold and acad_pct >= good_threshold:
            category = "ATTENDANCE RISK"
            badge_class = "warning"
            icon = "bi-exclamation-triangle-fill"
            description = f"Academic score is strong ({acad_pct}%), but attendance is critically low (< {att_threshold}%)."
            action = "Issue attendance alert and require faculty mentor sign-off."
        elif att_pct >= att_threshold and acad_pct < pass_threshold:
            category = "ACADEMIC RISK"
            badge_class = "danger"
            icon = "bi-x-circle-fill"
            description = f"Regular attendance ({att_pct}%), but performance is below pass threshold (< {pass_threshold}%)."
            action = "Recommend remedial tutorials, internal re-tests, and peer tutoring."
        elif att_pct < att_threshold and acad_pct < pass_threshold:
            category = "HIGH RISK"
            badge_class = "dark"
            icon = "bi-shield-slash-fill"
            description = f"Severely deficient in both attendance (< {att_threshold}%) and academic marks (< {pass_threshold}%)."
            action = "Immediate intervention: Contact parents/guardian, mandatory counseling meeting."
        else:
            category = "MODERATE PROGRESS"
            badge_class = "info"
            icon = "bi-info-circle-fill"
            description = "Satisfactory attendance with standard passing performance."
            action = "Encourage participation in review sessions to reach excellence."

        return {
            "student_id": student_id,
            "category": category,
            "badge_class": badge_class,
            "icon": icon,
            "attendance_percentage": att_pct,
            "academic_percentage": acad_pct,
            "grade": acad_summary["grade"],
            "description": description,
            "recommended_action": action
        }

    @staticmethod
    def get_all_students_risk_list(department_id: int = None, semester: int = None) -> list:
        query = Student.query
        if department_id:
            query = query.filter_by(department_id=department_id)
        if semester:
            query = query.filter_by(semester=semester)

        students = query.all()
        risk_records = []
        for st in students:
            risk = AnalyticsService.classify_student_risk(st.id)
            risk_records.append({
                "student": st,
                "roll_no": st.roll_no,
                "name": st.user.name if st.user else "Unknown",
                "department": st.department.name if st.department else "",
                "semester": st.semester,
                "attendance_percentage": risk["attendance_percentage"],
                "academic_percentage": risk["academic_percentage"],
                "grade": risk["grade"],
                "category": risk["category"],
                "badge_class": risk["badge_class"],
                "icon": risk["icon"],
                "recommended_action": risk["recommended_action"]
            })

        return risk_records

    @staticmethod
    def get_college_analytics() -> dict:
        total_students = Student.query.count()
        total_faculty = Faculty.query.count()
        total_subjects = Subject.query.count()
        
        # Attendance overall
        total_att = Attendance.query.count()
        present_att = Attendance.query.filter(Attendance.status.in_(["Present", "Late"])).count()
        overall_attendance = round((present_att / total_att) * 100, 1) if total_att > 0 else 0.0

        # Performance overall
        avg_perf = db.session.query(func.avg(Mark.marks_obtained * 100.0 / Mark.max_marks)).scalar()
        overall_performance = round(float(avg_perf), 1) if avg_perf else 0.0

        # Risk distribution
        all_risks = AnalyticsService.get_all_students_risk_list()
        risk_counts = {
            "GOOD": sum(1 for r in all_risks if r["category"] == "GOOD"),
            "ATTENDANCE RISK": sum(1 for r in all_risks if r["category"] == "ATTENDANCE RISK"),
            "ACADEMIC RISK": sum(1 for r in all_risks if r["category"] == "ACADEMIC RISK"),
            "HIGH RISK": sum(1 for r in all_risks if r["category"] == "HIGH RISK"),
            "MODERATE PROGRESS": sum(1 for r in all_risks if r["category"] == "MODERATE PROGRESS")
        }

        # Students below attendance threshold
        thresholds = AnalyticsService.get_thresholds()
        below_att_count = sum(1 for r in all_risks if r["attendance_percentage"] < thresholds["attendance_threshold"])

        # Top 5 performers
        top_performers = sorted(all_risks, key=lambda x: x["academic_percentage"], reverse=True)[:5]

        # Department-wise attendance
        departments = Department.query.all()
        dept_attendance = []
        for d in departments:
            dept_students = [s.id for s in d.students]
            if dept_students:
                d_att = Attendance.query.filter(Attendance.student_id.in_(dept_students)).all()
                d_total = len(d_att)
                d_pres = sum(1 for a in d_att if a.status in ("Present", "Late"))
                d_pct = round((d_pres / d_total) * 100, 1) if d_total > 0 else 0.0
            else:
                d_pct = 0.0
            dept_attendance.append({"name": d.name, "code": d.code, "percentage": d_pct})

        # Monthly attendance trends across college
        all_att = Attendance.query.order_by(Attendance.date.asc()).all()
        month_map = {}
        for a in all_att:
            m_key = a.date.strftime("%b %Y")
            if m_key not in month_map:
                month_map[m_key] = {"total": 0, "present": 0}
            month_map[m_key]["total"] += 1
            if a.status in ("Present", "Late"):
                month_map[m_key]["present"] += 1

        monthly_trends = []
        for m_key, counts in month_map.items():
            pct = round((counts["present"] / counts["total"]) * 100, 1) if counts["total"] > 0 else 0.0
            monthly_trends.append({"month": m_key, "percentage": pct, "count": counts["total"]})

        return {
            "total_students": total_students,
            "total_faculty": total_faculty,
            "total_subjects": total_subjects,
            "overall_attendance": overall_attendance,
            "overall_performance": overall_performance,
            "below_att_count": below_att_count,
            "risk_counts": risk_counts,
            "top_performers": top_performers,
            "department_attendance": dept_attendance,
            "monthly_trends": monthly_trends,
            "thresholds": thresholds
        }

analytics_service = AnalyticsService()
