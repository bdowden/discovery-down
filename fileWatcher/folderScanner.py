from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from fileWatcher.discoveryNzbParser import DiscoveryNzbParser

class FolderScanner:
    def __init__(self, path: str):
        self.path = path
        self.eventHandler = PatternMatchingEventHandler(patterns=["*.nzb"], 
                                            ignore_patterns=[],
                                            ignore_directories=True)

        self.eventHandler.on_created = self.on_created
        self.observer = Observer()
        self.observer.schedule(self.eventHandler, self.path, recursive = False)
        self.fileParser = DiscoveryNzbParser()
        self.onEpisodeDownloadRequested = None

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        epId = self.fileParser.retrieveEpisodeId(event.src_path)

        if (self.onEpisodeDownloadRequested):
            self.onEpisodeDownloadRequested(epId)