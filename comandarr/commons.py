# #############################################################################
# File Name: commons.py
# Author: Todd Johnson
# Creation Date: 08/04/2017
#
# Description: [To be completed]
#
# Offical website: https://www.comandarr.github.io
# Github Source: https://www.github.com/comandarr/comandarr/
# Readme Source: https://www.github.com/comandarr/comandarr/README.md
#
# #############################################################################

# Import Required modules
import json
import yaml

# Import User Configurations
from definitions import CONFIG_PATH
config = yaml.safe_load(open(CONFIG_PATH))


# ----------------------------------------------------------------------
# -------------------------- COMMON FUNCTIONS --------------------------


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

    return http + config['sonarr']['server']['addr'] + ':' + \
        str(config['sonarr']['server']['port'])


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
    url = generateServerAddress() + '/api/' + endpoint + '?apikey=' + \
        config['sonarr']['auth']['apikey']

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
def generateWebhookResponse(response, context={}, slack_msg={}, fb_msg={}, \
    tele_msg={}, kik_msg={}):
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
