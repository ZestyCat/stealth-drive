import re
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from validate_email import validate_email

def find_emails(obj):
    """ obj may be sting or Requests response object """
    if "Response" in str(type(obj)):
        obj = obj.text
    emails = re.findall(r"[a-z0-9\.\-]+@[a-z0-9\.\-+_]+\.[a-z]+", obj, re.I)
    emails = [email for email in emails if validate_email(email)]
    if len(emails):
        print(f"Found {len(emails)}: {emails}")
        return emails
    else:
        return ""

def find_images(obj):
    """ obj may be sting or Requests response object """
    if "Response" in str(type(obj)):
        obj = obj.text
    soup = BeautifulSoup(obj)
    img = soup.find_all("img")
    return [i.attrs["src"] for i in img]

def find_phone(obj):
    """ obj may be sting or Requests response object """
    if "Response" in str(type(obj)):
        obj = obj.text
    numbers = re.findall(r"1{0, 1}.*?[0-9]{3}.*?[0-9]{3}.*?[0-9]{4}", obj, re.I)
    if len(numbers):
        print(f"Found {len(numbers)}: {numbers}")
        return numbers
    else:
        return ""
