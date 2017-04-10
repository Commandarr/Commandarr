import json
import requests
import os
import yaml

from flask import Flask, flash, redirect, render_template, request, session, abort, \
make_response

# from comandarr import sonarr, radarr, lidarr

# from definitions import CONFIG_PATH
#
config = yaml.safe_load(open('config/config.yaml'))
app = Flask(__name__)

# Root of web interface
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == config['comandarr']['auth']['password'] and \
    request.form['username'] == config['comandarr']['auth']['username']:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

# Webhook for API.ai
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
    app.secret_key = os.urandom(12)
    port = int(os.getenv('PORT', 7676))

    print('Starting app on port %d' % port)

    app.run(debug=True, port=port, host='0.0.0.0')
