from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import googleapiclient.discovery
import requests

from urllib.parse import urlsplit, quote_plus, urljoin
from bs4 import BeautifulSoup
import re

import os
import time
import random


# Selenium functions
def make_driver(proxy=None, load_images=False, config=True):
    options = uc.ChromeOptions()
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    if not load_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    driver = uc.Chrome(options=options, use_subprocess=True)
    if config:
        input("You have started an Undetected Chromedriver!\nTake a minute to configure the browser before scraping.\n") # Install ublock origin or other plugins
    return driver

def fill_form(driver, text, element, by = By.ID, timeout=10, human=False):
    input = WebDriverWait(driver, timeout).until( \
        EC.presence_of_element_located((by, element)))
    input.clear()
    if human: # Imitate human behavior)
        time.sleep(random.uniform(0.3, 1))
        for letter in text:
            input.send_keys(letter)
            time.sleep(random.uniform(0.1, 0.75))
    else:
        input.send_keys(text)
   
def click_item(driver, element, by = By.ID, timeout=10, multi=False):
    WebDriverWait(driver, timeout).until( \
        EC.element_to_be_clickable((by, element)))
    if multi:
        btn = driver.find_elements(by, element)
        for b in btn:
            driver.execute_script("arguments[0].click();", b)
    else:
        btn = driver.find_element(by, element)
        driver.execute_script("arguments[0].click();", btn)
    
def get_element_text(driver, element, by = By.ID, timeout=10):
    WebDriverWait(driver, timeout).until( \
        EC.presence_of_element_located((by, element)))
    ele = driver.find_element(by, element)
    return ele.text

def check_loaded(driver, element, by=By.ID, timeout=10):
    WebDriverWait(driver, timeout).until( \
            EC.presence_of_element_located((by, element)))

def get_element(driver, element, by = By.ID, timeout=10):
    WebDriverWait(driver, timeout).until( \
        EC.presence_of_element_located((by, element)))
    ele = driver.find_element(by, element)
    return ele

def get_elements(driver, element, by = By.ID, timeout=10):
    WebDriverWait(driver, timeout).until( \
        EC.presence_of_element_located((by, element)))
    ele = driver.find_elements(by, element)
    return ele


# Instagram functions
def instagram_login(driver, my_username, my_password):
    driver.get("https://instagram.com/login")
    fill_form(driver, my_username, "input[name='username']", By.CSS_SELECTOR, human=True)
    time.sleep(random.uniform(0.1, 0.3))
    fill_form(driver, my_password, "input[name='password']", By.CSS_SELECTOR, human=True)
    time.sleep(random.uniform(0.1, 0.3))
    click_item(driver, "button[type='submit']", By.CSS_SELECTOR)
    time.sleep(random.uniform(0.1, 0.3))
    click_item(driver, "div[class='_ac8f'] > button[class='_acan _acao _acas']", By.CSS_SELECTOR)

def get_instagram_user_info(driver, username):
    print(f"getting profile data for {username}")
    driver.get(f"https://instastories.watch/en/{username}/")
    soup = BeautifulSoup(driver.page_source)
    try:
        stats = [tag.text for tag in soup.select("ul.fIYNp > li")]
        n_posts, n_followers, n_following = [s for s in stats]
        title = soup.select_one("h1.ArEj5").text
        bio = soup.select_one("p.T5HPc").text
    except AttributeError:
        print("Could not get user stats! Maybe they are a private account.")
        n_posts, n_followers, n_following, title, bio = ["private" for p in range(1,6)]
    return {
        "username": username,
        "title": title, 
        "bio": bio,
        "n_posts": n_posts,
        "n_followers": n_followers,
        "n_following": n_following
    }

def get_instagram_user_posts(driver, username, n=10):
    print(f"getting posts for {username}")
    driver.get(f"https://pixwox.com/profile/{username}")
    soup = BeautifulSoup(driver.page_source)
    atags = soup.select("a[class='cover_link']")
    try:
        hrefs = [a.attrs["href"] for a in atags]
    except AttributeError:
        print("Could not get user posts! Maybe they are a private account.")
        return None
    links = [urljoin("https://pixwox.com", href) for href in hrefs]
    posts = []
    for i, link in enumerate(links): # Try grequests
        if i >= n:
            break
        driver.get(link)
        soup = BeautifulSoup(driver.page_source)
        wrapper = soup.select_one("div[class='view_w']")
        caption = wrapper.select_one("img").attrs["alt"]
        comments = []
        try:
            comment_divs = soup.select("div[class=comment_w]")
            for c in comment_divs:
                comment = {
                    "username": c.select_one("div[class='username'] > a").text.replace("@", ""),
                    "comment": c.select_one("div[class='sum']").text
                }
                comments.append(comment)
        except AttributeError:
            pass
        posts.append({
            "post": link,
            "likes": soup.select_one("div[class='count_item count_item_like cf'] > span[class='num']").text,
            "caption": caption,
            "media": wrapper.select_one("a").attrs["href"],
            "mentions": re.findall(r"@\w+", caption),
            "hashtags": re.findall(r"#\w+", caption),
            "comments": comments
        })
    return posts

