from collections import deque
from urllib.parse import urlsplit, quote_plus
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import random
import requests

class StealthDriver():
    """ Undetected chromdriver with rotating proxies """
    def __init__(self, **kwargs):
        print("getting proxies...")
        self.proxies = self.get_proxies(**kwargs)
    
    def init_driver(self, proxy=None):
        if hasattr(self, "driver"):
            self.driver.quit()
        ua = UserAgent()
        userAgent = ua.random
        options = uc.ChromeOptions()
        options.add_argument(f"--user-agent={userAgent}")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        options.add_argument("--disable-javascript")
        self.driver = uc.Chrome(options=options, use_subprocess=True)

    def get_proxies(self, https=True, countries=None):
        url = "https://free-proxy-list.net/"
        html = requests.get(url).content
        soup = BeautifulSoup(html, features="lxml")
        rows = soup.find_all("table")[0].find_all("tr")
        table_data = []
        for row in rows:
            data = [td.text for td in row]
            if https:
                data = [d for d in data if data[6] == "yes"]
            if countries:
                data = [d for d in data if \
                        data[2] in countries or data[3] in countries]
            if len(data) != 0:
                table_data.append(data)
        return [f"{row[0]}:{str(row[1])}" for row in table_data]

    def get(self, url, callback=None, **kwargs):
        if not hasattr(self, "driver"):
            self.init_driver()
        self.driver.get(url)
        if callback:
            try:
                callback(self.driver, **kwargs)
            except:
                raise Exception

    def proxy_get(self, url, callback=None, **kwargs):
        while True:
            try:
                p = random.randint(0, len(self.proxies) - 1)
                self.init_driver(self.proxies[p])
                self.driver.get(url)
                print(f"using proxy {self.proxies[p]}.")
                if callback:
                    try:
                        callback(self.driver, **kwargs)
                        break
                    except:
                        raise Exception
                break
            except:
                print("rotating to another proxy...")
                self.driver.quit()

def get_proxies(https = True, countries = None):
    url = "https://free-proxy-list.net/"
    html = requests.get(url).content
    soup = BeautifulSoup(html, features="lxml")
    rows = soup.find_all("table")[0].find_all("tr")
    table_data = []
    for row in rows:
        data = [td.text for td in row]
        if https:
            data = [d for d in data if data[6] == "yes"]
        if countries:
            data = [d for d in data if \
                    data[2] in countries or data[3] in countries]
        if len(data) != 0:
            table_data.append(data)
    return [f"{row[0]}:{str(row[1])}" for row in table_data]


def proxy_get(proxies, url, headers=None, timeout=3):
    """ Simple free proxy rotation for free proxy lists """
    """ for paid proxy lists use spb_elevate """
    while True:
        try:
            p = random.randint(0, len(proxies) - 1)
            print(proxies[p])
            response = requests.get(url, proxies= {"https":proxies[p]}, headers=headers, timeout=timeout)
            print(f"using proxy {proxies[p]}.")
            break
        except:
            print("rotating to another proxy...")
            continue
    return response

def spb_get(url, api_key, premium=False):
    """ Try without proxy, then try with scrapingbee proxy """
    try:
        print("trying to get {} without proxy".format(url))
        r = requests.get(url)
        if r.status_code > 400:
            raise Exception
        return r
    except:
        print("trying to get {} with proxy".format(url))
        try:
            if premium:
                p = "&premium_proxy=True"
            else:
                p = ""
            proxies = {
                "http": f"http://{api_key}:render_js=False&{p}@proxy.scrapingbee.com:8886",
                "https": f"https://{api_key}:render_js=False&{p}@proxy.scrapingbee.com:8887"
            }
            r = requests.get(url, proxies=proxies)
            return r
        except Exception as error:
            print("could not get url {}".format(url))
            return error

def spb_google(client, query, render_js="False"):
    query = quote_plus(query)
    google = "https://www.google.com/search?client=firefox-b-1-d&q="
    r = client.get(google+query,
        {
            "custom_google" : "True",
            "render_js" : render_js,
        }
    )  
    return r

def crawl(start_url, proxy=False, proxies=None, callback=None, **kwargs):
    """Generator function does callback on response text"""
    new_urls = deque([start_url])
    processed_urls = set()

    while len(new_urls):
        url = new_urls.popleft()
        processed_urls.add(url)
        parts = urlsplit(url)
        base_url = f"{parts.scheme}://{parts.netloc}"
        
        print(f"processing {url}")
        try:
            if proxy:
                response = proxy_get(proxies, url)
            else:
                response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            continue

        soup = BeautifulSoup(response.text)

        for a in soup.find_all("a"):
            link = a.attrs["href"] if "href" in a.attrs else ""
            if link.startswith("/"):
                link = base_url + link
            if link.startswith("http") and \
                    base_url in link and not \
                    link in new_urls and not \
                    link in processed_urls:
                        new_urls.append(link)

        if callback:
            yield callback(response, **kwargs)
        else:
            yield response
