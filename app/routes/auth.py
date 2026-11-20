from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Student, Faculty
from app.services.notification_service import notification_service
from app.utils.validators import validate_email_format, validate_password_strength

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif current_user.role == "faculty":
            return redirect(url_for("faculty.dashboard"))
        else:
            return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if not email or not password:
            flash("Please enter both email and password.", "warning")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html")

        if not user.active:
            flash("Your account has been deactivated. Please contact the administrator.", "danger")
            return render_template("login.html")

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.name}!", "success")

        # Redirect to appropriate dashboard
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)

        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif user.role == "faculty":
            return redirect(url_for("faculty.dashboard"))
        else:
            return redirect(url_for("student.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been securely logged out.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_info":
            phone = request.form.get("phone", "").strip()
            current_user.phone = phone
            db.session.commit()
            flash("Profile contact information updated.", "success")
        elif action == "change_password":
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")

            if not current_user.check_password(current_pw):
                flash("Current password entered is incorrect.", "danger")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "danger")
            else:
                valid, msg = validate_password_strength(new_pw)
                if not valid:
                    flash(msg, "warning")
                else:
                    current_user.set_password(new_pw)
                    db.session.commit()
                    flash("Password successfully changed.", "success")

        return redirect(url_for("auth.profile"))

    # Load details
    student = Student.query.filter_by(user_id=current_user.id).first() if current_user.role == "student" else None
    faculty = Faculty.query.filter_by(user_id=current_user.id).first() if current_user.role == "faculty" else None
    notifications = notification_service.get_user_notifications(current_user.id)

    return render_template("profile.html", student=student, faculty=faculty, notifications=notifications)

@auth_bp.route("/api/notifications/mark-read/<int:notif_id>", methods=["POST"])
@login_required
def mark_notification_read(notif_id):
    success = notification_service.mark_as_read(notif_id, current_user.id)
    return jsonify({"success": success})
