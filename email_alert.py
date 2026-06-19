"""
email_alert.py   (OPTIONAL / ADVANCED FEATURE)
--------------------------------------------------
Sends an email notification whenever integrity changes are detected,
so you find out even if you're not watching the terminal.

SECURITY NOTE FOR BEGINNERS:
Never hard-code your real email password in source code, and never
commit it to GitHub. Gmail/Outlook/etc. let you generate a separate
"App Password" specifically for scripts like this one — use that
instead, and ideally load it from an environment variable rather than
typing it directly into this file:

    import os
    SENDER_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
"""

import smtplib
from email.mime.text import MIMEText

# --- Fill these in with your own details before using this feature ---
SMTP_SERVER = "smtp.gmail.com"      # e.g. smtp.gmail.com, smtp.office365.com
SMTP_PORT = 587                      # 587 = TLS (standard for most providers)
SENDER_EMAIL = "your_email@gmail.com"
SENDER_APP_PASSWORD = "your_app_password"   # use an App Password, NOT your real password
RECEIVER_EMAIL = "receiver_email@gmail.com"


def send_alert_email(changes):
    """
    Build a short, readable email body describing detected changes and
    send it via SMTP.

    Parameters:
        changes (dict): The same dict produced by verifier.compare_hashes(),
                         i.e. {"modified": [...], "deleted": [...], "added": [...]}
    """
    body_lines = ["File Integrity Checker detected the following changes:\n"]

    for path in changes.get("modified", []):
        body_lines.append(f"MODIFIED: {path}")
    for path in changes.get("deleted", []):
        body_lines.append(f"DELETED: {path}")
    for path in changes.get("added", []):
        body_lines.append(f"ADDED: {path}")

    if len(body_lines) == 1:
        body_lines.append("(No changes — this is a test message.)")

    body = "\n".join(body_lines)

    msg = MIMEText(body)
    msg["Subject"] = "⚠ File Integrity Alert"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # upgrade the connection to an encrypted one
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)
        print("[OK] Alert email sent successfully.")
    except Exception as error:
        # We catch broadly here because SMTP can fail in many different
        # ways (wrong password, no internet, server down, etc.) and we
        # just want to report it clearly rather than crash the program.
        print(f"[ERROR] Could not send email: {error}")


# Example of how you would plug this into verifier.log_changes() in main.py:
#
#   from email_alert import send_alert_email
#   changes = compare_hashes(old_hashes, new_hashes)
#   log_changes(changes)
#   if any(changes.values()):
#       send_alert_email(changes)
