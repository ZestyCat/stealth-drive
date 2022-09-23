import re
from urllib.parse import urlsplit
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def find_emails(text):
    try:
        emails = re.findall(r"[a-z0-9\.\-]+@[a-z0-9\.\-+_]+\.[a-z]+", text, re.I)
        if len(emails):
            return list(set(emails))
        else:
            return None
    except Exception as error:
        print("Could not get email")
        return error

def find_images(obj):
    """ obj may be sting or Requests response object """
    if "Response" in str(type(obj)):
        obj = obj.text
    soup = BeautifulSoup(obj)
    img = soup.find_all("img")
    return [i.attrs["src"] for i in img]

def find_phone(text):
    try:
        numbers = re.findall(r"[0-9]{3}[^0-9a-z]{1,2}?[0-9]{3}[^0-9a-z]{1,2}?[0-9]{4}", text, re.I)
        numbers = [re.sub(r"[^0-9]", "", number) for number in numbers]
        if len(numbers):
            return list(set(numbers))
        else:
            return None
    except Exception as error:
        print("could not get phone number")
        return error

def find_contact_url(obj, base_url=None):
    """ obj may be sting or Requests response object 
        search a page for a "contact" section
    """
    try:
        if "Response" in str(type(obj)):
            obj = obj.text
        soup = BeautifulSoup(obj)
        contact_url = str(soup.find("a", {"href" : re.compile("contact")}).get("href"))
        if not contact_url.startswith("http") and base_url:
            contact_url = urljoin(base_url, contact_url)
        return contact_url
    except AttributeError as error:
        print("no contact url found")
        return None
    except Exception as error:
        print("Could not get contact url")
        return None

def find_phone_and_email(obj):
    """ obj may be sting or Requests response object """
    try:
        if "Response" in str(type(obj)):
            obj = obj.text
        soup = BeautifulSoup(obj)
        body = soup.find("body")
        text = body.get_text(separator=" ")
    except Exception as error:
        print("Could not parse the response or text")
        return error
    try:
        phone = find_phone(text)
    except:
        phone = ""
    try:
        email = find_emails(text)
    except:
        email = ""
    if phone == "" and email == "":
        print("No phone or email found")
    print(phone, email)
    return phone, email
