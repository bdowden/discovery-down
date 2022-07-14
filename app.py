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

import asyncio

class DiscoveryDown:
    def __init__(self, config: Config):
        self.scanner = FolderScanner(config.watchPath)
        self.scanner.onEpisodeDownloadRequested = self.downloadEpisode
        self.downloader = DiscoveryDownloader(config.cookiePath)

    async def start(self):
        self.scanner.start()
        await self.downloader.start()

    def downloadEpisode(self, episodeId, fileName):
        epId = int(episodeId)
        with sessionMaker() as session:
            episode = session.scalars(select(Episode).where(Episode.id == epId)).first()

            if (episode):
                asyncio.run(self.downloader.downloadEpisode(episode.url, fileName))
                episode.isDownloaded = True

            session.commit()




async def main():
    cookiePath = os.path.join(str(pathlib.Path(__file__).parent.absolute()),  "cookie.txt")

    loop = asyncio.get_running_loop()
    config = Config(watchPath="/pickup", downloadPath="/download", cookiePath=cookiePath)
    down = DiscoveryDown(config)
    downloader = down.start()
    apiServer = loop.run_in_executor(None, api.api.start)

    await asyncio.gather(*[downloader, apiServer])
    

asyncio.run(main())