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
# Github Source: https://www.github.com/TJohnson93/comandarr/
# Readme Source: https://www.github.com/TJohnson93/comandarr/README.md
#
# #############################################################################

import json
import urllib2
import requests
import yaml
import datetime
import csv

# Collect user configuration settings
CONFIG = yaml.safe_load(open('config.yaml'))

# -------------------------------------------------------------
# -------------------------- GENERIC --------------------------

# Generate the server URL (e.g. https://ipaddress:port)
def generateServerAddress():
    if CONFIG['sonarr']['server']['ssl']:
        http = 'https://'
    else:
        http = 'http://'

    return http + CONFIG['sonarr']['server']['addr'] + ':' + str(CONFIG['sonarr']['server']['port'])

# Performs a clean up of a URL to ensure it is valid.
def cleanUrl(text):
    url = text.replace(' ', '%20') # replace spaces with %20
    return url

# Generate the query for the Sonarr API
def generateApiQuery(endpoint, parameters={}):
    url = generateServerAddress() + '/api/' + endpoint + '?apikey=' + CONFIG['sonarr']['auth']['apikey']

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
        'contextOut': [context],
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
    params = {
        'term': cleanUrl(series_name)
    }
    # return requests.get(generateApiQuery('series/lookup', params))
    return json.load(urllib2.urlopen(generateApiQuery('series/lookup', params)))


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
def confirmSeries(series_name):
    result = {}

    # Retrieve any shows that match the user's request
    possible_matches = lookupSeriesByName(series_name)

    if len(possible_matches) > 1:
        context_params = {}
        response = 'There are ' + str(len(possible_matches)) + ' possible matches. Which one is correct?'

        for index, match in enumerate(possible_matches, start=1):
            response += ' Option ' + str(index) + ' is ' + match['title'] + '.'

        slack_message = {
            'attachments': [{
                'fallback': response,
                'text': response,
                'color': 'warning',
                "thumb_url": CONFIG['sonarr']['resources']['app_logo'],
            }]
        }
        context = {
                "name":"media",
                "lifespan":1,
                "parameters":{}
            }

        result = generateWebhookResponse(response, context, slack_message)

    elif len(possible_matches) == 1:
        for match in possible_matches:
            result = addSeriesToWatchList(match)

    return result

# Add a TV Series to Sonarr
def addSeriesToWatchList(series, monitored='false'):
    response = ''


    # Check to see if match is already in Sonarr
    my_shows = getSeries()
    for show in my_shows:

        if series['tvdbId'] == show['tvdbId']:
            if CONFIG['comandarr']['settings']['slang'].lower() == 'au':
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
            if CONFIG['comandarr']['settings']['slang'].lower() == 'au':
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
            "author_icon": CONFIG['sonarr']['resources']['app_logo'],
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
            "thumb_url": CONFIG['sonarr']['resources']['app_logo'],
        }]
    }
    context = {}

    return generateWebhookResponse(response, context, slack_message)