def get_follower_list(driver, username, n=300):
    driver.get(f"https://www.instagram.com/{username}/followers/")
    time.sleep(random.uniform(1,4))
    scroll = """
        scrollingDiv = document.querySelector("div._aano");
        scrollingDiv.scrollTop = scrollingDiv.scrollHeight * {};
    """
    followers = set()
    while len(followers) < n:
        print(f"got {len(followers)} followers from {username}")
        driver.execute_script(scroll.format(random.uniform(0.99, 0.999))) # Random scroll length
        time.sleep(random.uniform(1,4)) # Random scroll pause
        follower_div = get_element(driver, "div._aano", By.CSS_SELECTOR).get_attribute("outerHTML")
        soup = BeautifulSoup(follower_div)
        follower_names = [s.text for s in soup.select("span[class='_aacl _aaco _aacw _aacx _aad7 _aade']")]
        print(follower_names)
        followers.update(follower_names)
    return list(followers)


class YoutubeChannel():
    def __init__(self, api_key, channel):
        self.driver = make_driver()
        self.channel = channel
        self.channel_id = self.get_channel_id(channel)
        self.data = self.get_channel_data(api_key, n_videos=10)
        self.driver.quit()

    def get_channel_id(self, channel):
        r = requests.get(f"https://youtube.com/c/{channel}")
        soup = BeautifulSoup(r.text)
        href = soup.select_one("link[itemprop='url']").attrs["href"]
        return href.split("/")[-1]

    def get_video_id(self, n=10):
        self.driver.get(f"https://www.youtube.com/c/{self.channel}/videos")
        soup = BeautifulSoup(self.driver.page_source)
        hrefs = [a.attrs["href"] for a in soup.select("a[id=video-title]")]
        ids = []
        for href in hrefs[0:n]:
            if "/shorts" in href:
                ids.append(href.split("/")[-1])
            else:
                ids.append(href.split("=")[-1])
        return ids

    def get_video_comments(self, api_key, video_id):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=api_key
        )
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id
        )
        response = request.execute()
        return response

    def get_video_data(self, api_key, video_id):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=api_key
        )
        request = youtube.videos().list(
            part="statistics,localizations,snippet,statistics,status,topicDetails,recordingDetails",
            id=video_id
        )
        response = request.execute()
        try:
            comments = self.get_video_comments(api_key, video_id)
            n_comments = len(comments["items"])
        except:
            comments = None
            n_comments = None
        return {
            "title": response["items"][0]["snippet"]["title"],
            "description": response["items"][0]["snippet"]["description"],
            "date_published": response["items"][0]["snippet"]["publishedAt"],
            "channel": response["items"][0]["snippet"]["channelTitle"],
            "n_views": response["items"][0]["statistics"]["viewCount"],
            "n_likes": response["items"][0]["statistics"]["likeCount"],
            "n_favorites": response["items"][0]["statistics"]["favoriteCount"],
            "n_comments": n_comments,
            "comments": comments
        }

    def get_channel_data(self, api_key, n_videos=10):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=api_key
        )
        request = youtube.channels().list(
            part="statistics,contentOwnerDetails,localizations,snippet,statistics,status,topicDetails,brandingSettings",
            id=self.channel_id
        )
        response = request.execute()
        keywords = response["items"][0]["brandingSettings"]["channel"]["keywords"]
        videos = self.get_video_id(n_videos)
        return {
            "title": response["items"][0]["snippet"]["title"],
            "description": re.sub(r"\\", "", re.sub(r"\n+", " ", response["items"][0]["snippet"]["description"])),
            "custom_url": response["items"][0]["snippet"]["customUrl"],
            "published_date": response["items"][0]["snippet"]["publishedAt"],
            "view_count": response["items"][0]["statistics"]["viewCount"],
            "n_subscribers": response["items"][0]["statistics"]["subscriberCount"],
            "hidden_sub_count": response["items"][0]["statistics"]["hiddenSubscriberCount"],
            "video_count": response["items"][0]["statistics"]["videoCount"],
            "topic_categories": response["items"][0]["topicDetails"]["topicCategories"],
            "country": response["items"][0]["brandingSettings"]["channel"]["country"],
            "keywords": keywords,
            "videos": [self.get_video_data(api_key, video) for video in videos]
        }
