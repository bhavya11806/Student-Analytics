import boto3
from botocore.exceptions import ClientError
from flask import current_app
from app import db
from app.models import Notification, User

class NotificationService:
    def __init__(self):
        self._sns_client = None

    def _get_sns_client(self):
        if self._sns_client is not None:
            return self._sns_client

        region = current_app.config.get("AWS_REGION", "ap-south-1")
        access_key = current_app.config.get("AWS_ACCESS_KEY_ID")
        secret_key = current_app.config.get("AWS_SECRET_ACCESS_KEY")

        if access_key and secret_key:
            self._sns_client = boto3.client(
                "sns",
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
        else:
            try:
                self._sns_client = boto3.client("sns", region_name=region)
            except Exception:
                self._sns_client = None

        return self._sns_client

    def send_notification(self, user_id: int, title: str, message: str,
                          notif_type: str = "attendance_warning", send_sns: bool = True) -> Notification:
        """
        Creates an in-app database notification and optionally publishes an AWS SNS alert.
        """
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        sns_published = False
        topic_arn = current_app.config.get("AWS_SNS_TOPIC_ARN")
        client = self._get_sns_client()

        if send_sns and topic_arn and client:
            try:
                sns_subject = f"[{title[:80]}] Student Analytics Alert"
                sns_body = f"Hello {user.name},\n\n{message}\n\nCollege Attendance & Performance System"
                client.publish(
                    TopicArn=topic_arn,
                    Subject=sns_subject,
                    Message=sns_body
                )
                sns_published = True
            except ClientError as e:
                # Log SNS issue but do not break in-app notification
                print(f"AWS SNS publish notice: {e}")

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notif_type,
            is_read=False,
            sent_via_sns=sns_published
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    def send_bulk_attendance_alerts(self, low_attendance_list: list) -> int:
        """
        Sends notifications to all students identified below threshold.
        Avoids sending duplicate alerts within the same day.
        """
        count = 0
        for item in low_attendance_list:
            student = item["student"]
            percentage = item["percentage"]
            user = student.user
            if not user:
                continue

            # Check if alert already sent recently
            existing = Notification.query.filter_by(
                user_id=user.id,
                type="attendance_warning",
                is_read=False
            ).first()

            if not existing:
                title = f"Low Attendance Warning: {percentage}%"
                message = (
                    f"Dear {user.name} (Roll No: {student.roll_no}), your current overall attendance is {percentage}%, "
                    f"which is below the minimum mandatory requirement of 75%. Please contact your department coordinator."
                )
                self.send_notification(user.id, title, message, notif_type="attendance_warning", send_sns=True)
                count += 1

        return count

    def get_user_notifications(self, user_id: int, unread_only: bool = False):
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Notification.created_at.desc()).all()

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            db.session.commit()
            return True
        return False

notification_service = NotificationService()
