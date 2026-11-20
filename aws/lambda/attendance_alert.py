"""
AWS Lambda Function: Automated Student Attendance Check & SNS Notification Dispatcher

Execution Workflow:
1. Scheduled automatically on a daily basis via Amazon EventBridge (e.g., cron(0 12 * * ? *)).
2. Connects securely to Amazon RDS MySQL (or reads from application API).
3. Evaluates overall attendance percentage for each enrolled student:
   Attendance Percentage = (Present Classes / Total Conducted Classes) * 100
4. Flags students falling below the configured threshold (default: 75%).
5. Publishes an emergency attendance alert to an Amazon SNS Topic for multi-channel SMS/Email dispatch.
6. Emits structured monitoring logs to Amazon CloudWatch.
"""

import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

# Configure CloudWatch logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Optional PyMySQL for direct RDS execution in Lambda VPC
try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

def get_db_connection():
    """Establishes private connection to Amazon RDS MySQL instance."""
    host = os.environ.get("DB_HOST", "student-analytics-rds.local")
    user = os.environ.get("DB_USER", "dbadmin")
    password = os.environ.get("DB_PASSWORD", "")
    database = os.environ.get("DB_NAME", "student_analytics")
    port = int(os.environ.get("DB_PORT", 3306))

    if not PYMYSQL_AVAILABLE:
        logger.warning("PyMySQL not packaged in Lambda layer. Using demonstration mode.")
        return None

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

def lambda_handler(event, context):
    logger.info("Initiating scheduled attendance surveillance execution.")
    
    threshold = float(os.environ.get("ATTENDANCE_THRESHOLD", "75.0"))
    topic_arn = os.environ.get("SNS_TOPIC_ARN")
    region = os.environ.get("AWS_REGION", "ap-south-1")

    if not topic_arn:
        logger.error("SNS_TOPIC_ARN environment variable is not configured.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "SNS_TOPIC_ARN is missing."})
        }

    sns_client = boto3.client("sns", region_name=region)
    flagged_students = []

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Query overall attendance per student
                query = """
                    SELECT 
                        s.id AS student_id,
                        s.roll_no,
                        u.name AS student_name,
                        u.email,
                        u.phone,
                        COUNT(a.id) AS total_classes,
                        SUM(CASE WHEN a.status IN ('Present', 'Late') THEN 1 ELSE 0 END) AS present_classes
                    FROM students s
                    JOIN users u ON s.user_id = u.id
                    JOIN attendance a ON s.id = a.student_id
                    WHERE s.account_status = 'Active'
                    GROUP BY s.id, s.roll_no, u.name, u.email, u.phone
                    HAVING total_classes > 0;
                """
                cursor.execute(query)
                results = cursor.fetchall()

                for row in results:
                    total = row["total_classes"]
                    present = row["present_classes"]
                    pct = round((present / total) * 100.0, 2)
                    if pct < threshold:
                        flagged_students.append({
                            "roll_no": row["roll_no"],
                            "name": row["student_name"],
                            "percentage": pct,
                            "email": row["email"],
                            "phone": row["phone"]
                        })
        except Exception as e:
            logger.error(f"RDS query error: {str(e)}")
        finally:
            conn.close()
    else:
        # Standalone mock event data for offline / dry-run testing
        logger.info("Executing dry-run attendance evaluation with test payload.")
        flagged_students = [
            {"roll_no": "CSE2024004", "name": "Rahul Sharma", "percentage": 60.0},
            {"roll_no": "CSE2024008", "name": "Vikram Singh", "percentage": 45.0}
        ]

    # Publish notification messages via Amazon SNS
    dispatched_count = 0
    for st in flagged_students:
        msg_subject = f"URGENT: Low Attendance Warning for {st['roll_no']}"
        msg_body = (
            f"Dear {st['name']} ({st['roll_no']}),\n\n"
            f"Your current attendance stands at {st['percentage']}%, which is below the mandatory "
            f"minimum college requirement of {threshold}%.\n\n"
            f"Please meet your departmental academic coordinator immediately.\n\n"
            f"-- College Student Attendance & Performance Analytics Cloud"
        )
        try:
            sns_client.publish(
                TopicArn=topic_arn,
                Subject=msg_subject[:100],
                Message=msg_body
            )
            dispatched_count += 1
            logger.info(f"SNS Alert published for student {st['roll_no']} ({st['percentage']}%)")
        except ClientError as e:
            logger.error(f"Failed to publish SNS for {st['roll_no']}: {e}")

    summary = {
        "status": "COMPLETED",
        "threshold_evaluated": threshold,
        "flagged_count": len(flagged_students),
        "sns_dispatched_count": dispatched_count
    }
    logger.info(f"Attendance execution summary: {json.dumps(summary)}")

    return {
        "statusCode": 200,
        "body": json.dumps(summary)
    }
