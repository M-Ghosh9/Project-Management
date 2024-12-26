from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()
scheduler = BackgroundScheduler()
scheduler.start()

def send_email(recipient, subject, body):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    if not all([sender, password]):
        raise ValueError("Email credentials not configured")

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")

def schedule_reminders(email, message, remind_time):
    scheduler.add_job(send_email, "date", run_date=remind_time, args=[email, "Project Reminder", message])
