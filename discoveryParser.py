from http.cookiejar import MozillaCookieJar
from discoveryShow import DiscoveryShow
import os
import pathlib
import re
import requests

class DiscoveryParser:
    def __init__(self, config):
        self.config = config

        if (os.path.exists(config['cookiePath'])):
            self.cookiePath = config['cookiePath']

            self._cj = MozillaCookieJar(self.cookiePath)
            self._cj.load(ignore_discard=True, ignore_expires=True)
            s = requests.Session()
            s.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                "authority": "us1-prod-direct.discoveryplus.com",
                "x-disco-client": "WEB:UNKNOWN:dplus_us:1.8.0",
                "x-disco-params": "realm=go,siteLookupKey=dplus_us,features=ar",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9"
            }
            
            s.cookies = self._cj
            self._session = s
    
    def retrieveShowData(self, url):
        url_slug_regex = '^.*\/show\/(.*)$'

        result = re.match(url_slug_regex, url)

        if (not result):
            return None

        url_slug = result.group(1)

        show_data = self._retrieveShowMetadata(url_slug)

        return show_data

    def _retrieveShowMetadata(self, url_slug):
        result = self._session.get(f"https://us1-prod-direct.discoveryplus.com/cms/routes/show/{url_slug}?include=default&decorators=viewingHistory,isFavorite,playbackAllowed")

        result_data = result.json()

        return self._parseShowMetadata(result_data, url_slug)

    def _parseShowMetadata(self, result_data, url_slug):        
        show = DiscoveryShow(url_slug)
        included = result_data['included']

        show_id = None

        season_count = 0

        for include in included:
            if (not 'attributes' in include):
                continue

            attributes = include['attributes']

            if (not 'component' in attributes):
                continue

            component = attributes['component']

            if (not show_id):
                show_id = self._getShowId(component)

            season_result = self._getSeasonResult(component)

            if (season_result):
                season_count = max(season_count, season_result)
           
        show.showId = show_id
        show.totalSeasons = season_count

        show.episodeUrls.extend(self._getEpisodeUrls(show_id, season_count))

        return show

    def _getShowId(self, component):
        show_id_regex = '.*pf\[show\.id\]=(\d+).*'
        show_entry_regex = ".*pf\[show\.id\].*"

        if (not 'mandatoryParams' in component):
            return None

        mandatoryParams = component['mandatoryParams']

        result = re.match(show_entry_regex, mandatoryParams)

        if (not result):
            return None

        show_id_match = re.match(show_id_regex, mandatoryParams)

        if (not show_id_match):
            return None

        return show_id_match.group(1)

    def _getSeasonResult(self, component):
        max_season = 0
        season_num_regex = '.*pf\[seasonNumber\]=\d+.*'

        if (not 'filters' in component):
            return 0

        filters = component['filters']

        if (len(filters) == 0):
            return 0

        first_filter = filters[0]

        if (not 'options' in first_filter):
            return 0

        options = first_filter['options']

        for option in options:
            if (re.match(season_num_regex, option['parameter'])):
                max_season = max(int(option['value']), max_season)

        return max_season

    def _getEpisodeUrls(self, show_id, season_count):
        urls = []

        for season in range(0, season_count + 1):
            season_url = f"https://us1-prod-direct.discoveryplus.com/cms/collections/89438300356657080631189351362572714453?include=default&decorators=viewingHistory,isFavorite,playbackAllowed&pf[seasonNumber]={season}&pf[show.id]={show_id}"

            response = self._session.get(season_url)

            data = response.json()

            if (not 'included' in data):
                continue

            included = data['included']

            for include in included:
                if (not 'attributes' in include):
                    continue

                attributes = include['attributes']

                if (not 'path' in attributes):
                    continue

                
                url_slug = attributes['path']

                urls.append(f"https://www.discoveryplus.com/video/{url_slug}")

            
        return urls