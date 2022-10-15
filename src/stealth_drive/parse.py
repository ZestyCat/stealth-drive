import re
from urllib.parse import urlsplit
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def find_email(text, multi=False):
    emails = re.findall(r"[a-z0-9\.\-]+@[a-z0-9\.\-+_]+\.[a-z]+", text, re.I)
    emails = [email for email in emails if not re.match(r"(\.jpg)|(\.png)|(\.gif)|(\.svg)", email)]
    if len(emails):
        if multi:
            return list(set(emails))
        if not multi:
            return emails[0]
    else:
        return ""

def find_facebook(text, multi=False):
    fb = re.findall(r"facebook\.com/[a-z0-9_\-]+", text, re.I)
    if len(fb):
        if multi:
            return list(set(fb))
        if not multi:
            return fb[0]
    else:
        return ""

def find_instagram(text, multi=False):
    ig = re.findall(r"instagram\.com/[a-z0-9_\-]+", text, re.I)
    if len(ig):
        if multi:
            return list(set(ig))
        if not multi:
            return ig[0]
    else:
        return ""

def find_twitter(text, multi=False):
    t = re.findall(r"twitter\.com/[a-z0-9_\-]+", text, re.I)
    if len(t):
        if multi:
            return list(set(t))
        if not multi:
            return t[0]
    else:
        return ""

def find_contacts(text):
    return {
        "email" : find_email(text),
        "facebook" : find_facebook(text),
        "instagram" : find_instagram(text),
        "twitter" : find_twitter(text)
    }

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
            return ""
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
        contact_url = str(soup.find("a", {"href" : re.compile(r".*contact.*")}).get("href"))
        if not contact_url.startswith("http") and base_url:
            contact_url = urljoin(base_url, contact_url)
        return contact_url
    except AttributeError as error:
        print(error)
        print("no contact url found")
        return error
    except Exception as error:
        print("Could not get contact url")
        return error

def find_phone_and_email(obj):
    """ obj may be sting or Requests response object """
    try:
        if "Response" in str(type(obj)):
            obj = obj.text
        soup = BeautifulSoup(obj)
        text = soup.find("body").get_text(separator=" ")
    except Exception as error:
        print("Could not parse the response or text")
        return ("", "")
    try:
        phone = find_phone(text)[0]
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

def multiple_replace(text, dict):
    regex = re.compile("(\b%s\b)" % "|".join(map(re.escape, dict.keys())))
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 
