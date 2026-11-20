from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models import Department, Student
from app.utils.decorators import faculty_required
from app.services.analytics_service import analytics_service

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

@analytics_bp.route("/overview")
@login_required
@faculty_required
def overview():
    stats = analytics_service.get_college_analytics()
    departments = Department.query.all()
    return render_template("analytics.html", stats=stats, departments=departments)

@analytics_bp.route("/risk")
@login_required
@faculty_required
def risk_analysis():
    category = request.args.get("category")
    dept_id = request.args.get("department_id", type=int)
    semester = request.args.get("semester", type=int)

    all_risks = analytics_service.get_all_students_risk_list(dept_id, semester)

    if category:
        all_risks = [r for r in all_risks if r["category"] == category]

    departments = Department.query.all()
    thresholds = analytics_service.get_thresholds()

    return render_template(
        "risk_analysis.html",
        risks=all_risks,
        departments=departments,
        thresholds=thresholds,
        selected_category=category,
        selected_dept=dept_id,
        selected_sem=semester
    )

# ----------------- Chart.js JSON API Endpoints -----------------
@analytics_bp.route("/api/summary")
@login_required
def api_summary():
    stats = analytics_service.get_college_analytics()
    return jsonify({
        "overall_attendance": stats["overall_attendance"],
        "overall_performance": stats["overall_performance"],
        "total_students": stats["total_students"],
        "total_faculty": stats["total_faculty"],
        "below_att_count": stats["below_att_count"],
        "risk_counts": stats["risk_counts"]
    })

@analytics_bp.route("/api/monthly-trends")
@login_required
def api_monthly_trends():
    stats = analytics_service.get_college_analytics()
    return jsonify(stats["monthly_trends"])

@analytics_bp.route("/api/department-comparison")
@login_required
def api_dept_comparison():
    stats = analytics_service.get_college_analytics()
    return jsonify(stats["department_attendance"])

@analytics_bp.route("/api/risk-distribution")
@login_required
def api_risk_distribution():
    stats = analytics_service.get_college_analytics()
    return jsonify(stats["risk_counts"])
