import Cookie
import base64
import cgi
import conf
import datetime
import hashlib
import hmac
import logging
import time
import traceback
import urllib
import os
import time
import random
import RedditLib
import sys

from FacebookHandler import Facebook
from UserHandler import User
from uuid import uuid4
from google.appengine.dist import use_library
from django.utils import simplejson as json
from google.appengine.api import urlfetch, taskqueue
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import util, template
from google.appengine.runtime import DeadlineExceededError
from google.appengine.ext.webapp.util import run_wsgi_app
from DefaultStartSentences import defaultStart
from DefaultEndSentences import defaultEnd
from types import *
from google.appengine.api import memcache
from cacheLib import retrieveCache, storeCache, deleteData, markPlayerHostedGame, canPlayerHost, resetPlayerHost
from basehandler import BaseHandler
from findgame import FindGame

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '0.96')

SUBMISSION_TIME = 90
DISPLAY_TIME = 20
_USER_FIELDS = u'name,email,picture,friends'
LAST_USED_GAME_ID_KEY = "a45tfyhssert356t"
END_VOTING_TIME = 20
FIRST_PLACE_BONUS = 3
SECOND_PLACE_BONUS = 1
FIRST_PLACE_TIE_BONUS = 2
SECOND_PLACE_TIE_BONUS = 1
MAX_GAME_CREATION = 10*60

def getPlayerNames(game):
    nameList = []
    for user_id in game.users:
        user = retrieveCache(user_id, User)
        nameList.append(trimName(user.name, user.display_type))
        #nameList.append(trimName(retrieveCache(user, User).name))
    return nameList

def resetRecentScoreData(game):
    game.recent_score_data = []
    for user in game.users:
        game.recent_score_data.append(0)

def allUsersVoted(game):
    return (len(game.users) == len(game.users_voted))

def postRedditStory(game):
    RedditLib.postStory(game)
    return

class UserSettings(BaseHandler):
    def get(self):
        if self.user:
            self.render(u'user_settings')
        else:
            self.render(u'login_screen')

class CreateGame(BaseHandler):
    def get(self):
        if self.user:
            self.render(u'create_game')
        else:
            self.render(u'login_screen')

routes = [
    ('/', MenuPage),
    ('/find_game', FindGame),
    ('/game_screen', GameScreen),
    ('/game_status', GameStatus),
    ('/view_lobby', ViewLobby),
    ('/start_game', StartGame),
    ('/start_early', StartEarly),
    ('/submission_complete_verification', SubmissionCompleteVerification),
    ('/get_choices', GetChoices),
    ('/vote', Vote),
    ('/vote_complete_verification', VoteCompleteVerification),
    ('/display_complete_verification', DisplayCompleteVerification),
    ('/end_vote_complete_verification', EndVoteCompleteVerification),
    ('/cast_end_vote', EndVote),
    ('/join_game', JoinGame),
    ('/waiting_to_start', WaitingToStart),
    ('/cancel_game', CancelGame),
    ('/game_deleted_error', GameDeleted),
    ('/leave_before_start', LeaveBeforeStart),
    ('/vote_end_early', VoteEndEarly),
    ('/get_lobby', GetLobby),
    ('/get_visibility', GetVisibility),
    ('/set_visibility', SetVisibility),
    ('/user_settings', UserSettings),
    ('/create_game', CreateGame)
]
app = webapp.WSGIApplication(routes)

def main():
    LastUsedGameID.get_or_insert(LAST_USED_GAME_ID_KEY, game_id=0)

    run_wsgi_app(app)

if __name__ == '__main__':
    main()
