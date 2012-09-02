from google.appengine.api import urlfetch
from django.utils import simplejson as json
from UserHandler import User

import logging
import urllib
import Cookie
import time

user_name = 'FallenRGH'
password = 'temporarypassword'
reddit_session_cookie = Cookie.SimpleCookie()

def postStory(game):
    modhash = login()

    time.sleep(2) #don't overload requests

    title, text = getStoryInfo(game)

    url = 'http://www.reddit.com/api/submit'
    payload = urllib.urlencode({'uh':modhash, 'kind':'self', 'text':text, 'sr':'storybook', 'title':title, 'r':'storybook', 'api_type':'json'})
    response = urlfetch.fetch(url, payload, method=urlfetch.POST, headers=getHeaders(reddit_session_cookie))
    json_response = json.loads(response.content)
    logging.debug(response.content)

def login():
    url = 'https://ssl.reddit.com/api/login/' + user_name
    payload = urllib.urlencode({'api_type' : 'json', 'user' : user_name, 'passwd': password})
    response = urlfetch.fetch(url, payload, method=urlfetch.POST, headers=getHeaders(reddit_session_cookie))
    logging.debug(response.content)
    json_response = json.loads(response.content)
    reddit_session_cookie.load(response.headers.get('set-cookie', ''))
    return json_response['json']['data']['modhash']

def getHeaders(cookie=None):
    headers = {'User-Agent': 'Storybook Bot by /u/FallenRGH', 'Cookie': '' if (cookie is None) else getCookieHeaders(cookie)}
    return headers

def getCookieHeaders(cookie):
    cookieHeader = ""
    for value in cookie.values():
        cookieHeader += "%s=%s; " % (value.key, value.value)
    logging.debug('Cookie headers: ' + cookieHeader)
    return cookieHeader

def getStoryInfo(game):
    title = game.end_sentence
    text = ''
    text += '**Authors**:\n\n'
    users = game.users
    scores = game.scores
    userScores = {}
    visibility = {}

    for i in range(0, len(users)):
        user = User.get_by_key_name(users[i])
        users[i] = user.name
        visibility[users[i]] = user.display_type
        userScores[users[i]] = scores[i]

    sortedUsers = sorted(userScores, key=userScores.get, reverse=True)
    sortedVis = sorted(visibility, key=userScores.get, reverse=True)

    for user in sortedUsers:
        text += trimName(user, visibility[user]) + '\n\n'

    text += '\n\n_______________________________________________\n\n' + getStoryString(game)

    return title, text

def getStoryString(game):
    string = game.start_sentence + " ... "
    for s in game.story:
        string += s
    string += " ... " + game.end_sentence
    return string

def trimName(name, display_type):
    logging.debug(name + ' ' + str(display_type))
    split_name = name.partition(' ')
    return_string = ''
    if display_type == 0:
        return 'Anonymous'
    elif display_type == 1:
        for name in split_name:
            return_string += name[0] + '. '
        return return_string
    elif display_type == 2:
        for i in range(0, len(split_name)):
            if i == (len(split_name) - 1):
                return_string += split_name[i][0] + '.'
            else:
                return_string += split_name[i] + ' '
        return return_string
    else:
        for name in split_name:
            return_string += name + ' '
        return return_string

    return (split_name[0] + ' ' + (split_name[2])[0] + '.')
