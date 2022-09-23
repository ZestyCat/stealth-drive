import re
from urllib.parse import urlsplit
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def find_emails(obj):
    """ obj may be sting or Requests response object """
    if "Response" in str(type(obj)):
        obj = obj.text
    emails = re.findall(r"[a-z0-9\.\-]+@[a-z0-9\.\-+_]+\.[a-z]+", obj, re.I)
    if len(emails):
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
    numbers = re.findall(r"[0-9]{3}[^0-9a-z]{0,2}?[0-9]{3}[^0-9a-z]{0,2}?[0-9]{4}", obj, re.I)
    numbers = [re.sub(r"[^0-9]", "", number) for number in numbers]
    if len(numbers):
        return numbers
    else:
        return ""

def find_contact_url(obj, base_url=None):
    """ obj may be sting or Requests response object """
    if "Response" in str(type(obj)):
        obj = obj.text
    soup = BeautifulSoup(obj)
    contact_url = str(soup.find("a", {"href" : re.compile("contact")}).get("href"))
    if not contact_url.startswith("http") and base_url:
        contact_url = urljoin(base_url, contact_url)
    return contact_url

def find_phone_and_email(obj):
    """ obj may be sting or Requests response object """
    if "Response" in str(type(obj)):
        obj = obj.text
    soup = BeautifulSoup(obj)
    body = soup.find("body")
    try:
        phone = find_phone(body.text)[0]
    except:
        phone = ""
    try:
        email = find_emails(body.text)[0]
    except:
        email = ""
    return phone, email
