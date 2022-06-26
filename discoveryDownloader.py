from discoveryShow import DiscoveryShow
import asyncio
import aiohttp

class DiscoveryDownloader:

    def __init__(self, cookiePath: str):
        self.max_concurrent_downloads = 5
        self.cookiePath = cookiePath

    async def downloadShow(self, show: DiscoveryShow):
        
        semaphore = asyncio.Semaphore(self.max_concurrent_downloads)

        async def sem_task(task):
            async with semaphore:
                return await task

        
        for url in show.episodeUrls:
            sem_task(self._downloadEpisode(cself.ookiePath, url))
        

    async def _downloadEpisode(self, cookiePath: str, url: str):
        args = ["yt-dlp", "--cookies", f"{cookiePath}", "-v", "--hls-prefer-ffmpeg", "--extractor-retries", "10", "--ignore-config", "-N50", "-o", "/downloads/S%(season_number)02dE%(episode_number)02d.%(title)s.%(ext)s", url]

        result = subprocess.run (args, capture_output=True, text=True)
    
        return result