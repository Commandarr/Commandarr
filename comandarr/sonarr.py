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
# Github Source: https://www.github.com/comandarr/comandarr/
# Readme Source: https://www.github.com/comandarr/comandarr/README.md
#
# #############################################################################

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

# Generate the server URL
def generateServerAddress():
    if config['sonarr']['server']['ssl']:
        http = 'https://'
    else:
        http = 'http://'

    return http + config['sonarr']['server']['addr'] + ':' + str(config['sonarr']['server']['port'])

# Performs a clean up of a URL to ensure it is valid.
def cleanUrl(text):
    url = text.replace(' ', '%20') # replace spaces with %20
    return url

# Generate the query for the Sonarr API
def generateApiQuery(endpoint, parameters={}):
    url = generateServerAddress() + '/api/' + endpoint + '?apikey=' + config['sonarr']['auth']['apikey']

    # If parameters exist iterate through dict and add parameters to URL.
    if parameters:
        for key, value in parameters.iteritems():
            url += '&' + key + '=' + value

    return url

# Generates the Webhook Response. This includes different integrations
def generateWebhookResponse(response, context={}, slack_msg={}, fb_msg={}, tele_msg={}, kik_msg={}):
    return {
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


# ---------------------------------------------------------------
# -------------------------- API/QUEUE --------------------------

# Retrieve a list of episodes currently in queue to be downloaded.
def getQueueList():


# ------------------------------------------------------------------
# -------------------------- API/CALENDAR --------------------------

# Retrieve a list of tv episodes due to be released (Up to 7 days)
# def getUpcoming(days):
    todays_date = datetime.date.today()
    weeks_end_date = todays_date + datetime.timedelta(days=days)

    params = {
        'start': str(todays_date),
        'end': str(weeks_end_date)
    }
    req = requests.get(generateApiQuery('calendar', params))
    return json.loads(req.text)


# -----------------------------------------------------------------
# -------------------------- API/COMMAND --------------------------

# Rescan all Series in Sonarr
def performCmdRescanSeries():
    req = requests.get(generateApiQuery('command'))
    parsed_json = json.loads(req.text)
    return parsed_json


# ----------------------------------------------------------------------
# -------------------------- API/QUEUE/LOOKUP --------------------------

# Lookup Series information by the series name
def lookupSeriesByName(series_name):
    # Set query parameters
    params = {
        'term': cleanUrl(series_name)
    }

    # Perform Get request from Sonarr API
    req = requests.get(generateApiQuery('series/lookup', params))
    parsed_json = json.loads(req.text)
    return parsed_json


# Lookup Series information by the series name
def lookupSeriesByTvdbId(tvdb_id):
    # Convert from Float to Integer to String
    tvdb_id_str = str(int(tvdb_id))

    # Set query parameters
    params = {
        'term': 'tvdb:' + tvdb_id_str
    }

    # Perform Get request from Sonarr API
    req = requests.get(generateApiQuery('series/lookup', params))
    parsed_json = json.loads(req.text)
    return parsed_json


# ----------------------------------------------------------------
# -------------------------- API/SERIES --------------------------

# Get all series listed in Sonarr
def getSeries():
    req = requests.get(generateApiQuery('series'))
    parsed_json = json.loads(req.text)
    return parsed_json

# Get information about a singular series, found by show ID.
def getSeriesById(series_id):
    return json.load(urllib2.urlopen(generateApiQuery('series/' + str(series_id))))

# Get the Series ID by it's name
def getSeriesIdByName(series_name):
    series_id = ''
    all_series = getSeries()
    for series in all_series:
        if series['title'] == series_name:
            series_id = series['id']

    return int(series_id)

# Confirm the Series with the user
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


# Add a TV Series to Sonarr
def addSeriesToWatchList(requested_series, requested_tvdbId=0, monitored='false'):
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
