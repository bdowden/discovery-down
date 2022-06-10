
class DiscoveryShow:
    def __init__(self, slug):
        self.slug = slug
        self.totalSeasons = 0
        self.episodeUrls = []
        self._show_id = 0

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
