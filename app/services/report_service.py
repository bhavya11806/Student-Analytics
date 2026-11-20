import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from flask import current_app
from app import db
from app.models import Student, Subject, Attendance, Mark, AcademicReport, Department, User
from app.services.attendance_service import attendance_service
from app.services.analytics_service import analytics_service
from app.services.s3_service import s3_service

class ReportService:
    @staticmethod
    def _ensure_report_dir():
        reports_dir = current_app.config.get("REPORTS_DIR")
        os.makedirs(reports_dir, exist_ok=True)
        return reports_dir

    @staticmethod
    def generate_student_attendance_pdf(student_id: int, generated_by_user_id: int) -> tuple[str, AcademicReport]:
        """
        Generates a formal, beautifully styled PDF Attendance Report for a student using ReportLab.
        """
        student = db.session.get(Student, student_id)
        if not student:
            raise ValueError("Student not found.")

        reports_dir = ReportService._ensure_report_dir()
        filename = f"attendance_report_{student.roll_no}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(reports_dir, filename)

        summary = attendance_service.get_student_attendance_summary(student_id)
        risk = analytics_service.classify_student_risk(student_id)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1e293b"),
            alignment=1,
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            "SubTitleStyle",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#64748b"),
            alignment=1,
            spaceAfter=15
        )
        section_style = ParagraphStyle(
            "SectionStyle",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#2563eb"),
            spaceBefore=12,
            spaceAfter=6
        )
        normal_style = styles["Normal"]

        story = []

        # Header Banner
        story.append(Paragraph("<b>COLLEGE OF ENGINEERING & TECHNOLOGY</b>", title_style))
        story.append(Paragraph("Cloud-Based Student Attendance & Performance Analytics System", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=15))

        # Student Details Table
        student_info = [
            [Paragraph("<b>Student Name:</b>", normal_style), Paragraph(student.user.name, normal_style),
             Paragraph("<b>Roll Number:</b>", normal_style), Paragraph(student.roll_no, normal_style)],
            [Paragraph("<b>Department:</b>", normal_style), Paragraph(student.department.name if student.department else "N/A", normal_style),
             Paragraph("<b>Course / Semester:</b>", normal_style), Paragraph(f"{student.course} / Sem {student.semester}", normal_style)],
            [Paragraph("<b>Overall Attendance:</b>", normal_style), Paragraph(f"<b>{summary['overall_percentage']}%</b> ({summary['total_present']}/{summary['total_conducted']} classes)", normal_style),
             Paragraph("<b>Risk Status:</b>", normal_style), Paragraph(f"<b>{risk['category']}</b>", normal_style)],
        ]
        info_table = Table(student_info, colWidths=[110, 150, 110, 150])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 15))

        # Subject-wise Attendance Table
        story.append(Paragraph("<b>Subject-wise Attendance Breakdown</b>", section_style))
        sub_headers = ["Code", "Subject Name", "Credits", "Conducted", "Attended", "Absent", "Attendance %"]
        sub_rows = [sub_headers]
        for sub in summary["subject_wise"]:
            sub_rows.append([
                sub["code"],
                sub["name"],
                str(sub["credits"]),
                str(sub["conducted"]),
                str(sub["attended"]),
                str(sub["absent"]),
                f"{sub['percentage']}%"
            ])

        sub_table = Table(sub_rows, colWidths=[65, 180, 50, 60, 55, 55, 65])
        sub_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(sub_table)
        story.append(Spacer(1, 20))

        # Sign-off Block
        sign_block = [
            ["Generated Date: " + datetime.utcnow().strftime("%d-%b-%Y %H:%M UTC"), "", "Authorized Signatory / Faculty Mentor"],
            ["Verification Key: AWS-S3-" + filename[:16], "", "Department Coordinator Stamp"]
        ]
        sign_table = Table(sign_block, colWidths=[200, 120, 200])
        sign_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#64748b")),
            ("LINEABOVE", (2, 0), (2, 0), 1, colors.HexColor("#94a3b8")),
            ("ALIGN", (2, 0), (2, -1), "CENTER"),
        ]))
        story.append(sign_table)

        doc.build(story)

        # Upload to S3 if configured
        s3_key = f"reports/attendance/{filename}"
        s3_url = None
        if s3_service.is_configured():
            success, s3_res = s3_service.upload_file(filepath, s3_key, content_type="application/pdf")
            if success:
                s3_url = s3_service.generate_presigned_url(s3_key)

        file_size = round(os.path.getsize(filepath) / 1024.0, 1)

        report_rec = AcademicReport(
            title=f"Attendance Report - {student.roll_no}",
            report_type="attendance_pdf",
            file_name=filename,
            file_path=filepath,
            s3_key=s3_key if s3_url else None,
            s3_url=s3_url,
            file_size_kb=file_size,
            generated_by=generated_by_user_id
        )
        db.session.add(report_rec)
        db.session.commit()

        return filepath, report_rec

    @staticmethod
    def generate_student_performance_pdf(student_id: int, generated_by_user_id: int) -> tuple[str, AcademicReport]:
        """
        Generates a formal academic performance transcript PDF with marks, grades, and risk analysis.
        """
        student = db.session.get(Student, student_id)
        if not student:
            raise ValueError("Student not found.")

        reports_dir = ReportService._ensure_report_dir()
        filename = f"performance_transcript_{student.roll_no}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(reports_dir, filename)

        acad = analytics_service.get_student_academic_summary(student_id)
        risk = analytics_service.classify_student_risk(student_id)

        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        normal = styles["Normal"]

        story = []
        story.append(Paragraph("<b>COLLEGE OF ENGINEERING & TECHNOLOGY</b>", styles["Heading1"]))
        story.append(Paragraph("Official Academic Performance Transcript", styles["Normal"]))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#6366f1"), spaceAfter=15))

        # Student Details
        student_info = [
            [Paragraph("<b>Student:</b> " + student.user.name, normal), Paragraph("<b>Roll Number:</b> " + student.roll_no, normal)],
            [Paragraph("<b>Course:</b> " + student.course, normal), Paragraph("<b>Semester:</b> " + str(student.semester), normal)],
            [Paragraph("<b>Overall Academic Score:</b> " + f"<b>{acad['overall_percentage']}% ({acad['grade']})</b>", normal),
             Paragraph("<b>Status Classification:</b> " + f"<b>{risk['category']}</b>", normal)]
        ]
        info_t = Table(student_info, colWidths=[260, 260])
        info_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f3ff")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#c7d2fe")),
            ("PADDING", (0, 0), (-1, -1), 6)
        ]))
        story.append(info_t)
        story.append(Spacer(1, 15))

        # Marks Table
        story.append(Paragraph("<b>Examination Scores & Evaluation</b>", styles["Heading2"]))
        headers = ["Subject Code", "Subject Name", "Total Obtained", "Maximum Marks", "Score %", "Grade"]
        rows = [headers]
        for sub in acad["subject_wise_performance"]:
            rows.append([
                sub["code"],
                sub["name"],
                str(sub["total_obtained"]),
                str(sub["total_max"]),
                f"{sub['percentage']}%",
                sub["grade"]
            ])

        marks_t = Table(rows, colWidths=[80, 200, 75, 75, 60, 40])
        marks_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("PADDING", (0, 0), (-1, -1), 5)
        ]))
        story.append(marks_t)
        story.append(Spacer(1, 20))

        doc.build(story)

        s3_key = f"reports/performance/{filename}"
        s3_url = None
        if s3_service.is_configured():
            success, _ = s3_service.upload_file(filepath, s3_key, content_type="application/pdf")
            if success:
                s3_url = s3_service.generate_presigned_url(s3_key)

        file_size = round(os.path.getsize(filepath) / 1024.0, 1)

        report_rec = AcademicReport(
            title=f"Performance Transcript - {student.roll_no}",
            report_type="performance_pdf",
            file_name=filename,
            file_path=filepath,
            s3_key=s3_key if s3_url else None,
            s3_url=s3_url,
            file_size_kb=file_size,
            generated_by=generated_by_user_id
        )
        db.session.add(report_rec)
        db.session.commit()

        return filepath, report_rec

    @staticmethod
    def generate_attendance_excel(department_id: int = None, semester: int = None, generated_by_user_id: int = 1) -> tuple[str, AcademicReport]:
        """
        Generates a comprehensive Excel (.xlsx) Master Attendance Sheet using OpenPyXL with styled headers,
        alternating rows, and risk categorization.
        """
        reports_dir = ReportService._ensure_report_dir()
        filename = f"attendance_master_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(reports_dir, filename)

        wb = Workbook()
        ws = wb.active
        ws.title = "Attendance Summary"

        # Styles
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1")
        )

        # Title Row
        ws.merge_cells("A1:G1")
        ws["A1"] = "COLLEGE OF ENGINEERING & TECHNOLOGY - MASTER ATTENDANCE SHEET"
        ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

        headers = ["Roll Number", "Student Name", "Department", "Semester", "Classes Conducted", "Classes Present", "Attendance %"]
        ws.append([])  # Blank row 2
        ws.append(headers)

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=3, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        query = Student.query
        if department_id:
            query = query.filter_by(department_id=department_id)
        if semester:
            query = query.filter_by(semester=semester)

        students = query.all()
        for row_idx, st in enumerate(students, start=4):
            summary = attendance_service.get_student_attendance_summary(st.id)
            row_data = [
                st.roll_no,
                st.user.name if st.user else "Unknown",
                st.department.name if st.department else "N/A",
                st.semester,
                summary["total_conducted"],
                summary["total_present"],
                f"{summary['overall_percentage']}%"
            ]
            ws.append(row_data)

            # Styling row
            fill = PatternFill(start_color="F8FAFC" if row_idx % 2 == 0 else "FFFFFF", fill_type="solid")
            for col_idx in range(1, len(headers) + 1):
                c = ws.cell(row=row_idx, column=col_idx)
                c.fill = fill
                c.border = thin_border
                if col_idx in (1, 4, 5, 6, 7):
                    c.alignment = Alignment(horizontal="center")

        # Auto-fit column widths
        for col_idx, col in enumerate(ws.columns, start=1):
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        wb.save(filepath)

        s3_key = f"reports/excel/{filename}"
        s3_url = None
        if s3_service.is_configured():
            success, _ = s3_service.upload_file(filepath, s3_key, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            if success:
                s3_url = s3_service.generate_presigned_url(s3_key)

        file_size = round(os.path.getsize(filepath) / 1024.0, 1)

        report_rec = AcademicReport(
            title="College Attendance Master Spreadsheet",
            report_type="attendance_excel",
            file_name=filename,
            file_path=filepath,
            s3_key=s3_key if s3_url else None,
            s3_url=s3_url,
            file_size_kb=file_size,
            generated_by=generated_by_user_id
        )
        db.session.add(report_rec)
        db.session.commit()

        return filepath, report_rec

    @staticmethod
    def generate_performance_excel(department_id: int = None, semester: int = None, generated_by_user_id: int = 1) -> tuple[str, AcademicReport]:
        """
        Generates an Excel (.xlsx) Academic Marks & Risk Analysis workbook.
        """
        reports_dir = ReportService._ensure_report_dir()
        filename = f"academic_performance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(reports_dir, filename)

        wb = Workbook()
        ws = wb.active
        ws.title = "Academic Performance"

        header_fill = PatternFill(start_color="4338CA", end_color="4338CA", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1")
        )

        ws.merge_cells("A1:H1")
        ws["A1"] = "COLLEGE OF ENGINEERING & TECHNOLOGY - ACADEMIC PERFORMANCE & RISK REPORT"
        ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="4338CA")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

        headers = ["Roll Number", "Student Name", "Department", "Semester", "Attendance %", "Marks %", "Grade", "Risk Status"]
        ws.append([])
        ws.append(headers)

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=3, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        risks = analytics_service.get_all_students_risk_list(department_id, semester)
        for row_idx, r in enumerate(risks, start=4):
            ws.append([
                r["roll_no"],
                r["name"],
                r["department"],
                r["semester"],
                f"{r['attendance_percentage']}%",
                f"{r['academic_percentage']}%",
                r["grade"],
                r["category"]
            ])
            fill = PatternFill(start_color="F5F3FF" if row_idx % 2 == 0 else "FFFFFF", fill_type="solid")
            for col_idx in range(1, len(headers) + 1):
                c = ws.cell(row=row_idx, column=col_idx)
                c.fill = fill
                c.border = thin_border
                if col_idx in (1, 4, 5, 6, 7, 8):
                    c.alignment = Alignment(horizontal="center")

        for col_idx, col in enumerate(ws.columns, start=1):
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        wb.save(filepath)

        s3_key = f"reports/excel/{filename}"
        s3_url = None
        if s3_service.is_configured():
            success, _ = s3_service.upload_file(filepath, s3_key, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            if success:
                s3_url = s3_service.generate_presigned_url(s3_key)

        file_size = round(os.path.getsize(filepath) / 1024.0, 1)

        report_rec = AcademicReport(
            title="College Academic Performance & Risk Spreadsheet",
            report_type="performance_excel",
            file_name=filename,
            file_path=filepath,
            s3_key=s3_key if s3_url else None,
            s3_url=s3_url,
            file_size_kb=file_size,
            generated_by=generated_by_user_id
        )
        db.session.add(report_rec)
        db.session.commit()

        return filepath, report_rec

report_service = ReportService()
