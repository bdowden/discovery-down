from http.cookiejar import MozillaCookieJar

from orm.show import Show
from orm.season import Season
from orm.episode import Episode

from typing import Optional

import os
import pathlib
import re
import requests
import datetime
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from sqlalchemy import select
from urllib.parse import urljoin
from config import Config

import json

class DiscoveryParser:
    def __init__(self, config: Config, dbSessionMaker):
        self.config = config

        if (os.path.exists(config.cookiePath)):
            self.cookiePath = config.cookiePath

            self._cj = MozillaCookieJar(self.cookiePath)
            self._cj.load(ignore_discard=True, ignore_expires=True)

            self.retry = Retry(connect = 3, backoff_factor=0.5)
            self.adapter = HTTPAdapter(max_retries=self.retry)
            s = requests.Session()
            s.mount('http://', self.adapter)
            s.mount('https://', self.adapter)
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
            self._dbSessionMaker = dbSessionMaker

    def updateAllShowData(self):
        shows = []

        with self._dbSessionMaker() as database:
            res = list(database.query(Show))

            for result in res:
                shows.append({'slug': result.slug, 'tvdbId': result.tvdbId})

        for show in shows:
            self._getShowMetadata(show.get('slug'), show.get('tvdbId'))
    
    
    def retrieveShowData(self, url: str, tvdbId: Optional[str] = None):
        url_slug_regex = '^.*\/show\/(.*)$'

        result = re.match(url_slug_regex, url)

        if (not result):
            return None

        url_slug = result.group(1)

        return self._getShowMetadata(url_slug, tvdbId)

    def _getShowMetadata(self, url_slug, tvdbId):

        with self._dbSessionMaker() as database:
            show_data = self._retrieveShowMetadata(url_slug, tvdbId, database)

            database.commit()
            database.flush()

            return show_data


    def _retrieveShowMetadata(self, url_slug, tvdbId, database):
        result = self._session.get(f"https://us1-prod-direct.discoveryplus.com/cms/routes/show/{url_slug}?include=default")

        result_data = result.json()

        #with open('/config/projects/discovery-down/show.json', 'wb') as outf:
        #    outf.write(result.content)

        return self._parseShowMetadata(result_data, url_slug, tvdbId, database)

    def _parseShowMetadata(self, result_data, url_slug, tvdbId, database):

        show = database.scalars(select(Show).where(Show.slug == url_slug)).first()

        if (not show):
            show = Show(slug = url_slug)
            database.add(show)

        if (show.tvdbId != tvdbId and tvdbId != None):
            show.tvdbId = tvdbId

        included = result_data['included']

        show_id = None

        season_count = 0

        for include in included:
            attributes = include.get('attributes') or None

            if (not attributes):
                continue

            type = include.get('type') or None

            if (type == "page"):
                show.title = attributes.get('title')

            if (not 'component' in attributes):
                continue

            component = attributes['component']

            if (not show_id):
                show_id = self._getShowId(component)

            season_result = self._getSeasonResult(component)

            if (season_result):
                season_count = max(season_count, season_result)
           
        show.id = show_id

        self._getEpisodeUrls(show, season_count, database)

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

    def _getEpisodeUrls(self, show, season_count, database):
        urls = []

        show_id = show.id

        for season in range(0, season_count + 1):

            discSeason = next(filter(lambda s: s.num == season, show.seasons), None)

            if (not discSeason):
                discSeason = Season(num = season)
                show.seasons.append(discSeason)

            season_url = f"https://us1-prod-direct.discoveryplus.com/cms/collections/89438300356657080631189351362572714453?include=default&decorators=viewingHistory,isFavorite,playbackAllowed&pf[seasonNumber]={season}&pf[show.id]={show_id}"

            response = self._session.get(season_url)

            data = response.json()

            if (not 'included' in data):
                continue

            included = data.get('included')

            for include in included:
                attributes = include.get('attributes')

                if (not attributes):
                    continue
                              
                url_slug = attributes.get('path')

                if (not url_slug):
                    continue


                url = urljoin('https://www.discoveryplus.com/video/', url_slug)

                id = include.get('id')

                airDate = attributes.get('airDate')

                publishDate = attributes.get('publishStart')

                episodeNum = attributes.get('episodeNumber')

                resolution = attributes.get('videoResolution')

                ad = self.convertToDate(airDate)
                pd = self.convertToDate(publishDate)

                episode = database.scalars(select(Episode).where(Episode.id == id).where(Episode.seasonId == discSeason.id)).first()

                if (not episode):
                    episode = Episode(id = id, num = episodeNum, url = url, title = attributes.get('name'), airDate = ad, publishDate = pd)
                    discSeason.episodes.append(episode)

                if (episode.resolution != resolution):
                    episode.resolution = resolution

    def convertToDate(self, value):
        return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')