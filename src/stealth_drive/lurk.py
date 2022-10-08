from collections import deque
from urllib.parse import urlsplit, quote_plus
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import random
import requests
import json
import re
import os

def make_driver(proxy=None, load_images=False):
    options = uc.ChromeOptions()
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    if not load_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    driver = uc.Chrome(options=options, use_subprocess=True)
    input("You have started an Undetected Chromedriver!\nTake a minute to set up ublock origin before scraping.\n")
    return driver

class StealthDriver():
    """ Undetected chromdriver with rotating proxies """
    def __init__(self, proxy=None, free_proxies=False, load_images=False, **kwargs):
        if free_proxies:
            print("getting proxies...")
            self.proxies = self.get_proxies(**kwargs)
        self.init_driver(proxy=proxy, load_images=load_images)

    def init_driver(self, proxy=None, load_images=False):
        if hasattr(self, "driver"):
            self.driver.quit()
        ua = UserAgent()
        userAgent = ua.random
        options = uc.ChromeOptions()
        if not load_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        options.add_argument(f"--user-agent={userAgent}")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
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
    for proxy in proxies:
        try:
            response = requests.get(url, proxies= {"https":proxy}, headers=headers, timeout=timeout)
            return response
        except:
            continue

def spb_get(api_key, url, headers=None, try_requests=True, premium=False):
    """ Try without proxy, try with scrapingbee proxy """
    try:
        if not try_requests:
            raise ValueError
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise ValueError
        return r
    except ValueError:
        if premium:
            proxies = {
                "http": f"http://{api_key}:render_js=False&premium_proxy=True@proxy.scrapingbee.com:8886",
                "https": f"https://{api_key}:render_js=False&premium_proxy=True@proxy.scrapingbee.com:8887"
            }
        else:
            proxies = {
                "http": f"http://{api_key}:render_js=False@proxy.scrapingbee.com:8886",
                "https": f"https://{api_key}:render_js=False@proxy.scrapingbee.com:8887"
            }

        print(proxies)
        r = requests.get(url, proxies=proxies, headers=headers, verify=False)
        return r

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

def get_until_got(n_tries, logfile=None): # nice decorator to try get request n times until you get a 200, and optional logging
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(0, n_tries):
                try:
                    r = func(*args, **kwargs)
                    if r.status_code != 200:
                        raise ValueError
                    if logfile:
                        text = f"Got {args[1]} after {i} attempts.\n"
                        with open(logfile, "a") as f:
                            f.write(text)
                    return r
                except ValueError:
                    if logfile:
                        text = f"Failed to get {args[1]} after {i} attempts with message {r.text}\nfor reason {r.reason}\n"
                        with open(logfile, "a") as f:
                            f.write(text)
                    continue
        return wrapper
    return decorator

