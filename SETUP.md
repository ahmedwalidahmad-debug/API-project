# SETUP GUIDE — Google Sheets API Project

## Step 1 — Install dependencies
```
pip install -r requirements.txt
```

---

## Step 2 — Get your credentials.json from Google

1. Go to: https://console.cloud.google.com/
2. Create a new project (or use an existing one)
3. Enable **Google Sheets API**:
   - Search "Google Sheets API" → Enable
4. Create credentials:
   - Go to APIs & Services → Credentials
   - Click "Create Credentials" → OAuth 2.0 Client ID
   - Application type: **Desktop App**
   - Download the JSON file
   - Rename it to `credentials.json`
   - Put it in the same folder as `sheets_manager.py`

---

## Step 3 — Create your Google Sheet

1. Go to https://sheets.google.com
2. Create a new spreadsheet
3. Rename the first sheet tab to: `Registrations`
4. Copy the Spreadsheet ID from the URL:
   - URL looks like: `https://docs.google.com/spreadsheets/d/YOUR_ID_HERE/edit`
   - Copy `YOUR_ID_HERE`
5. Open `sheets_manager.py` and paste it here:
   ```python
   SPREADSHEET_ID = "paste_your_id_here"
   ```

---

## Step 4 — (Optional) Email Setup

If you want emails to work:
1. Go to your Google Account → Security → App Passwords
2. Create an App Password for Gmail
3. In `sheets_manager.py`, update:
   ```python
   EMAIL_SENDER   = "your_email@gmail.com"
   EMAIL_PASSWORD = "your_app_password"
   ```

---

## Step 5 — Run the project
```
python sheets_manager.py
```

First run will open a browser window to authorize access.
After that, `token.json` is saved and won't ask again.

---

## What the project does

| Feature | Description |
|---|---|
| Google Sheets API | Read, write, update data in a real spreadsheet |
| JSON | All API responses handled as JSON; exports a `students_report.json` |
| Email (SMTP) | Sends confirmation email to each registered student |
| Auto ID | Generates student IDs like STU-001, STU-002 automatically |
