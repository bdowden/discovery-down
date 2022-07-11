import api.api
import asyncio
import os
import pathlib

from discoveryParser import DiscoveryParser

from fileWatcher.folderScanner import FolderScanner
from config import Config

class DiscoveryDown:
    def __init__(self, config: Config):
        self.scanner = FolderScanner(config.watchPath)
        #self.parser = parser

    def start(self):
        self.scanner.start()

def main():
    cookiePath = os.path.join(str(pathlib.Path(__file__).parent.absolute()),  "cookie.txt")

    config = Config(watchPath="/pickup", downloadPath="/download", cookiePath=cookiePath)

    down = DiscoveryDown(config)
    down.start()
    asyncio.start_server(api.api.start())

main()