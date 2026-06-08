"""
====================================================
  Student Registration System - Google Sheets API
  Uses: Google Sheets API + Gmail API + JSON
====================================================
  HOW TO RUN:
  1. pip install -r requirements.txt
  2. Follow SETUP.md to get your credentials.json
  3. python sheets_manager.py
====================================================
"""

import json
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# PASTE YOUR SPREADSHEET ID HERE (from the URL)
# e.g. https://docs.google.com/spreadsheets/d/YOUR_ID_HERE/edit
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"

SHEET_NAME = "Registrations"

# Email config (Gmail SMTP)
EMAIL_SENDER    = "your_email@gmail.com"
EMAIL_PASSWORD  = "your_app_password"   # Use Gmail App Password, not your real password


# ─────────────────────────────────────────────
# GOOGLE SHEETS AUTH
# ─────────────────────────────────────────────
def get_sheets_service():
    """Authenticate and return Google Sheets API service."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            json.dump(json.loads(creds.to_json()), token)

    return build("sheets", "v4", credentials=creds)


# ─────────────────────────────────────────────
# SHEET OPERATIONS
# ─────────────────────────────────────────────
def create_headers(service):
    """Create header row if sheet is empty."""
    headers = [["ID", "Name", "Email", "Course", "Level", "Registration Date", "Status"]]
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="RAW",
        body={"values": headers},
    ).execute()
    print("✅ Headers created.")


def add_student(service, student: dict) -> str:
    """
    Add a new student registration to the sheet.
    student = {
        "name": "Ahmed Ali",
        "email": "ahmed@example.com",
        "course": "Data Science",
        "level": "beginner"
    }
    Returns the assigned student ID.
    """
    # Get current rows to generate next ID
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:A",
    ).execute()

    rows = result.get("values", [])
    next_id = f"STU-{len(rows):03d}"  # e.g. STU-001, STU-002

    row = [
        next_id,
        student["name"],
        student["email"],
        student["course"],
        student["level"],
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Active",
    ]

    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

    print(f"✅ Student added: {student['name']} → ID: {next_id}")
    return next_id


def get_all_students(service) -> list[dict]:
    """Read all students from the sheet and return as list of dicts."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1:G1000",
    ).execute()

    rows = result.get("values", [])
    if len(rows) < 2:
        return []

    headers = rows[0]
    students = []
    for row in rows[1:]:
        # Pad row in case some cells are empty
        padded = row + [""] * (len(headers) - len(row))
        students.append(dict(zip(headers, padded)))

    return students


def get_student_by_id(service, student_id: str) -> dict | None:
    """Find a student by ID."""
    students = get_all_students(service)
    for s in students:
        if s.get("ID") == student_id:
            return s
    return None


def update_student_status(service, student_id: str, new_status: str):
    """Update the Status column for a specific student."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:A",
    ).execute()

    ids = result.get("values", [])
    for i, row in enumerate(ids):
        if row and row[0] == student_id:
            row_number = i + 1  # Sheets rows are 1-indexed
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!G{row_number}",
                valueInputOption="RAW",
                body={"values": [[new_status]]},
            ).execute()
            print(f"✅ Updated {student_id} status → {new_status}")
            return

    print(f"❌ Student {student_id} not found.")


# ─────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────
def send_confirmation_email(student: dict, student_id: str):
    """Send a confirmation email to the newly registered student."""
    if EMAIL_SENDER == "your_email@gmail.com":
        print("⚠️  Email skipped — add your Gmail credentials in the config section.")
        return

    subject = f"Welcome to Kayfa Academy – Registration Confirmed ({student_id})"
    body = f"""
Hi {student['name']},

Your registration has been confirmed! 🎉

Details:
- Student ID : {student_id}
- Course     : {student['course']}
- Level      : {student['level']}
- Date       : {datetime.now().strftime('%Y-%m-%d')}

We'll be in touch with your learning plan soon.

Best,
Kayfa Academy Team
"""

    msg = MIMEMultipart()
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = student["email"]
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, student["email"], msg.as_string())
        print(f"📧 Confirmation email sent to {student['email']}")
    except Exception as e:
        print(f"❌ Email failed: {e}")


# ─────────────────────────────────────────────
# SAVE JSON REPORT
# ─────────────────────────────────────────────
def export_to_json(service, filename: str = "students_report.json"):
    """Export all students from the sheet to a local JSON file."""
    students = get_all_students(service)
    report = {
        "exported_at": datetime.now().isoformat(),
        "total_students": len(students),
        "students": students,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"📄 Exported {len(students)} students → {filename}")
    return report


# ─────────────────────────────────────────────
# MAIN DEMO
# ─────────────────────────────────────────────
def main():
    print("🚀 Connecting to Google Sheets API...")
    service = get_sheets_service()

    # Step 1: Create headers
    create_headers(service)

    # Step 2: Register new students
    students_to_add = [
        {"name": "Ahmed Ali",    "email": "ahmed@example.com",  "course": "Data Science",      "level": "beginner"},
        {"name": "Sara Mohamed", "email": "sara@example.com",   "course": "Machine Learning",  "level": "intermediate"},
        {"name": "Omar Hassan",  "email": "omar@example.com",   "course": "Python Basics",     "level": "beginner"},
    ]

    for student in students_to_add:
        student_id = add_student(service, student)
        send_confirmation_email(student, student_id)

    # Step 3: Read all students
    print("\n📋 All registered students:")
    all_students = get_all_students(service)
    for s in all_students:
        print(f"  {s.get('ID')} | {s.get('Name')} | {s.get('Course')} | {s.get('Status')}")

    # Step 4: Update a student status
    update_student_status(service, "STU-001", "Graduated")

    # Step 5: Export to JSON
    export_to_json(service)

    print("\n✅ All done!")


if __name__ == "__main__":
    main()
