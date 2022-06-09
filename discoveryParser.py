from http.cookiejar import MozillaCookieJar
import os
import pathlib
import requests

class DiscoveryParser:
    def __init__(self, config):
        self.config = config

        if (os.path.exists(config['cookiePath'])):
            self.cookiePath = config['cookiePath']
    
    def retrieveShowData(self, url):
        cj = MozillaCookieJar(self.cookiePath)
        cj.load(ignore_discard=True, ignore_expires=True)

        url_slug = "deadliest-catch"

        s = requests.Session()
        s.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "authority": "us1-prod-direct.discoveryplus.com",
            "x-disco-client": "WEB:UNKNOWN:dplus_us:1.8.0",
            "x-disco-params": "realm=go,siteLookupKey=dplus_us,features=ar",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9"
        }

        s.cookies = cj

        result = s.get(f"https://us1-prod-direct.discoveryplus.com/cms/routes/show/{url_slug}?include=default&decorators=viewingHistory,isFavorite,playbackAllowed")

        cj.save(ignore_discard=True, ignore_expires=True)

        return result.json()





# -H 'authority: us1-prod-direct.discoveryplus.com' \
#  -H 'x-disco-client: WEB:UNKNOWN:dplus_us:1.8.0' \
#3  -H 'x-disco-params: realm=go,siteLookupKey=dplus_us,features=ar' \
#  -H 'accept: */*' \
#  -H 'accept-language: en-US,en;q=0.9' \



#        import os
#import pathlib
#import requests
#from http.cookiejar import MozillaCookieJar


#cookiesFile = str(pathlib.Path(__file__).parent.absolute() / "cookies.txt")  # Places "cookies.txt" next to the script file.
#cj = MozillaCookieJar(cookiesFile)
#if os.path.exists(cookiesFile):  # Only attempt to load if the cookie file exists.
#    cj.load(ignore_discard=True, ignore_expires=True)  # Loads session cookies too (expirydate=0).

#s = requests.Session()
#s.headers = {
#    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
#    "Accept-Language": "en-US,en"
#}
#s.cookies = cj  # Tell Requests session to use the cookiejar.

# DO STUFF HERE WHICH REQUIRES THE PERSISTENT COOKIES...
#s.get("https://www.somewebsite.com/")

#cj.save(ignore_discard=True, ignore_expires=True)  # Saves session cookies too (expirydate=0).