from flask import Flask, url_for, send_file
from flask import Response, request

from typing import Optional

from api.data import Data

import pathlib
import asyncio

from orm.common import Base, engine, sessionMaker

from orm.show import Show
from orm.episode import Episode
from orm.season import Season

import urllib.parse

import os

Base.metadata.create_all(engine)

api = Flask(__name__)

@api.route('/api/', methods=['GET'], strict_slashes=False)
def search():

    def getDownloadUrl(episodeId):
        return urllib.parse.urljoin(request.host_url, url_for('retrieveNzb', episodeId = episodeId))

    d = Data(sessionMaker(), getDownloadUrl)

    queryData = request.args.to_dict()

    result = d.retrieveData(queryData)

    r = Response(response=result, status=200, mimetype="application/rss+xml")
    r.headers["Content-Type"] = "text/xml; charset=utf-8"
    return r

@api.route('/data/<int:episodeId>', methods=['GET'], strict_slashes = False)
def retrieveNzb(episodeId: int):

    d = Data(sessionMaker(), None)

    nzb = d.retrieveNzb(episodeId)

    r = Response(response=nzb, status=200)

    r.headers['Content-Type'] = 'application/x-nzb'
    r.headers['X-DNZB-Name'] = 'test'
    r.headers['X-DNZB-Category'] = 'TV'
    r.headers['Content-Disposition'] = 'attachment; filename="{ep}.nzb"'.format(ep = episodeId)
    return r

def start(port: Optional[str] = '8985'):
    api.run(host='0.0.0.0', port=port)