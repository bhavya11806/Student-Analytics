from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user

def roles_required(*roles):
    """
    Decorator to restrict view access to specific user roles.
    Example: @roles_required('admin', 'faculty')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                flash("Access denied: You do not have permission to view this resource.", "danger")
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(fn):
    return roles_required("admin")(fn)

def faculty_required(fn):
    return roles_required("faculty", "admin")(fn)

def student_required(fn):
    return roles_required("student")(fn)
