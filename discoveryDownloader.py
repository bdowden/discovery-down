#from discoveryShow import DiscoveryShow
import asyncio
import aiohttp
import subprocess

class DiscoveryDownloader:

    def __init__(self, cookiePath: str):
        self.max_concurrent_downloads = 4
        self.cookiePath = cookiePath
        self.queue = asyncio.Queue(self.max_concurrent_downloads)
        self.consumers = [asyncio.create_task(self._downloadEpisode(self.queue))
                        for _ in range(self.max_concurrent_downloads)]

    async def downloadEpisode(self, url: str):
        await self.queue.put(url)

        i = 0
        #await self.queue.join()

#async def downloadShow(self, show):
 #       for url in show.episodeUrls:
  #          await queue.put(url)
#
 #       await queue.join()
  #      print("All episodes downloaded")

    async def _downloadEpisode(self, queue):
        while True:
            url = await queue.get()
            print(f"Downloading episode from {url}")
            #args = ["yt-dlp", "--cookies", f"{self.cookiePath}", "-v", "--hls-prefer-ffmpeg", "--extractor-retries", "10", "--ignore-config", "-N50", "-o", "/downloads/S%(season_number)02dE%(episode_number)02d.%(title)s.%(ext)s", url]
            args = ["--cookies", f"{self.cookiePath}", "--hls-prefer-ffmpeg", "--extractor-retries", "10", "--ignore-config", "-N50", "--download-archive", "/downloads/log.txt", "-o", "/downloads/S%(season_number)02dE%(episode_number)02d.%(title)s.%(ext)s", url]
            
            proc = await asyncio.create_subprocess_exec("yt-dlp", *args)

            await proc.communicate()
            
           # result = subprocess.run (args, capture_output=True, text=True)
           # print(result.stdout)
            queue.task_done()
            print(f"Downloaded episode from {url}")