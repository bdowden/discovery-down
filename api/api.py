from flask import Flask, url_for, send_file
from flask import Response, request

from typing import Optional

from api.data import Data
from mako.template import Template


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

absPath = str(pathlib.Path(__file__).parent.absolute())


templatePath = str(absPath)
ADD_SHOW_TEMPLATE = Template(filename = os.path.join(templatePath, 'addShow.template.mako'))

def getDownloadUrl(episodeId):
    return urllib.parse.urljoin(request.host_url, url_for('retrieveNzb', episodeId = episodeId))

d = Data(sessionMaker, getDownloadUrl)

addShowToDatabase = None

@api.route('/show', methods=["POST"], strict_slashes=False)
def addShow():
    data = request.form
    url = data.get('dUrl') or None
    tvdbId = data.get('tvdbId') or None

    if (not addShowToDatabase):
        return "addShowToDatabase is null"
        
    result = addShowToDatabase (url, tvdbId)

    return result

@api.route('/show', methods=['GET'], strict_slashes=False)
def getAddShowPage():
    postUrl = urllib.parse.urljoin(request.host_url, url_for('addShow'))
    return ADD_SHOW_TEMPLATE.render(**{'postUrl': postUrl})


@api.route('/api/', methods=['GET'], strict_slashes=False)
def search():

    queryData = request.args.to_dict()

    result = d.retrieveData(queryData)

    r = Response(response=result, status=200, mimetype="application/rss+xml")
    r.headers["Content-Type"] = "text/xml; charset=utf-8"
    return r

@api.route('/data/<int:episodeId>', methods=['GET'], strict_slashes = False)
def retrieveNzb(episodeId: int):

    nzb = d.retrieveNzb(episodeId)

    r = Response(response=nzb, status=200)

    r.headers['Content-Type'] = 'application/x-nzb'
    r.headers['X-DNZB-Name'] = 'test'
    r.headers['X-DNZB-Category'] = 'TV'
    r.headers['Content-Disposition'] = 'attachment; filename="{ep}.nzb"'.format(ep = episodeId)
    return r

#@api.route('/api/show/search/<str:term>', methods=['GET'], strict_slashes = False)
def showSearch(term):
    return ''


def start(port: Optional[str] = '8985'):
    api.run(host='0.0.0.0', port=port)