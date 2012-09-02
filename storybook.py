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

class DisplayCompleteVerification(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical("Invalid display completion verification detected!")
            return
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            response = {}
            self.response.headers['Content-type'] = 'application/json'
            response['updated_story'] = getStoryStringForGameScreen(game)
            response['scores'] = getScoreInfo(game)
            response['profiles'], response['afks'] = getProfilesAndAFKS(response['scores'])
            self.response.out.write(json.dumps(response))
            if (game.num_phases < 10 or game.went_to_submission) and (len(game.users_voted_end_early) < len(game.users)/2):
                if not game.display_phase and game.can_submit:
                    self.response.headers.add_header('response', "v")
                    logging.debug(self.response.headers)
                    return
                elif datetime.datetime.now() > game.end_display_time:
                    changeToSubmissionPhase(game, self)
                    game.went_to_submission = True
                    game.put()
                    #storeCache(game, game_id)
                    logging.debug(self.response.headers)
                    return
                self.response.headers.add_header('response', "i")
                self.response.headers.add_header('updated_story', "")
            else:
                if (not game.display_phase) and game.end_voting:
                    self.response.headers.add_header('response', "v")
                    logging.debug(self.response.headers)
                    return
                elif datetime.datetime.now() > game.end_display_time:
                    changeToEndVotingPhase(game, self)
                    logging.debug(self.response.headers)
                    return
                self.response.headers.add_header('response', "i")
        logging.debug(self.response.headers)
        return

def getProfilesAndAFKS(scoreList):
    profiles = []
    afks = []
    for entry in scoreList:
        user_id = entry['user_id']
        #user = User.get_by_key_name(user_id)
        user = retrieveCache(user_id, User)
        profiles.append(user.picture)
        if user.rounds_afk >= 2:
            afks.append(True)
        else:
            afks.append(False)

    return profiles, afks

class EndVote(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical('Invalid end-vote attempt detected!')
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if (self.user.user_id in game.users) and not (int(self.user.user_id) in game.end_users_voted) and game.end_voting:
                choice = int(self.request.get('selection'))
                game.end_users_voted.append(self.user.user_id)
                game.end_votes.append(choice)
                game.put()
                #storeCache(game, game_id)
                self.response.headers.add_header('response', "s")
                return

        self.response.headers.add_header('response', "n")
        return

class EndVoteCompleteVerification(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical("Invalid end-vote completion verification detected!")
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if (not game.end_voting and game.can_submit) or (not game.end_voting and game.finished):
                self.response.headers.add_header('response', "e" if game.finished else "c")
                return
            elif datetime.datetime.now() > game.end_end_vote_time:
                outcome = finishGameTally(game)
                if outcome:
                    finishGame(game)
                    self.response.headers.add_header('response', "e")
                    return
                else:
                    changeToSubmissionPhase(game, self)
                    self.response.headers.add_header('response', "c")
                    return
            self.response.headers.add_header('response', "q")
        return

class WaitingToStart(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            game_id = self.request.get('game_id')
            user_id = self.user.user_id
            self.render(u'waiting_to_start', game_id=game_id, MAX_PLAYERS=MAX_PLAYERS, user_id=user_id)

        return

def getPlayerNames(game):
    nameList = []
    for user_id in game.users:
        user = retrieveCache(user_id, User)
        nameList.append(trimName(user.name, user.display_type))
        #nameList.append(trimName(retrieveCache(user, User).name))
    return nameList

class JoinGame(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical('Invalid game join attempt')
        else:
            info = json.loads(self.request.body)
            game_id = info['game_id']
            joined = joinGame(self.user, game_id)
            response = {}
            response['valid'] = "v" if joined else "i"
            self.response.out.write(json.dumps(response))
        return

class MenuPage(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            self.render(u'menu_screen')

class VoteCompleteVerification(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical("Invalid vote completion verification detected!")
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            self.response.headers['Content-type'] = 'application/json'
            if not game.can_vote and game.display_phase:
                self.response.headers.add_header('completed', "v")
                recent_winner_string = "\"" + game.winning_sentences[len(game.winning_sentences)-1] + "\" By: " + game.winning_users_names[len(game.winning_users_names) - 1]
                self.response.headers.add_header('recent_winner', recent_winner_string)
            elif datetime.datetime.now() > game.end_vote_time:
                markAFKS(game, game.users_voted)
                changeToDisplayPhase(game, self)
            else:
                self.response.headers.add_header('completed', "i")
            response = {}
            response['winning_data'] = getRecentScoreInfo(game)
            self.response.out.write(json.dumps(response))
        return

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

def getStoryString(game):
    string = game.start_sentence + " ... "
    for s in game.story:
        string += s
    string += " ... " + game.end_sentence
    return string

def getStoryStringForGameScreen(game):
    string = game.start_sentence + " ...<br><br><br>"
    for s in game.story:
        string += s + ' '
    string += "<br><br><br>... " + game.end_sentence
    return string

def clearPhaseInformation(game):
    game.next_parts = []
    game.users_next_parts = []
    game.votes = []
    game.users_voted = []
    game.num_phases = game.num_phases + 1

def finishGameTally(game):
    #true is finished
    removeAFKVotes(game)
    count_no = game.end_votes.count(0)
    count_yes = game.end_votes.count(1)
    if count_yes > count_no:
        return True
    return False

def removeAFKVotes(game):
    for user_id in game.users:
        user = retrieveCache(user_id, User)
        if user.rounds_afk >= 2:
            if user_id in game.end_users_voted:
                index = game.end_users_voted.index(user_id)
                del game.end_users_voted[index]
                del game.end_votes[index]

    game.put()


def getScoreInfo(game):
    scores = []
    haveUsed = []
    for i in range(0, len(game.users)):
        user_id = game.users[i]
        #user = User.get_by_key_name(user_id)
        user = retrieveCache(user_id, User)
        temp = {}
        temp['user_name'] = trimName(user.name, user.display_type)
        temp['user_id'] = user_id
        temp['score'] = game.scores[i]
        scores.append(temp)

    scores = sortByScore(scores)
    for i in range(0, len(scores)):
        (scores[i])['position'] = i+1

    return scores

def getRecentScoreInfo(game):
    scores = []

    for i in range(0, len(game.users)):
        user_id = game.users[i]
        #user = User.get_by_key_name(user_id)
        user = retrieveCache(user_id, User)
        temp = {}
        temp['user_name'] = trimName(user.name, user.display_type)
        temp['score'] = game.recent_score_data[i]
        submitted = game.users_next_parts.count(user_id) > 0
        if submitted:
            temp['sentence'] = game.next_parts[game.users_next_parts.index(user_id)]
        else:
            temp['sentence'] = 'User did not submit'
        scores.append(temp)

    scores = sortByScore(scores)
    for i in range(0, len(scores)):
        (scores[i])['position'] = i+1

    return scores

def sortByScore(scores):
    return quicksort(scores)

def quicksort(L):
    pivot = 0
    if len(L) > 1:
        pivot = random.randrange(len(L))
        elements = L[:pivot]+L[pivot+1:]
        left  = [element for element in elements if element > L[pivot]]
        right =[element for element in elements if element <= L[pivot]]
        return quicksort(left)+[L[pivot]]+quicksort(right)
    return L


def resetRecentScoreData(game):
    game.recent_score_data = []
    for user in game.users:
        game.recent_score_data.append(0)

def changeToSubmissionPhase(game, request_handler = None):
    game.can_submit = True
    game.can_vote = False
    game.end_voting = False
    game.can_vote = False
    game.end_submission_time = datetime.datetime.now() + datetime.timedelta(seconds=SUBMISSION_TIME)
    game.display_phase = False
    game.end_users_voted = []
    game.end_votes = []
    clearPhaseInformation(game)
    if not request_handler == None:
        request_handler.response.headers.add_header('response', "v")
    game.put()
    #storeCache(game, str(game.game_id))

def changeToEndVotingPhase(game, request_handler = None):
    game.end_voting = True
    game.can_vote = False
    game.end_end_vote_time = datetime.datetime.now() + datetime.timedelta(seconds=END_VOTING_TIME)
    game.display_phase = False
    if not request_handler == None:
        request_handler.response.headers.add_header('response', "v")
    game.put()
    #storeCache(game, str(game.game_id))

def allUsersVoted(game):
    return (len(game.users) == len(game.users_voted))

def finishGame(game):
    game.finished = True
    game.game_ended = datetime.datetime.now()
    game.put()
    #storeCache(game, str(game.game_id))

def postRedditStory(game):
    RedditLib.postStory(game)
    return

class CreateSampleGame(BaseHandler):
    def get(self):
        game = Game(key_name="69")
        game.game_id = 69
        game.can_vote = False
        game.current_players = 3
        game.story = ['The first sentence.', 'The second sentence.', 'The third sentence.', 'The fourth sentence.', 'The fifth sentence.']
        game.users = [u'100000041224382', u'100000945793839', u'100004050465254']
        game.next_parts = []
        game.users_next_parts = []
        game.started = False
        game.end_submission_time = None
        game.end_display_time = None
        game.can_submit = False
        game.end_vote_time = None
        game.end_sentence = 'And such was the final sentence.'
        game.votes = []
        game.users_voted = []
        game.display_phase = False
        game.end_display_time = None
        game.winning_sentences = []
        game.winning_users = []
        game.winning_users_names = []
        game.num_phases = 11
        game.finished = True
        game.end_voting = False
        game.end_users_voted = []
        game.end_votes = []
        game.end_end_vote_time = None
        game.game_ended = None
        game.scores = [15L, 35L, 4L]
        game.recent_score_data = []
        game.went_to_submission = False
        game.put()
        #storeCache(game, str(game.game_id))
        return

class CancelGame(BaseHandler):
    def post(self):
        if self.user:
            info = json.loads(self.request.body)
            game_id = info['game_id']
            try:
                game = Game.get_by_key_name(game_id)
                #game = retrieveCache(game_id, Game)
                db.delete(game)
                #deleteData(game, game_id)
                resetPlayerHost(self.user.user_id)
            except Exception, ex:
                logging.critical(ex)
        else:
            logging.critical('Unauthorized Game Canceling Request Made')

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
                ('/create_sample_game', CreateSampleGame),
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
