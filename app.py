import json
import requests
import os
import yaml

from flask import Flask
from flask import request
from flask import make_response

from comandarr import sonarr
from comandarr import radarr
from comandarr import lidarr

from definitions import CONFIG_PATH

config = yaml.safe_load(open(CONFIG_PATH))
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    # print('Request: ')
    # print(json.dumps(req, indent=4))
    sendAnalyticsReport(req)

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def processRequest(request):
    processed_data = [] # Store the processed data

    # Set decision making variables from request
    media_title = request['result']['parameters']['media-title']
    media_type = request['result']['parameters']['media-type']
    request_action = request['result']['action']
    context_list = request['result']['contexts']

    request_parameters = { # Set required parameters from request
        'media_title': media_title,
        'media_type': media_type,
        'request_action': request_action,
    }


    if request_action == 'download_media' or request_action == 'download_media_confirm':

        # If the title matches a possible match, append TVDB Id to request_parameters
        for context in context_list:
            if 'title' in context['parameters']:
                if context['parameters']['title'] == media_title:
                    request_parameters['tvdb_id'] = context['parameters']['tvdbId']

        # Perform Confirmation based on media type
        if media_type == 'Series':
            processed_data = sonarr.confirmSeries(request_parameters)
        elif media_type == 'Movie':
            processed_data = radarr.confirmMovie(request_parameters)


    return processed_data



def sendAnalyticsReport(sent_data):
    if config['comandarr']['analytics']['enable']:
        # if config['comandarr']['analytics']['keys']
        processed_data = {
            'message': json.dumps(sent_data)
        }
        headers = {'Authorization': 'Token ' + config['comandarr']['analytics']['keys']['google']}
        req = requests.post('https://botanalytics.co/api/v1/messages/user/google-assistant/', data=processed_data, headers=headers)
        print 'Sent Analytics'
        print req.text



if __name__ == '__main__':
    port = int(os.getenv('PORT', 7676))

    print('Starting app on port %d' % port)

    app.run(debug=True, port=port, host='0.0.0.0')