class InstagramProfile():
    def __init__(self, driver, username, posts=10):
        self.driver = driver
        self.posts = self.get_posts(username, n=posts)
        self.data = self.get_basic_info(username)
        self.data["posts"] = self.posts

    def get_basic_info(self, username):
        print(f"getting profile data for {username}")
        self.url = f"https://pixwox.com/profile/{username}/"
        self.driver.get(self.url)
        soup = BeautifulSoup(self.driver.page_source)
        n_posts = soup.select_one("div[class='item item_followers'] > div[class='num']").text.replace(",", "").strip()
        n_followers = soup.select_one("div[class='item item_followers'] > div[class='num']").text.replace(",", "").strip()
        n_following = soup.select_one("div[class='item item_following'] > div[class='num']").text.replace(",", "").strip()
        n_posts = re.sub(r"\.\dk", "500", n_posts)
        n_posts = re.sub("k", "000", n_posts)
        n_followers = re.sub(r"\.\dk", "500", n_followers)
        n_followers = re.sub("k", "000", n_followers)
        n_following = re.sub(r"\.\dk", "500", n_following)        
        n_following = re.sub("k", "000", n_following)        
        try:
            title = soup.select_one("h1[class='fullname']").text
            bio = soup.select_one("div[class='sum']").text
        except AttributeError:
            title = ""
            bio = ""
        data = {
            "username": username,
            "title": title, 
            "bio": bio,
            "n_posts": int(n_posts),
            "n_followers": int(n_followers),
            "n_following": int(n_following)
        }
        return data

    def get_posts(self, username, n=10, get_comments=True):
        print(f"getting posts for {username}")
        self.driver.get(f"https://pixwox.com/profile/{username}")
        soup = BeautifulSoup(self.driver.page_source)
        try:
            n_posts = int(soup.select_one("div[class='item item_posts'] > div[class='num']").text.replace(",", "").strip())
            if n_posts == 0:
                return []
            if soup.select_one("div[class='notice'] > div[class='txt']"):
                return []
        except AttributeError:
            print("Page not found!")
        atags = soup.select("a[class='cover_link']")
        hrefs = [a.attrs["href"] for a in atags]
        links = [urljoin("https://pixwox.com", href) for href in hrefs]
        posts = []
        for i, link in enumerate(links):
            if i >= n:
                break
            try:
                self.driver.get(link)
            except TimeoutException as e:
                print(e)
                continue # if timeout
            post = {
                "post": link,
                "likes": 0,
                "caption": "",
                "media": "",
                "mentions": [],
                "hashtags": [],
                "comments": []
            }
            soup = BeautifulSoup(self.driver.page_source)
            wrapper = soup.select_one("div[class='view_w']")
            post["likes"] = soup.select_one("div[class='count_item count_item_like cf'] > span[class='num']").text
            if post["likes"] == 0:
                post["likes"] = "NA" # Viewing likes on some posts is disabled
            post["caption"] = wrapper.select_one("img").attrs["alt"]
            post["media"] = wrapper.select_one("a").attrs["href"]
            post["mentions"] = re.findall(r"@\w+", post["caption"])
            post["hashtags"] = re.findall(r"#\w+", post["caption"])
            if get_comments:
                try:
                    comments = soup.select("div[class=comment_w]")
                    for c in comments:
                        comment = {
                            "username": c.select_one("div[class='username'] > a").text.replace("@", ""),
                            "comment": c.select_one("div[class='sum']").text
                        }
                        post["comments"].append(comment)
                except:
                    pass
            posts.append(post)
        return posts

class InstagramInfluencer(InstagramProfile):
    def __init__(self, driver, username, session_id, apify_api_key, posts=10, follower_count=100):
        super().__init__(driver, username, posts=posts)
        self.get_followers(username, apify_api_key, session_id, n=follower_count)
        self.data["followers"] = self.followers
        self.get_audience_posts(n=posts)

    def get_followers(self, username, apify_api_key, session_id,  n=100):
        print(f"getting followers for {username}")
        url = f"https://instagram.com/{username}"
        json = {
            "includeFollowers": True,
            "includeFollowing": False,
            "maxItems": n,
            "proxy": {
                "useApifyProxy": False
            },
            "sessionid": session_id,
            "startUrls": [{"url": url}]
            
        }
        requests.post(f"https://api.apify.com/v2/acts/alexey~instagram-audience-profile-follows/run-sync?token={apify_api_key}", json=json)
        followers = requests.get(f"https://api.apify.com/v2/acts/alexey~instagram-audience-profile-follows/runs/last/dataset/items?token={apify_api_key}")
        self.followers = followers.json()
        if len(self.followers) < n:
            print("Your instagram account was banned!")
            raise ValueError

    def get_following(self, username, apify_api_key, session_id,  n=100):
        print(f"getting following for {username}")
        url = f"https://instagram.com/{username}"
        json = {
            "includeFollowers": False,
            "includeFollowing": True,
            "maxItems": n,
            "proxy": {
                "useApifyProxy": False
            },
            "sessionid": session_id,
            "startUrls": [{"url": url}]
            
        }
        requests.post(f"https://api.apify.com/v2/acts/alexey~instagram-audience-profile-follows/run-sync?token={apify_api_key}", json=json)
        following = requests.get(f"https://api.apify.com/v2/acts/alexey~instagram-audience-profile-follows/runs/last/dataset/items?token={apify_api_key}")
        self.following = following.json()
        if len(self.following) < n:
            print("Your instagram account was banned!")
            raise ValueError

    def get_audience_posts(self, n=10):
        for i, follower in enumerate(self.data["followers"]):
            print(f"getting profile data and posts for follower {i} of {enumerate(self.data['followers'])}")
            username = follower["username"]
            basic_info = super().get_basic_info(username)
            posts = super().get_posts(username, n=n, get_comments=False)
            self.data["followers"][i]["posts"] = posts
            self.data["followers"][i]["n_followers"] = basic_info["n_followers"]
            self.data["followers"][i]["n_following"] = basic_info["n_following"] 
