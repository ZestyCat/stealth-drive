# stealth_drive
## Description
The StealthDriver class r is very useful for web scraping and will get past most anti-bot measures. 
It is essentially a wrapper for selenium with undetected_chromedriver, with built in proxy retrieval and rotation, and randomized user agent.
A list of up-to-date proxies is generated on instantiation. GET requests can be made using the proxy_get() method. If rotating proxies is not required, the get() method can be used.
By default, the StealthDriver uses its own list of proxies to rotate through, but the user may also provide a list of proxies when using the proxy_get() method.

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
```

## Usage:
### Creating a StealthDriver
```
# Instantiate the class, specifying options for get_proxies() method
sd = StealthDriver(https=True, countries=["US", "UK", "Australia", etc...])
```

### GET request through rotating proxy
```
# Rotate through proxies until a connection is formed
# Callback function may be passed with keyword arguments
sd.proxy_get(url, callback=None, **kwargs)
```

### GET request without proxy
```
# Normal get without proxy rotation
# Callback function may be passed with keyword arguments
sd.get(url, callback=None, **kwargs)
```

### Create list of proxies (runs on instantiation)
```
# Get list of proxies. Runs on instantiation
# Set https to True if you want https proxies only
# Specify list of countries where proxies should be located
sd.get_proxies(https=True, countries=["US", "UK", "Australia", etc...])
```

### Return list of proxies
```
sd.proxies
```


