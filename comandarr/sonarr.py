# #############################################################################
# File Name: sonarr.py
# Author: Todd Johnson
# Creation Date: 29/03/2017
#
# Description: This Python script is the business logic for a bot that interacts
#              with Sonarr's API. This allows users to perform tasks in Sonarr
#              by utilising consumer applications like Telegram, Facebook Messenger
#              and also interact with Sonarr via voice with Google Assistant/Home,
#              Amazon Alexa and Microsoft Cortana.
#              The integration of these consumer technologies are implemented
#              through API.ai (Machine Learning(ML) and Natural Language
#              Processing(NLP)) via webhook.
#
# Offical website: https://www.comandarr.github.io
# Github Source: https://www.github.com/comandarr/comandarr/
# Readme Source: https://www.github.com/comandarr/comandarr/README.md
#
# #############################################################################

# Import Required modules
import json
import urllib2
import requests
import yaml
import datetime

# Set User Configurations
from definitions import CONFIG_PATH
config = yaml.safe_load(open(CONFIG_PATH))


# -------------------------------------------------------------
# -------------------------- GENERIC --------------------------

# Function: generateServerAddress
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Generate the server URL
#
# @return addr | STR | http(s)://ip_address:port
def generateServerAddress():
    if config['sonarr']['server']['ssl']:
        http = 'https://'
    else:
        http = 'http://'

    addr = http + config['sonarr']['server']['addr'] + ':' + str(config['sonarr']['server']['port'])
    return addr


# Function: cleanUrl
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Performs a clean up of a URL to ensure it is valid.
#
# @param text | STR | Dirty URL Address
# @return url | STR | Clean URL Address
def cleanUrl(text):
    url = text.replace(' ', '%20') # replace spaces with %20
    return url


# Function: generateApiQuery
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Generates an API Query that is compatible with Sonarr.
#
# @param endpoint | STR | The Sonarr API endpoint for query
# @param parameters | DICT | Add any parameters to query
# @return url | STR | HTTP api query string
def generateApiQuery(endpoint, parameters={}):

    # Set default API query with authentication
    url = generateServerAddress() + '/api/' + endpoint + '?apikey=' + config['sonarr']['auth']['apikey']

    # If parameters exist iterate through dict and add parameters to URL.
    if parameters:
        for key, value in parameters.iteritems():
            url += '&' + key + '=' + value

    return cleanUrl(url) # Clean URL (validate) and return as string


# Function: generateWebhookResponse
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Generates the Webhook Response.
#
# @param response | STR | Basic text response to user
# @param context | DICT | Any extra contexts that need to be sent back to API.ai
# @param slack_msg | DICT | Specific Slack formatting
# @param tele_msg | DICT | Specific Telegram formatting
# @param kik_msg | DICT | Specific Kik formatting
# @param fb_msg | DICT | Specific Facebook Messenger formatting
# @return result | DICT | The Response to user with different integration formatting.
def generateWebhookResponse(response, context={}, slack_msg={}, fb_msg={}, tele_msg={}, kik_msg={}):
    result = {
        'speech': response,
        'displayText': response,
        'data': {
            'slack': slack_msg,
            'facebook': fb_msg,
            'telegram': tele_msg,
            'kik': kik_msg
        },
        'contextOut': context,
        'source': 'Sonarr'
    }

    return result


# ------------------------------------------------------------------
# -------------------------- API/CALENDAR --------------------------

# Function: getUpcoming
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Retrieve a list of tv episodes due to be released.
#
# TODO: Test and implement in API.ai
#
# @param days | STR | The amount of days requested for query
# @return req | DICT | List of upcoming episodes within the amount of days requested
def getUpcoming(days):
    todays_date = datetime.date.today()
    weeks_end_date = todays_date + datetime.timedelta(days=int(days))

    params = {
        'start': str(todays_date),
        'end': str(weeks_end_date)
    }
    req = requests.get(generateApiQuery('calendar', params))
    return json.loads(req.text)


# -----------------------------------------------------------------
# -------------------------- API/COMMAND --------------------------

# Function: performCmdRescanSeries
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Rescan all Series in Sonarr
#
# TODO: To test and implement in API.ai
#
# @return parsed_json | DICT | Result of Sonarr Command
def performCmdRescanSeries():
    req = requests.get(generateApiQuery('command'))
    parsed_json = json.loads(req.text)
    return parsed_json


# ----------------------------------------------------------------------
# -------------------------- API/QUEUE/LOOKUP --------------------------

# Function: lookupSeriesByName
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Lookup Series information in TVDB by the series name
#
# @param series_name | STR | The name of the series to be looked up
# @return parsed_json | DICT | List of all possible matches
def lookupSeriesByName(series_name):
    params = { # Set query parameters
        'term': series_name
    }

    # Perform Get request from Sonarr API
    req = requests.get(generateApiQuery('series/lookup', params))
    parsed_json = json.loads(req.text)
    return parsed_json



# Function: lookupSeriesByTvdbId
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Lookup Series information in TVDB by the TVDB ID
#
# @param tvdb_id | FLOAT | The TVDB ID of the series to be looked up
# @return parsed_json | DICT | List of all possible matches
def lookupSeriesByTvdbId(tvdb_id):
    params = { # Set query parameters
        'term': 'tvdb:' + str(int(tvdb_id))
    }

    # Perform Get request from Sonarr API
    req = requests.get(generateApiQuery('series/lookup', params))
    parsed_json = json.loads(req.text)
    return parsed_json


