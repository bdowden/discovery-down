
class DiscoveryShow:
    def __init__(self, slug):
        self.slug = slug
        self.totalSeasons = 0
        self.episodeUrls = []
        self._show_id = 0
        self.seasons = []

    @property
    def episodeCount(self):
        return len(self.episodeUrls)

    @property
    def showId(self):
        return self._show_id

    @showId.setter
    def showId(self, value):
        self._show_id = value

    def addEpisodeUrl(self, url):
        self.episodeUrls.append(url)

class DiscoverySeason:
    def __init__(self, seasonNumber: int, show: DiscoveryShow):
        self.show = show
        self.seasonNumber = seasonNumber
        self.episodes = []

    @property 
    def episodeCount(self):
        return len(self.episodes)

class DiscoveryEpisode:
    def __init__(self, season: DiscoverySeason, episodeNum: int, url: str):
        self.season = season
        self.episodeNum = episodeNum
        self.url = url