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

def initializeGame(game_id, max_players, start_sentence, end_sentence):
    game_id = getNextGameID()
    newGame = Game(key_name=str(game_id))
    newGame.game_id = game_id
    newGame.created = datetime.datetime.now()
    newGame.can_vote = False
    newGame.story = []
    newGame.users = []
    newGame.current_players = 0
    newGame.num_phases = 1
    newGame.end_sentence = end_sentence
    newGame.start_sentence = start_sentence
    newGame.can_submit = False
    newGame.display_phase = False
    newGame.finished = False
    newGame.started = False
    newGame.users_voted_end_early = []
    newGame.users
    newGame.put()
    #storeCache(newGame, str(game_id))
    return game_id

def getNextGameID():
    previous_game_id = LastUsedGameID.get_by_key_name(LAST_USED_GAME_ID_KEY)
    if previous_game_id.game_id == sys.maxint:
        game_id = 0
    else:
        game_id = previous_game_id.game_id + 1
    previous_game_id.game_id = game_id
    previous_game_id.put()
    return game_id

def resetRecentScoreData(game):
    game.recent_score_data = []
    for user in game.users:
        game.recent_score_data.append(0)

def allUsersVoted(game):
    return (len(game.users) == len(game.users_voted))

def postRedditStory(game):
    RedditLib.postStory(game)
    return

class GameDeleted(BaseHandler):
    def get(self):
        self.render(u'game_deleted')

class LeaveBeforeStart(BaseHandler):
    def post(self):
        info = json.loads(self.request.body)
        game_id = info['game_id']
        user_id = info['user_id']
        removeUser(game_id, user_id)

def removeUser(game_id, user_id):
    game = Game.get_by_key_name(game_id)
    try:
        game.users.remove(user_id)
        game.current_players = game.current_players - 1
        game.put()
        #storeCache(game, str(game.game_id))
    except Exception, ex:
        logging.critical(ex)

class VoteEndEarly(BaseHandler):
    def post(self):
        if self.user:
            info = json.loads(self.request.body)
            game_id = info['game_id']
            user_id = self.user.user_id
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if not user_id in game.users_voted_end_early:
                game.users_voted_end_early.append(user_id)
            #storeCache(game, game_id)
            game.put()
            returnData = {'success': True}
            self.response.out.write(json.dumps(returnData))
            return
        else:
            logging.critical("Unauthorized vote early attempt")

class GetLobby(BaseHandler):
    def post(self):
        if self.user:
            games = getLobbyGames()
            response = {'games':[]}
            for game in games:
                response['games'].append({'game_id':game.game_id, 'current_players':game.current_players, 'end_sentence':game.end_sentence})
            self.response.out.write(json.dumps(response))
        else:
            logging.critical("Unauthorized lobby post request")

class GetVisibility(BaseHandler):
    def post(self):
        if self.user:
            response_info = {'visibility': self.user.display_type}
            self.response.out.write(json.dumps(response_info))
            logging.debug(json.dumps(response_info))
        else:
            logging.critical('Unauthorized visibility check')
        return

class SetVisibility(BaseHandler):
    def post(self):
        if self.user:
            info = json.loads(self.request.body)
            self.user.display_type = int(info['visibility'])
            storeCache(self.user, self.user.user_id)
            response_info = {'success': True}
            self.response.out.write(json.dumps(response_info))
            logging.debug(json.dumps(response_info))
        else:
            logging.critical('Unauthorized visibility set attempt')

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
