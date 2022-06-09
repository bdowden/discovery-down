import DiscoveryParser
import pathlib

cookiePath = str(pathlib.Path(__file__).parent.absolute() / "cookie.txt") 

parser = DiscoveryParser({cookiePath: cookiePath})

result = parser.retrieveShowData("")

i = 0