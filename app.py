from flask import Flask
import asyncio
import os

def main():
    api = Flask(__name__)

    @api.route('/movie/<int:tmdbId>/', methods=['POST'], strict_slashes=False)
    def update_movie(tmdbId):
        return ''

    api.run(host='0.0.0.0', port='8782')

main()