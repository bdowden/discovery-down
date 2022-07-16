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

import datetime

from typing import Optional

class DiscoveryDown:
    def __init__(self, config: Config):
        self.scanner = FolderScanner(config.watchPath)
        self.scanner.onEpisodeDownloadRequested = self.downloadEpisode
        self.downloader = DiscoveryDownloader(config.cookiePath)
        self.parser = DiscoveryParser(config, sessionMaker)

    async def start(self):
        self.scanner.start()
        await self.downloader.start()

    async def updateShows(self):
        while True:

            sleepSeconds = 60 * 60 * 3 #3 hour - 60 seconds * 60 minutes * 3

            await asyncio.sleep(sleepSeconds * 1000)

            self.parser.updateAllShowData()

    def downloadEpisode(self, episodeId, fileName):
        epId = int(episodeId)
        with sessionMaker() as session:
            episode = session.scalars(select(Episode).where(Episode.id == epId)).first()

            if (episode):
                asyncio.run(self.downloader.downloadEpisode(episode.url, fileName))
                episode.isDownloaded = True

            session.commit()

    def addShow(self, url: str, tvdbId: Optional[str]):
        show = self.parser.retrieveShowData(url, tvdbId)

        if (not show):
            return "Something went wrong"

        return "Success"




async def main():
    cookiePath = os.path.join(str(pathlib.Path(__file__).parent.absolute()),  "cookie.txt")

    loop = asyncio.get_running_loop()
    config = Config(watchPath="/pickup", downloadPath="/download", cookiePath=cookiePath)
    down = DiscoveryDown(config)
    api.api.addShowToDatabase = down.addShow

    downloaderTask = down.start()

    updateTask = down.updateShows()

    apiServerTask = loop.run_in_executor(None, api.api.start)

    await asyncio.gather(*[downloaderTask, apiServerTask, updateTask])
    

asyncio.run(main())