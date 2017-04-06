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

# VERSION: '0.1.0'

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print('Request: ')
    print(json.dumps(req, indent=4))
    sendAnalyticsReport(req)

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def processRequest(request):
    media_title = request['result']['parameters']['media-title']
    media_type = request['result']['parameters']['media-type']
    action = request['result']['action']

    data = []

    # Based on Action. call the appropriate function.
    if action == 'download_media':
        if media_type == 'Series':
            data = sonarr.confirmSeries(media_title, media_type)
        elif media_type == 'Movie':
            data = radarr.addSeriesToWatchList(media_title, media_type)
    elif action == 'download_media_confirm':
        if media_type == 'Series':
            for context in request['result']['contexts']:
                if 'title' in context['parameters']:
                    if context['parameters']['title'] == media_title:
                        data = sonarr.confirmSeries(media_title, media_type, context['parameters']['tvdbId'])


    res = makeWebhookResult(data)

    print data
    return res


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


def makeWebhookResult(result):
    return result



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print('Starting app on port %d' % port)

    app.run(debug=False, port=port, host='0.0.0.0')
