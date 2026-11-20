# Amazon EventBridge: Daily Attendance Check Schedule Setup

Amazon EventBridge invokes the `student-attendance-alert` AWS Lambda function on a recurring daily cron schedule after classes conclude.

---

## 1. Schedule Specification

- **Target Lambda Function:** `student-attendance-alert`
- **Schedule Cron Expression:** `cron(0 12 * * ? *)`
  *(Runs daily at 12:00 UTC / 17:30 IST / 5:30 PM Indian Standard Time)*
- **State:** Enabled
- **Payload:** Static JSON `{ "source": "aws.events.daily_attendance_check" }`

---

## 2. Setup via AWS CLI

### Step 1: Create the EventBridge Rule
```bash
aws events put-rule \
  --name "daily-student-attendance-check" \
  --schedule-expression "cron(0 12 * * ? *)" \
  --state ENABLED \
  --description "Triggers daily automated student attendance surveillance and SNS alerts" \
  --region ap-south-1
```

### Step 2: Grant EventBridge Permission to Invoke the Lambda Function
```bash
aws lambda add-permission \
  --function-name "student-attendance-alert" \
  --statement-id "EventBridgeDailyAttendanceInvoke" \
  --action "lambda:InvokeFunction" \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:ap-south-1:$(aws sts get-caller-identity --query Account --output text):rule/daily-student-attendance-check" \
  --region ap-south-1
```

### Step 3: Attach the Lambda Function as the Target
```bash
aws events put-targets \
  --rule "daily-student-attendance-check" \
  --targets '[
    {
      "Id": "1",
      "Arn": "arn:aws:lambda:ap-south-1:'"$(aws sts get-caller-identity --query Account --output text)"':function:student-attendance-alert",
      "Input": "{\"source\": \"eventbridge.scheduled_attendance_audit\"}"
    }
  ]' \
  --region ap-south-1
```

---

## 3. Setup via AWS Management Console

1. Navigate to **Amazon EventBridge** &rarr; **Rules** &rarr; **Create rule**.
2. **Rule name:** `daily-student-attendance-check`.
3. **Rule type:** Schedule.
4. **Schedule pattern:** Recurring schedule &rarr; Cron-based schedule &rarr; `0 12 * * ? *`.
5. **Target types:** AWS service &rarr; **Lambda function** &rarr; Select `student-attendance-alert`.
6. Review and click **Create rule**.
