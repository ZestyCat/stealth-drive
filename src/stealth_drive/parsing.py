# source: webscraping.pro

import requests
import requests.exceptions
import re
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urlsplit

new_urls = deque(["https://webscraping.pro"])
processes_urls = set()
emails = set()

while len(new_urls):
    url = new_urls.popleft()
    processes_urls.add(url)

    parts = urlsplit(url)
    base_url = f"{parts.scheme}://{parts.netloc}"
    path = url[:url.rfind("/") + 1] if "/" in parts.path else url

    print(f"Processing {url}")
    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        continue

    new_emails = re.findall(r"[a-z0-9\.\-]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I)
    emails.update(new_emails)
    print(f"Emails: {emails}")
    
    soup = BeautifulSoup(response.text)

    for a in soup.find_all("a"):
        link = a.attrs["href"] if "href" in a.attrs else ""
        if link.startswith("/"):
            link = base_url + link
        if link.startswith("http") and \
                base_url in link and not \
                link in new_urls and not \
                link in processes_urls:
            new_urls.append(link)
