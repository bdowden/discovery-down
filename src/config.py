from typing import Optional

class Config:
    def __init__(self, watchPath: str, downloadPath: str, cookiePath: str):
        self.watchPath = watchPath
        self.downloadPath = downloadPath
        self.cookiePath = cookiePath