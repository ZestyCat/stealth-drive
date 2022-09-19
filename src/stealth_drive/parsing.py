import re
from validate_email import validate_email

def find_emails(text):
    emails = re.findall(r"[a-z0-9\.\-]+@[a-z0-9\.\-+_]+\.[a-z]+", text, re.I)
    emails = [email for email in emails if validate_email(email)]
    if len(emails):
        print(f"Found {len(emails)}: {emails}")
        return emails
    else:
        return ""
