# stealth_drive
## Description
This package provides various tools useful in web scraping. 
It comes with three modules: 
- lurk: Web automation with bot detection avoidance
- selenium_functions: Common selenium web scraping operations
- parse: Text parsing functions such as email extraction

## Prerequisites
- Google chrome
- Chrome webdriver
- Webdriver must be in PATH

## Installation
```
git clone https://github.com/zestycat/stealth-drive
cd stealth-drive
pip install -e .
```

## Usage:
```
# Using lurk module
from stealth_drive import lurk
sd = stealth.StealthDriver(https=True, countries=None) # Make a StealthDriver
sd.proxy_get(url, callback=None, **kwargs) # Get page w/ rotating proxies
sd.get(url, callback=None, **kwargs) # Get page without proxies
sd.get_proxies(https=True, countries=["US", "UK", "Australia", etc...]) # Make list of proxies (runs on instantiation)
sd.proxies # Return list of proxies
lurk.get_proxies(https = True, countries = None) # get proxy list
lurk.proxy_get(proxies, url) # requests.get() wrapped in rotating proxies
lurk.crawl(url, proxy=False, proxies=None, callback=None, **kwargs) # crawl every link from base url, callback and proxy optional

# Using selenium_functions module
from stealth_drive import selenium_functions as sf
sf.fill_form(driver, text, element, by=By.ID, timeout=10)
sf.click_item(driver, element, by=By.ID, timeout=10)
sf.get_element_text(driver, element, by=By.ID, timeout=10)
sf.check_loaded(driver, element, by=By.ID, timeout=10)

# using parse module
from stealth_drive import parse
parse.find_emails(text)
```
