import asyncio
import os
from discoveryShow import DiscoveryShow
from discoveryParser import DiscoveryParser
from discoveryDownloader import DiscoveryDownloader

async def main():
    cookie = "/config/cookie.txt"

    url = input("Enter show URL:\n")

    config = {'cookiePath': cookie}
    downloader = DiscoveryDownloader(cookie)

    show : DiscoveryShow = DiscoveryParser(config).retrieveShowData(url)

    if (not show):
        print("Could not retrieve show data")

    print(f"Found show {show.slug}; seasons: {show.totalSeasons} episodes: {show.episodeCount}")
    
    #await downloader.downloadShow(show)

asyncio.run(main())