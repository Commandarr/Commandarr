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
import datetime
import yaml

# Import custom modules
import commons

from definitions import CONFIG_PATH
config = yaml.safe_load(open(CONFIG_PATH))


# --------------------------------------------------------------------
# -------------------------- API/ROOTFOLDER --------------------------
# TODO: Using below functions when sending series to sonarr takes too
#       long and causes a timeout error
def getRootFolder():
    req = requests.get(commons.generateApiQuery('sonarr', 'rootfolder'))
    return json.loads(req.text)

def getRootFolderPath():
    data = getRootFolder()
    path = ''
    for obj in data:
        path = obj['path']
    return path

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
    req = requests.get(commons.generateApiQuery('sonarr', 'calendar', params))
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
    req = requests.get(commons.generateApiQuery('sonarr', 'command'))
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
    req = requests.get(commons.generateApiQuery('sonarr', 'series/lookup', params))
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
    req = requests.get(commons.generateApiQuery('sonarr', 'series/lookup', params))
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
    req = requests.get(commons.generateApiQuery('sonarr', 'series'))
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
    req = requests.get(commons.generateApiQuery('sonarr', 'series/' + str(series_id)))
    parsed_json = json.loads(req.text)
    return parsed_json


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
# def confirmSeries(request):
def confirmSeries(requested_series):
    context_list = []
    result = {}

    # If an id was passed from API.ai skip possible matches lookup and add by
    # TVDB id to Sonarr.
    if 'tvdb_id' in requested_series:
        # Retrieve JSON result from TVDB by TVDB id
        requested_series_match = lookupSeriesByTvdbId(int(requested_series['tvdb_id']))
        result = addSeriesToWatchList(requested_series_match)
    else:
        # Query TVDB for any possible matches by the series_name
        possible_matches = lookupSeriesByName(requested_series['media_title'])

        if len(possible_matches) == 0: # If no matches, return result
            text_response = 'Whoops! Sonarr was unable to find a match for ' + requested_series['media_title'] + '. Please open Sonarr in your browser to add Series.'
            print 'Text: ' + text_response
            result = commons.generateWebhookResponse('sonarr', text_response, context_list)
            print result

        elif len(possible_matches) == 1: # If one match, skip to adding series by Name
            result = addSeriesToWatchList(possible_matches)

        else:
            text_response = 'There are ' + str(len(possible_matches)) + ' possible matches. Which one is correct? \n'

            # Add each possible match to response text and create a context with title
            # and the tvdbId (to avoid searching again)
            for index, match in enumerate(possible_matches, start=1):
                text_response += match['title'] + '. \n'
                context_list.append({
                    "name":"possible_match_0" + str(index),
                    "lifespan":2,
                    "parameters":{
                        'title': match['title'],
                        'tvdbId': match['tvdbId']
                    }
                })

                # Generate the webhook response w/ custom messages and contexts
                result = commons.generateWebhookResponse('sonarr', text_response, context_list)

    # Returns Webhook result
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
def addSeriesToWatchList(requested_series):
    response = ''
    context_list = []

    # Check to see if match is already in Sonarr
    my_shows = getSeries()

    for series in requested_series:
        for show in my_shows:
            if int(series['tvdbId']) == int(show['tvdbId']):
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
                    'path': config['sonarr']['server']['root_folder'] + series['title']
                    # 'path': getRootFolderPath() + series['title']
                }

                # Convert to JSON
                data_json = json.dumps(data)

                # Submit request to API
                r = requests.post(commons.generateApiQuery('sonarr', 'series'), data=data_json)
                parsed_json = json.loads(r.text)

                #  Set user Response
                response = 'Success! ' + series['title'] + ' has been added to Sonarr.'

    # Create Rich Notifications
    slack_message = {
        'attachments': [{
            'fallback': response,
            "pretext": "Message from Comandarr: " + response,
            'author_name': 'Sonarr',
            "author_link": commons.generateServerAddress('sonarr') + '/series/' + series['titleSlug'],
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
    context_list = []

    result = commons.generateWebhookResponse('sonarr', response, context_list)
    return result
