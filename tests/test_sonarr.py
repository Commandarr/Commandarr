# #############################################################################
# File Name: test_sonarr.py
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

# import pytest
# import yaml
# from comandarr import sonarr
#
# from definitions import CONFIG_PATH
# config = yaml.safe_load(open(CONFIG_PATH))
#
#
# def test_lookupSeriesByName():
#     assert sonarr.lookupSeriesByName('Futurama') == [{u'certification': u'TV-14', u'overview': u'A late 20th-century New York City pizza delivery boy, Philip J. Fry, after being unwittingly cryogenically frozen for one thousand years, finds employment at Planet Express, an interplanetary delivery company in the 31st century.', u'airTime': u'22:00', u'firstAired': u'1999-03-27T14:00:00Z', u'tvRageId': 3628, u'year': 1999, u'images': [{u'coverType': u'fanart', u'url': u'http://thetvdb.com/banners/fanart/original/73871-21.jpg'}, {u'coverType': u'banner', u'url': u'http://thetvdb.com/banners/graphical/73871-g15.jpg'}, {u'coverType': u'poster', u'url': u'http://thetvdb.com/banners/posters/73871-2.jpg'}], u'ratings': {u'votes': 613, u'value': 8.8}, u'genres': [u'Animation', u'Comedy', u'Science-Fiction'], u'monitored': False, u'network': u'Comedy Central (US)', u'title': u'Futurama', u'remotePoster': u'http://thetvdb.com/banners/posters/73871-2.jpg', u'seasonCount': 7, u'seriesType': u'standard', u'status': u'ended', u'added': u'0001-01-01T00:00:00Z', u'tvdbId': 73871, u'tags': [], u'imdbId': u'tt0149460', u'seasonFolder': False, u'cleanTitle': u'futurama', u'sortTitle': u'futurama', u'seasons': [{u'monitored': False, u'seasonNumber': 0}, {u'monitored': False, u'seasonNumber': 1}, {u'monitored': False, u'seasonNumber': 2}, {u'monitored': False, u'seasonNumber': 3}, {u'monitored': False, u'seasonNumber': 4}, {u'monitored': False, u'seasonNumber': 5}, {u'monitored': False, u'seasonNumber': 6}, {u'monitored': False, u'seasonNumber': 7}], u'useSceneNumbering': False, u'titleSlug': u'futurama', u'qualityProfileId': 0, u'profileId': 0, u'runtime': 20, u'tvMazeId': 538}]
#
#
# def test_lookupSeriesByTvdbId():
#     assert sonarr.lookupSeriesByTvdbId(73871) == [{u'certification': u'TV-14', u'overview': u'A late 20th-century New York City pizza delivery boy, Philip J. Fry, after being unwittingly cryogenically frozen for one thousand years, finds employment at Planet Express, an interplanetary delivery company in the 31st century.', u'airTime': u'22:00', u'firstAired': u'1999-03-27T14:00:00Z', u'tvRageId': 3628, u'year': 1999, u'images': [{u'coverType': u'fanart', u'url': u'http://thetvdb.com/banners/fanart/original/73871-21.jpg'}, {u'coverType': u'banner', u'url': u'http://thetvdb.com/banners/graphical/73871-g15.jpg'}, {u'coverType': u'poster', u'url': u'http://thetvdb.com/banners/posters/73871-2.jpg'}], u'ratings': {u'votes': 613, u'value': 8.8}, u'genres': [u'Animation', u'Comedy', u'Science-Fiction'], u'monitored': False, u'network': u'Comedy Central (US)', u'title': u'Futurama', u'remotePoster': u'http://thetvdb.com/banners/posters/73871-2.jpg', u'seasonCount': 7, u'seriesType': u'standard', u'status': u'ended', u'added': u'0001-01-01T00:00:00Z', u'tvdbId': 73871, u'tags': [], u'imdbId': u'tt0149460', u'seasonFolder': False, u'cleanTitle': u'futurama', u'sortTitle': u'futurama', u'seasons': [{u'monitored': False, u'seasonNumber': 0}, {u'monitored': False, u'seasonNumber': 1}, {u'monitored': False, u'seasonNumber': 2}, {u'monitored': False, u'seasonNumber': 3}, {u'monitored': False, u'seasonNumber': 4}, {u'monitored': False, u'seasonNumber': 5}, {u'monitored': False, u'seasonNumber': 6}, {u'monitored': False, u'seasonNumber': 7}], u'useSceneNumbering': False, u'titleSlug': u'futurama', u'qualityProfileId': 0, u'profileId': 0, u'runtime': 20, u'tvMazeId': 538}]
