from app.services.attendance_service import attendance_service, AttendanceService
from app.services.analytics_service import analytics_service, AnalyticsService
from app.services.notification_service import notification_service, NotificationService
from app.services.report_service import report_service, ReportService
from app.services.s3_service import s3_service, S3Service

__all__ = [
    "attendance_service",
    "AttendanceService",
    "analytics_service",
    "AnalyticsService",
    "notification_service",
    "NotificationService",
    "report_service",
    "ReportService",
    "s3_service",
    "S3Service"
]
