#from discoveryShow import DiscoveryShow
import asyncio
import aiohttp
import subprocess
import threading

from asyncio import Queue, create_task

class DiscoveryDownloader:

    def __init__(self, cookiePath: str):
        self.max_concurrent_downloads = 4
        self.cookiePath = cookiePath

        self._loop = asyncio.get_event_loop()

        self.consumers = []

    async def start(self):
        loop = self._loop

        self.queue = Queue(self.max_concurrent_downloads)
        for _ in range(self.max_concurrent_downloads):
            self.consumers.append(loop.create_task(self._downloadEpisode(self.queue)))
        
        await asyncio.wait(self.consumers, return_when=asyncio.ALL_COMPLETED)

        t = 0


    async def downloadEpisode(self, url: str, fileName: str):
        self._loop.call_soon_threadsafe(self.queue.put_nowait, {'url': url, 'name': fileName})

    async def _downloadEpisode(self, queue: Queue):
        while True:
            episodeData = await queue.get()

            url = episodeData.get('url')

            fileName = episodeData.get('name')
            
            args = ["--cookies", f"{self.cookiePath}", "--hls-prefer-ffmpeg", "--extractor-retries", "10", "--ignore-config", "-N50", "--download-archive", "/downloads/log.txt", "-o", "/downloads/{0}.%(ext)s".format(fileName), url]
            
            proc = await asyncio.create_subprocess_exec("yt-dlp", *args)

            await proc.communicate()
            
            queue.task_done()
            print(f"Downloaded episode from {url}")