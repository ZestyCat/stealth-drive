# stealth_drive
## Description
The StealthDriver class is very useful for web scraping and will get past most anti-bot measures. 
It is essentially a wrapper for selenium with undetected_chromedriver, with built in proxy retrieval and rotation, and randomized user agent.
A list of up-to-date proxies is generated on instantiation. GET requests can be made using the proxy_get() method. If rotating proxies is not required, the get() method can be used.


## Prerequisites
- Selenium
- undetected_chromedriver
- bs4
- fake_useragent

## Installation
```
git clone https://github.com/zestycat/stealth-drive
cd stealth-drive
pip install -e .

from stealth_drive import stealth_drive
```

## Usage:
```
# Instantiate the class, specifying options for get_proxies() method
sd = stealth_drive.StealthDriver(https=True, countries=["US", "UK", "Australia", etc...])

# Rotate through proxies until a connection is formed
# Callback function may be passed with keyword arguments
sd.proxy_get(url, callback=None, **kwargs)

# Normal get without proxy rotation
# Callback function may be passed with keyword arguments
sd.get(url, callback=None, **kwargs)

# Get list of proxies. Runs on instantiation
# Set https to True if you want https proxies only
# Specify list of countries where proxies should be located
sd.get_proxies(https=True, countries=["US", "UK", "Australia", etc...])

# Return list of proxies
sd.proxies
```


