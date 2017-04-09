# #############################################################################
# File Name: radarr.py
# Author: Todd Johnson
# Creation Date: 06/04/2017
#
# Description: This Python script is the business logic for a bot that interacts
#              with Radarr's API. This allows users to perform tasks in Radarr
#              by utilising consumer applications like Telegram, Facebook Messenger
#              and also interact with Radarr via voice with Google Assistant/Home,
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
# TODO: Using below functions when sending series to radarr takes too
#       long and causes a timeout error
def getRootFolder():
    req = requests.get(commons.generateApiQuery('radarr', 'rootfolder'))
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
    req = requests.get(commons.generateApiQuery('radarr', 'calendar', params))
    return json.loads(req.text)


# -----------------------------------------------------------------
# -------------------------- API/COMMAND --------------------------

# Function: performCmdRescanSeries
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Rescan all Series in Radarr
#
# TODO: To test and implement in API.ai
#
# @return parsed_json | DICT | Result of Radarr Command
def performCmdRescanSeries():
    req = requests.get(commons.generateApiQuery('radarr', 'command'))
    parsed_json = json.loads(req.text)
    return parsed_json


# ----------------------------------------------------------------------
# -------------------------- API/QUEUE/LOOKUP --------------------------

# Function: lookupMovieByName
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Lookup Series information in TVDB by the series name
#
# @param series_name | STR | The name of the series to be looked up
# @return parsed_json | DICT | List of all possible matches
def lookupMovieByName(series_name):
    params = { # Set query parameters
        'term': series_name
    }

    # Perform Get request from Radarr API
    req = requests.get(commons.generateApiQuery('radarr', 'movies/lookup', params))
    parsed_json = json.loads(req.text)
    return parsed_json


# Function: lookupMovieByTmdbId
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Lookup Series information in TVDB by the TVDB ID
#
# @param tmdb_id | FLOAT | The TVDB ID of the series to be looked up
# @return parsed_json | DICT | List of all possible matches
def lookupMovieByTmdbId(tmdb_id):
    params = { # Set query parameters
        'tmdbId': str(int(tmdb_id))
    }

    # Perform Get request from Radarr API
    req = requests.get(commons.generateApiQuery('radarr', 'movies/lookup/tmdb', params))
    parsed_json = json.loads(req.text)
    print req
    return parsed_json


# ----------------------------------------------------------------
# -------------------------- API/SERIES --------------------------

# Function: getMovies
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Get all series information listed in Radarr
#
# @return parsed_json | DICT | List of all tv series in Radarr
def getMovies():
    req = requests.get(commons.generateApiQuery('radarr', 'movie'))
    parsed_json = json.loads(req.text)
    return parsed_json


# Function: getMovieById
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Get information about a singular series, found by Radarr's series ID.
#
# @param series_id | INT | Radarr's Series ID
# @return parsed_json | DICT | information about single TV Series in Radarr
def getMovieById(series_id):
    req = requests.get(commons.generateApiQuery('radarr', 'movie/' + str(series_id)))
    parsed_json = json.loads(req.text)
    return parsed_json


# Function: getMovieIdByName
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Get Radarr's Series ID by the Series name
#
# @param series_name | STRING | The TV Show name
# @return parsed_json | DICT | Returns the series id
def getMovieIdByName(series_name):
    series_id = ''
    all_series = getMovie()
    for series in all_series:
        if series['title'] == series_name:
            series_id = series['id']

    return int(series_id)



