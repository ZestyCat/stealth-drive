# stealth_drive
## Description
This package provides various tools useful in web scraping. 
It comes with three modules: 
- stealth: Bot detection avoidance
- selenium_functions: Common selenium web scraping operations
- parse: Text parsing functions such as email extraction

The StealthDriver class from the stealth module is very useful for web scraping and will get past most anti-bot measures. 

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
# Using stealth module
from stealth_drive import stealth
sd = stealth.StealthDriver(https=True, countries=None) # Make a StealthDriver
sd.proxy_get(url, callback=None, **kwargs) # Get page w/ rotating proxies
sd.get(url, callback=None, **kwargs) # Get page without proxies
sd.get_proxies(https=True, countries=["US", "UK", "Australia", etc...]) # Make list of proxies (runs on instantiation)
sd.proxies # Return list of proxies
stealth.get_proxies(https = True, countries = None) # get proxy list
stealth.proxy_get(proxies, url) # requests.get() wrapped in rotating proxies

# Using selenium_functions module
from stealth_drive import selenium_functions as sf
sf.fill_form(driver, text, element, by=By.ID, timeout=10)
sf.click_item(driver, element, by=By.ID, timeout=10)
sf.get_element_text(driver, element, by=By.ID, timeout=10)
sf.check_loaded(driver, element, by=By.ID, timeout=10)

# using parse module
```
