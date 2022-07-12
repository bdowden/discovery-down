import xml.etree.ElementTree as ET


class DiscoveryNzbParser:
    def __init__(self):
        self.t = ''

    def retrieveEpisodeId(self, filePath: str):
        elementTree = ET.parse(filePath)
        root = elementTree.getroot()
        metaEpisodeIds = root.findall(".//{0}meta[@type='episodeId']".format("{http://www.newzbin.com/DTD/2003/nzb}"))

        if (len(metaEpisodeIds) == 1):
            return metaEpisodeIds[0].text

        return None