# ----------------------------------------------------------------
# -------------------------- API/SERIES --------------------------

# Function: getSeries
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Get all series information listed in Sonarr
#
# @return parsed_json | DICT | List of all tv series in Sonarr
def getSeries():
    req = requests.get(generateApiQuery('series'))
    parsed_json = json.loads(req.text)
    return parsed_json


# Function: getSeriesById
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Get information about a singular series, found by Sonarr's series ID.
#
# @param series_id | INT | Sonarr's Series ID
# @return parsed_json | DICT | information about single TV Series in Sonarr
def getSeriesById(series_id):
    return json.load(urllib2.urlopen(generateApiQuery('series/' + str(series_id))))


# Function: getSeriesIdByName
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Get Sonarr's Series ID by the Series name
#
# @param series_name | STRING | The TV Show name
# @return parsed_json | DICT | Returns the series id
def getSeriesIdByName(series_name):
    series_id = ''
    all_series = getSeries()
    for series in all_series:
        if series['title'] == series_name:
            series_id = series['id']

    return int(series_id)


# Function: confirmSeries
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: If there is more than one possible match for the user's request,
#              ask the user to confirm which series to download. Once confirmed
#              send series_name & tvdb_id to function to be downloaded.
#
# @param series_name | STR | The TV Series name
# @param media_type | STR | The media type from API.ai (Series, Movie etc.)
# @param tvdbId | INT | The TV Series TVDB ID
# @return result | DICT | Webhook Response
def confirmSeries(series_name, media_type, tvdbId=0):
    context_list = []
    result = {}

    # If only series_name parsed from request check for possible matches.
    if tvdbId == 0:
        # Query Sonarr for possible matches
        possible_matches = lookupSeriesByName(series_name)

        # Set response text
        response = 'There are ' + str(len(possible_matches)) + ' possible matches. Which one is correct? \n'

        # Add each possible match to response text and create a context with title
        # and the tvdbId (to avoid searching again)
        for index, match in enumerate(possible_matches, start=1):
            response += match['title'] + '. \n'
            context_list.append({
                    "name":"possible_match_0" + str(index),
                    "lifespan":2,
                    "parameters":{
                        'title': match['title'],
                        'tvdbId': match['tvdbId']
                        }
                })

        # Create custom app message formats
        slack_message = {
            'attachments': [{
                'fallback': response,
                'text': response,
                'color': 'warning',
                "thumb_url": config['sonarr']['resources']['app_logo'],
            }]
        }

        # Generate the webhook response w/ custom messages and contexts
        result = generateWebhookResponse(response, context_list, slack_message)

    else:
        exact_match = lookupSeriesByTvdbId(tvdbId)
        print 'match: '
        print exact_match
        result = addSeriesToWatchList(exact_match)

    return result


# Function: addSeriesToWatchList
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Add the requested series to Sonarr
#
# @param requested_series | STR | The TV Series name
# @param requested_tvdbId | INT | The TV Series TVDB ID
# @param monitored | BOOL | Whether series is to monitored right away.
# @return result | DICT | Webhook Response
def addSeriesToWatchList(requested_series, requested_tvdbId=0, monitored=False):
    response = ''

    # Check to see if match is already in Sonarr
    my_shows = getSeries()

    for series in requested_series:
        for show in my_shows:
            if int(series['tvdbId']) == int(show['tvdbId']):
                if config['comandarr']['settings']['slang'].lower() == 'au':
                    print 'test1'
                    response = 'You Dill! ' + series['title'] + ' is already in Sonarr'
                else:
                    print 'test2'
                    response = 'Looks like Sonarr is already watching for ' + series['title']
            else:
                data = { # Generate data query
                    'tvdbId': int(series['tvdbId']),
                    'title': series['title'],
                    'qualityProfileId': 3,
                    'titleSlug': series['titleSlug'],
                    'images': series['images'],
                    'seasons': series['seasons'],
                    'monitored': True,
                    'seasonFolder': True,
                    'path': '/Volumes/Plex Media 1/Plex/TV Shows/' + series['title']
                }

                # Convert to JSON
                data_json = json.dumps(data)

                # Submit request to API
                r = requests.post(generateApiQuery('series'), data=data_json)
                parsed_json = json.loads(r.text)

                # performCmdRescanSeries()

                #  Set user Response
                if config['comandarr']['settings']['slang'].lower() == 'au':
                    response = 'No Worries! ' + series['title'] + ' has been added to Sonarr.'
                else:
                    response = 'Success! ' + series['title'] + ' has been added to Sonarr.'

    # Create Rich Notifications
    slack_message = {
        'attachments': [{
            'fallback': response,
            "pretext": "Message from Comandarr: " + response,
            'author_name': 'Sonarr',
            "author_link": generateServerAddress() + '/series/' + series['titleSlug'],
            "author_icon": config['sonarr']['resources']['app_logo'],
            'title': 'Imported: ' + series['title'],
            # 'text': series['overview'],
            'color': 'good',
            "fields": [
                {
                    "title": "Number of Seasons",
                    "value": str(series['seasonCount']),
                    "short": 'true'
                },
                {
                    "title": "Monitored",
                    "value": str(series['monitored']),
                    "short": 'true'
                }
            ],
            "thumb_url": config['sonarr']['resources']['app_logo'],
        }]
    }
    context = {}

    return generateWebhookResponse(response, context, slack_message)
