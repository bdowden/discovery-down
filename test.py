from discoveryParser import DiscoveryParser
import pathlib
import re

cookiePath = str(pathlib.Path(__file__).parent.absolute() / "cookie.txt") 

parser = DiscoveryParser({"cookiePath": cookiePath})

result = parser.retrieveShowData("")

included = result['included']


show_id_regex = '.*pf\[show\.id\]=(\d+).*'
show_entry_regex = ".*pf\[show\.id\].*"

show_id = None

for include in included:
  if (not 'attributes' in include):
    continue

  attributes = include['attributes']

  if (not 'component' in attributes):
    continue

  component = attributes['component']

  if (not 'mandatoryParams' in component):
    continue

  mandatoryParams = component['mandatoryParams']

  result = re.match(show_entry_regex, mandatoryParams)

  if (not result):
    continue

  show_id_match = re.match(show_id_regex, mandatoryParams)

  if (not show_id_match):
    continue

  show_id = show_id_match.group(1)
  break
  


i = 0

'''
## USING THE SHOW_JSON_FIRST DUMP, WE CAN EXTRACT THE SHOW_ID & SHOW_SEASON_COUNT
SHOW_ID=$(echo "$SHOW_JSON_FIRST" | jq -r '.included[].attributes.component.mandatoryParams' | grep -Eo '^pf.*$' | head -n1 | sed -e 's#pf\[show\.id\]\=##' | sed -e 's/&.*$//g')
SHOW_SEASON_COUNT=$(echo "$SHOW_JSON_FIRST" | jq -r '.included[]? | .attributes.component.filters | values' | grep -Eo 'pf\[seasonNumber\].*$' | sed -e 's#pf\[seasonNumber\]=##g' -e 's#",##g')


## NOW WE'LL LOOP THRU EACH SEASON TO GRAB ALL EPISODE URLS AND PUT THEM IN INPUT_URLS.txt
for SEASON_NUMBER in $(echo "$SHOW_SEASON_COUNT"); do
  curl -s "https://us1-prod-direct.discoveryplus.com/cms/collections/89438300356657080631189351362572714453?include=default&decorators=viewingHistory,isFavorite,playbackAllowed&pf\[seasonNumber\]=${SEASON_NUMBER}&pf\[show.id\]=${SHOW_ID}" \
    -H 'authority: us1-prod-direct.discoveryplus.com' \
    -H 'x-disco-client: WEB:UNKNOWN:dplus_us:prod' \
    -H 'x-disco-params: realm=go,siteLookupKey=dplus_us,features=ar' \
    -H 'referer: https://www.discoveryplus.com/' \
    -H 'accept-language: en' \
    --cookie "${COOKIE_FILE}" | jq -r '.included[]? | .attributes | .path' | sed -e 's#null##g' -e '/^$/d' | sed -e 's#^#https://www.discoveryplus.com/video/#g' >> "$EPISODE_URL_LIST"
done


## LET'S GET THE TOTAL EPISODE COUNT & SET IT TO A VARIABLE
EPISODE_COUNT=$(cat "$EPISODE_URL_LIST" | wc -l) && clear
SEASONS_SUM=$(echo "$SHOW_SEASON_COUNT" | wc -l)


## BRAG ABOUT WHAT WE FOUND
centerCOLOR_ONE "$SEASONS_SUM Seasons Found!" && sleep 1 && echo ""
centerCOLOR_TWO "$EPISODE_COUNT Episodes Found!" && sleep 3 && echo "" && echo ""
read -n 1 -s -r -p "`centerBLINK '_-Press Any Key to Begin Downloading The Episodes-_'`"


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