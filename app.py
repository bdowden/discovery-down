import api.api
import asyncio
import os
import pathlib

from orm.common import sessionMaker
from orm.episode import Episode

from discoveryParser import DiscoveryParser
from discoveryDownloader import DiscoveryDownloader

from fileWatcher.folderScanner import FolderScanner
from config import Config
from sqlalchemy import select

class DiscoveryDown:
    def __init__(self, config: Config):
        self.scanner = FolderScanner(config.watchPath)
        self.scanner.onEpisodeDownloadRequested = self.downloadEpisode
        self.downloader = DiscoveryDownloader(config.cookiePath)

    def start(self):
        self.scanner.start()

    def downloadEpisode(self, episodeId):
        epId = int(episodeId)
        with sessionMaker() as session:
            episode = session.scalars(select(Episode).where(Episode.id == epId)).first()

            if (episode):
                asyncio.run(self.downloader.downloadEpisode(episode.url))
                episode.isDownloaded = True

            session.commit()




async def main():
    cookiePath = os.path.join(str(pathlib.Path(__file__).parent.absolute()),  "cookie.txt")

    config = Config(watchPath="/pickup", downloadPath="/download", cookiePath=cookiePath)

    down = DiscoveryDown(config)
    down.start()
    asyncio.start_server(api.api.start())

asyncio.run(main())