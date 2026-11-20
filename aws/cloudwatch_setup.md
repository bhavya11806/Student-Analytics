# Amazon CloudWatch Monitoring & Alarm Setup

This guide details how to monitor application logs, Lambda executions, and set up automated CloudWatch Alarms for the Student Analytics Cloud platform.

---

## 1. Amazon CloudWatch Log Groups

1. **Flask EC2 Application Logs:**
   - Log Group: `/aws/ec2/student-analytics`
   - Log Stream: `gunicorn-access` and `gunicorn-error`
   - Retention: 30 days

2. **AWS Lambda Attendance Alert Logs:**
   - Log Group: `/aws/lambda/student-attendance-alert`
   - Retention: 14 days

---

## 2. CloudWatch Metric Alarms

### Alarm 1: Lambda Execution Errors
Triggers an alert when attendance check fails due to database timeouts or SNS publishing errors.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "student-analytics-lambda-errors" \
  --alarm-description "Alerts when the attendance alert Lambda function encounters errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --dimensions Name=FunctionName,Value=student-attendance-alert \
  --evaluation-periods 1 \
  --alarm-actions "arn:aws:sns:ap-south-1:123456789012:admin-system-alarms" \
  --region ap-south-1
```

### Alarm 2: EC2 High CPU Utilization
Triggers when EC2 server load exceeds 80% for 2 consecutive evaluation periods (10 minutes).

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "student-analytics-ec2-high-cpu" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-0123456789abcdef0 \
  --evaluation-periods 2 \
  --alarm-actions "arn:aws:sns:ap-south-1:123456789012:admin-system-alarms" \
  --region ap-south-1
```
