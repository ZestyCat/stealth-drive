import re
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from validate_email import validate_email

def find_emails(obj, is_response=False):
    if is_response:
        obj = obj.text
    emails = re.findall(r"[a-z0-9\.\-]+@[a-z0-9\.\-+_]+\.[a-z]+", obj, re.I)
    emails = [email for email in emails if validate_email(email)]
    if len(emails):
        print(f"Found {len(emails)}: {emails}")
        return emails
    else:
        return ""

def find_images(obj, is_response=False):
    if is_response:
        obj = obj.text
    soup = BeautifulSoup(obj)
    img = soup.find_all("img")
    return [i.attrs["src"] for i in img]
