from discoveryShow import DiscoveryShow
import asyncio
import aiohttp

class DiscoveryDownloader:

    def __init__(self):
        self.h = ""
        self.max_concurrent_downloads = 5

    async def downloadShow(self, show, cookiePath):
        url = ""

        semaphore = asyncio.Semaphore(self.max_concurrent_downloads)

        async def sem_task(task):
            async with semaphore:
                return await task

        args = ["yt-dlp", "--cookies", f"{cookiePath}", "-v", "--hls-prefer-ffmpeg", "--extractor-retries", "10", "--ignore-config", "-N50", "-o", "S%(season_number)02dE%(episode_number)02d.%(title)s.%(ext)s", url]



        result = subprocess.run (args, capture_output=True, text=True)

    
