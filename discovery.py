import asyncio
import os
from discoveryParser import DiscoveryParser
from discoveryDownloader import DiscoveryDownloader

async def main():
    cookie = "/config/cookie.txt"

    url = input("Enter show URL:\n")

    config = {'cookiePath': cookie}

    show = DiscoveryParser(config).retrieveShowData(url)

    downloader = DiscoveryDownloader(cookie)

    await downloader.downloadShow(show)

asyncio.run(main())