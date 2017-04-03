import json
import requests
import os

from flask import Flask
from flask import request
from flask import make_response

import sonarr
import radarr

app = Flask(__name__)

# VERSION: '0.1.0'

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    # print('Request: ')
    # print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def processRequest(request):
    media_type = request['result']['parameters']['media-type']
    action = request['result']['action']

    data = []

    # Sonarr Requests (TV Series)
    if action == 'download_media':
        if media_type == 'Series':
            data = sonarr.confirmSeries(request['result']['parameters']['media-title'])
            # data = sonarr.addSeriesToWatchList(request['result']['parameters']['media-title'])
        elif media_type == 'Movie':
            data = radarr.addSeriesToWatchList(request['result']['parameters']['media-title'])

    # Radarr Request (Movies)
    if action == 'add_movie':
        data = []

    res = makeWebhookResult(data)

    print data
    return res



def makeWebhookResult(result):
    return result



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print('Starting app on port %d' % port)

    app.run(debug=False, port=port, host='0.0.0.0')
