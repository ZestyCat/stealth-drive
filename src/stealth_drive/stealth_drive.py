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

    def get_proxies(self, https = True, countries = None):
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
