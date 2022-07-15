import aiohttp
import os, pickle
import urllib.parse
from dataclasses import dataclass

from http.cookiejar import MozillaCookieJar
import requests

class DiscoveryApi:
    @dataclass
    class DiscoveryUrl:
        search: str = "https://us1-prod-direct.discoveryplus.com/cms/routes/search/result?include=default&decorators=viewingHistory,isFavorite,playbackAllowed&contentFilter[query]={searchTerm}&page[items.number]=1&page[items.size]=30"
        showMetadata: str = "https://us1-prod-direct.discoveryplus.com/cms/routes/show/{url_slug}?include=default"
        seasonMetadata: str = "https://us1-prod-direct.discoveryplus.com/cms/collections/89438300356657080631189351362572714453?include=default&decorators=viewingHistory,isFavorite,playbackAllowed&pf[seasonNumber]={season}&pf[show.id]={show_id}"
        showDownloadUrl: str = "https://www.discoveryplus.com/video/{urlSlug}"

    def __init__(self, config):
        self.config = config

        if (os.path.exists(config.get('cookiePath'))):
            self.cookiePath = config.get('cookiePath')
            self.pickled = config.get('pickleCookiePath')

            cookieJar = aiohttp.CookieJar()
            #cookieJar.load(self.pickled)

            self._cj = MozillaCookieJar(self.cookiePath)
            self._cj.load(ignore_discard=True, ignore_expires=True)


            #self.retry = Retry(connect = 3, backoff_factor=0.5)
            #self.adapter = HTTPAdapter(max_retries=self.retry)
            s = requests.Session()
            #s.mount('http://', self.adapter)
            #s.mount('https://', self.adapter)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                "authority": "us1-prod-direct.discoveryplus.com",
                "x-disco-client": "WEB:UNKNOWN:dplus_us:1.8.0",
                "x-disco-params": "realm=go,siteLookupKey=dplus_us,features=ar",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9"
            }

            self._aioSession = aiohttp.ClientSession(headers = headers, cookie_jar = cookieJar)

            s.headers = headers
            s.cookies = self._cj
            self._session = s

    async def search(self, term: str):
        url = self.DiscoveryUrl.search.format(searchTerm = urllib.parse.quote(term))
        data = self._session.get(url)

        #with open('/config/projects/discovery-down/pickled.cookies.txt', 'wb') as f:
        #    pickle.dump([c for c in self._session.cookies], f)
        
        return None