from discoveryParser import DiscoveryParser
from discoveryShow import DiscoveryShow
import pathlib
import subprocess

cookiePath = str(pathlib.Path(__file__).parent.absolute() / "cookie.txt") 

parser = DiscoveryParser({"cookiePath": cookiePath})

show = parser.retrieveShowData("")

url = show.episodeUrls[0]

args = ["yt-dlp", "--cookies", f"{cookiePath}", "-v", "--hls-prefer-ffmpeg", "--extractor-retries", "10", "--ignore-config", "-N50", "-o", "S%(season_number)02dE%(episode_number)02d.%(title)s.%(ext)s", url]

result = subprocess.run (args, capture_output=True, text=True)

print ('err: ', result.stderr)
print ('output: ', result.stdout)

print ("done")

'''

### Now We Sit Back and Have YT-DLP Download Every Episode We Found From Our TXT File
## Create a function so we can multi-thread
  MULTI_THREAD(){
    ## This Method is WAY FASTER than using w/ aria2c.
    ## "I've Included some extra metadata/thumbnail flags as well"
    ## If your connection/cpu can or cannot handle the current parallel downloading setting,modify "-N50" to increase/decrease the number of parallel fragment downloads per episode
    yt-dlp  --embed-thumbnail \
      --embed-metadata \
      --write-all-thumbnails \
      -N50 \
      --ignore-config \
      --cookies "$COOKIE_FILE" \
      --quiet \
      --no-warnings \
      --extractor-retries 10 \
      --hls-prefer-ffmpeg \
      ${LOG_FILE:+--download-archive $LOG_FILE} \
      -o '%(series)s/Season %(season_number)s/%(series)s - S%(season_number)02dE%(episode_number)02d: %(title)s.%(ext)s' \
      "$1"

  }

## THE NUMBER OF DOWNLOADS TO RUN AT ONCE, MODIFY AS NEEDED
## CURRENTLY THIS SCRIPT WILL CREATE 5 THREADS AT A TIME
THREADS=5

if ! hash parallel; then {
  centerCOLOR_FOUR "GNU Parallel not available, falling back to shell jobs"
  ## READ LINES FROM EPISODE_URL_LIST AND PASS IT TO MULTI_THREAD FUNCTION
  while read -r EP_URL; do
    centerBOLD "Downloading:"
    centerBOLD_TWO "$EP_URL"
    MULTI_THREAD $EP_URL &
    [ "$( jobs | wc -l )" -ge $THREADS ] && wait
  done < "$EPISODE_URL_LIST"
}
else {
    export -f MULTI_THREAD
    export COOKIE_FILE
    export LOG_FILE
    parallel --bar -P$THREADS MULTI_THREAD < "$EPISODE_URL_LIST"
}
fi
wait
clear


## Remove The TXT File of URLS, Feel Free To Comment This Out
centerCOLOR_ONE "To KEEP $EPISODE_URL_LIST Type: N ..and Hit Enter" && echo ""
centerCOLOR_TWO "To DELETE $EPISODE_URL_LIST Type: Y ..and Hit Enter" && echo "" && echo ""
rm -i "$EPISODE_URL_LIST"
clear


## ALL DONE
centerCOLOR_ONE "WE'RE ALL DONE HERE.." && sleep 1 && echo "" && echo ""
centerCOLOR_TWO "...For More Scripts, Be Sure To Checkout My Repo:" && sleep 1 && echo ""
centerCOLOR_THREE "https://github.com/ohmybahgosh/YT-DLP-SCRIPTS" && sleep 3 && echo "" && echo ""
read -n 1 -s -r -p "`centerBLINK '_-Press Any Key to Exit-_'`"
clear
exit 0
'''