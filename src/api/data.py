from typing import List

from api.result import ResultSet, Result, Category

from mako.template import Template
from mako import exceptions

from orm.show import Show
from orm.episode import Episode
from orm.season import Season

from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import contains_eager

import pathlib
import os

absPath = str(pathlib.Path(__file__).parent.absolute())

templatePath = str(absPath)

RESULT_TEMPLATE = Template(filename = os.path.join(templatePath, 'template.mako'))
CAPS_TEMPLATE = Template(filename = os.path.join(templatePath, 'caps.template.mako'))
NZB_TEMPLATE = Template(filename = os.path.join(templatePath, 'nzb.template.mako'))

class Data:
    def __init__(self, dbSessionMaker, urlRetriever):
        self.dbSessionMaker = dbSessionMaker
        self.urlRetriever = urlRetriever

    def retrieveData(self, queryData):
        type = queryData.get('t')

        if (type == "caps"):
            return self.retrieveCaps()

        if (type == "tvsearch"):
            return self.retrieveQuery(queryData)

        return ''
    
    def retrieveNzb(self, episodeId: int):
        data = {'episodeId': episodeId}

        return NZB_TEMPLATE.render(**data)

    def retrieveCaps(self):
        data = {"app_version": "1", "api_version": "1", "email": "test@test.com"}

        category = Category(id = 5000, name = "TV")
        category.children.append(Category(id = 5010, name = "TV/WEB-DL"))
        category.children.append(Category(id = 5020, name = "TV/Foreign"))
        category.children.append(Category(id = 5030, name = "TV/SD"))
        category.children.append(Category(id = 5040, name = "TV/HD"))
        category.children.append(Category(id = 5045, name = "TV/UHD"))
        category.children.append(Category(id = 5050, name = "TV/Other"))
        category.children.append(Category(id = 5060, name = "TV/Sport"))
        category.children.append(Category(id = 5080, name = "TV/Documentary"))

        data["categories"] = [category]

        result = CAPS_TEMPLATE.render(**data)

        return result

    def retrieveQuery(self, queryData):

        with self.dbSessionMaker() as db:
            query = db.query(Episode)

            season = queryData.get('season')
            episode = queryData.get('ep')
            q = queryData.get('q')

            if (episode):
                query = query.filter(Episode.num == int(episode))

            if (season):
                query = query.join(Season, Season.id == Episode.seasonId)
                query = query.filter(Season.num == int(season))

            if (q):
                query = query.join(Show, Show.id == Season.showId)
                #query = query.filter(Show.title == q)

            query = query.order_by(Episode.publishDate.desc())

            total = query.count()

            data = list(query)

            result = self._convertToResults(data, total)

            return result

    def _convertToResults(self, data: List[Show], total: int):
        
        dataset = ResultSet(total = total)

        episodes = data
        for episode in episodes:
            title = "{show} S{season:0>2d}E{episode:0>2d} {title}".format(show = episode.season.show.title, season = episode.season.num, episode = episode.num, title = episode.title)
            result = Result(id = episode.id, episode = episode.num, added = episode.airDate, posted = episode.publishDate, season = episode.season.num, title = title, resolution = episode.resolution)
            dataset.releases.append(result)

        try:
            d = vars(dataset)

            d['get_url'] = self.urlRetriever

            return RESULT_TEMPLATE.render(**d)
        except Exception as ex:
            return None