# Function: confirmMovie
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: If there is more than one possible match for the user's request,
#              ask the user to confirm which series to download. Once confirmed
#              send series_name & tmdb_id to function to be downloaded.
#
# @param series_name | STR | The TV Series name
# @param media_type | STR | The media type from API.ai (Series, Movie etc.)
# @param tmdbId | INT | The TV Series TVDB ID
# @return result | DICT | Webhook Response
# def confirmSeries(request):
def confirmMovie(requested_movie):
    context_list = []
    result = {}

    print requested_movie

    # If an id was passed from API.ai skip possible matches lookup and add by
    # TVDB id to Radarr.
    if 'tmdb_id' in requested_movie:
        # Retrieve JSON result from TVDB by TVDB id
        requested_movie_match = lookupMovieByTmdbId(int(requested_movie['tmdb_id']))
        result = addMovieToWatchList(requested_movie_match)
    else:
        # Query TVDB for any possible matches by the series_name
        possible_matches = lookupMovieByName(requested_movie['media_title'])

        if len(possible_matches) == 0: # If no matches, return result
            text_response = 'Whoops! Radarr was unable to find a match for ' + requested_movie['media_title'] + '. Please open Radarr in your browser to add the movie.'
            print 'Text: ' + text_response
            result = commons.generateWebhookResponse('radarr', text_response, context_list)
            print result

        elif len(possible_matches) == 1: # If one match, skip to adding series by Name
            result = addMovieToWatchList(possible_matches)

        else:
            text_response = 'There are ' + str(len(possible_matches)) + ' possible matches. Which one is correct? \n'

            # Add each possible match to response text and create a context with title
            # and the tmdbId (to avoid searching again)
            for index, match in enumerate(possible_matches, start=1):
                text_response += match['title'] + '. \n'
                context_list.append({
                    "name":"possible_match_0" + str(index),
                    "lifespan":2,
                    "parameters":{
                        'title': match['title'],
                        'tmdbId': match['tmdbId']
                    }
                })

                # Generate the webhook response w/ custom messages and contexts
                result = commons.generateWebhookResponse('radarr', text_response, context_list)

    # Returns Webhook result
    return result



# Function: addMovieToWatchList
# Date Created: 29/03/2017
# Author: Todd Johnson
#
# Description: Add the requested series to Radarr
#
# @param requested_movie | STR | The TV Series name
# @param requested_tmdbId | INT | The TV Series TVDB ID
# @param monitored | BOOL | Whether series is to monitored right away.
# @return result | DICT | Webhook Response
def addMovieToWatchList(requested_movie):
    response = ''
    context_list = []

    print requested_movie

    # Check to see if match is already in Radarr
    my_movies = getMovies()

    # for movie in requested_movie:
    # for show in my_movies:
    #     if int(requested_movie['tmdbId']) == int(show['tmdbId']):
    #         print 'Already Added'
    #         response = 'Looks like Radarr is already watching for ' + requested_movie['title']
    #     else:
    data = { # Generate data query
        'tmdbId': int(requested_movie['tmdbId']),
        'title': requested_movie['title'],
        'qualityProfileId': config['radarr']['server']['quality'],
        'titleSlug': requested_movie['titleSlug'],
        'images': requested_movie['images'],
        'monitored': True,
        'path': config['radarr']['server']['root_folder'] + requested_movie['title']
        # 'path': getRootFolderPath() + requested_movie['title']
    }

    # Convert to JSON
    data_json = json.dumps(data)

    # Submit request to API
    r = requests.post(commons.generateApiQuery('radarr', 'movie'), data=data_json)
    parsed_json = json.loads(r.text)

    #  Set user Response
    response = 'Success! ' + requested_movie['title'] + ' has been added to Radarr.'

    # Create Rich Notifications
    # slack_message = {
    #     'attachments': [{
    #         'fallback': response,
    #         "pretext": "Message from Comandarr: " + response,
    #         'author_name': 'Radarr',
    #         "author_link": commons.generateServerAddress('radarr') + '/movies/' + movie['titleSlug'],
    #         "author_icon": config['radarr']['resources']['app_logo'],
    #         'title': 'Imported: ' + movie['title'],
    #         # 'text': movie['overview'],
    #         'color': 'good',
    #         "fields": [
    #             {
    #                 "title": "Number of Seasons",
    #                 "value": str(movie['seasonCount']),
    #                 "short": 'true'
    #             },
    #             {
    #                 "title": "Monitored",
    #                 "value": str(movie['monitored']),
    #                 "short": 'true'
    #             }
    #         ],
    #         "thumb_url": config['radarr']['resources']['app_logo'],
    #     }]
    # }
    context_list = []


    result = commons.generateWebhookResponse('radarr', response, context_list)
    print result
    return result

request_parameters = { # Set required parameters from request
    'media_title': 'Star Wars: The Last Jedi',
    'media_type': 'Movie',
    'request_action': 'download_media',
    'tmdb_id': 181808
}

print confirmMovie(request_parameters)
