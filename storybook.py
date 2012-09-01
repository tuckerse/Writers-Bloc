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
import sys
import time

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
from Models import LastUsedGameID, Game
from DefaultSentences import defaults
from types import *

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '0.96')

MAX_PLAYERS = 8
#SUBMISSION_TIME = 90
#VOTE_TIME = 45
SUBMISSION_TIME = 10
VOTE_TIME = 10
DISPLAY_TIME = 10
_USER_FIELDS = u'name,email,picture,friends'
LAST_USED_GAME_ID_KEY = "a45tfyhssert356t"
DEFAULT_SENTENCES_KEY = "AUIRETI562345345TYI"
END_VOTING_TIME = 20
FIRST_PLACE_BONUS = 3
SECOND_PLACE_BONUS = 1
FIRST_PLACE_TIE_BONUS = 2
SECOND_PLACE_TIE_BONUS = 1

class BaseHandler(webapp.RequestHandler):
    facebook = None
    user = None
    csrf_protect = False

    def initialize(self, request, response):
        """General initialization for every request"""
        super(BaseHandler, self).initialize(request, response)

        try:
            self.init_facebook()
            self.init_csrf()
            self.response.headers[u'P3P'] = u'CP=HONK'  # iframe cookies in IE
        except Exception, ex:
            self.log_exception(ex)
            raise

    def handle_exception(self, ex, debug_mode):
        """Invoked for unhandled exceptions by webapp"""
        self.log_exception(ex)

    def log_exception(self, ex):
        """Internal logging handler to reduce some App Engine noise in errors"""
        msg = ((str(ex) or ex.__class__.__name__) +
                u': \n' + traceback.format_exc())
        if isinstance(ex, urlfetch.DownloadError) or \
           isinstance(ex, DeadlineExceededError) or \
           isinstance(ex, CsrfException) or \
           isinstance(ex, taskqueue.TransientError):
            logging.warn(msg)
        else:
            logging.error(msg)

    def set_cookie(self, name, value, expires=None):
        """Set a cookie"""
        if value is None:
            value = 'deleted'
            expires = datetime.timedelta(minutes=-50000)
        jar = Cookie.SimpleCookie()
        jar[name] = value
        jar[name]['path'] = u'/'
        if expires:
            if isinstance(expires, datetime.timedelta):
                expires = datetime.datetime.now() + expires
            if isinstance(expires, datetime.datetime):
                expires = expires.strftime('%a, %d %b %Y %H:%M:%S')
            jar[name]['expires'] = expires
        self.response.headers.add_header(*jar.output().split(u': ', 1))

    def render(self, name, **data):
        """Render a template"""
        if not data:
            data = {}
        data[u'js_conf'] = json.dumps({
            u'appId': conf.FACEBOOK_APP_ID,
            u'canvasName': conf.FACEBOOK_CANVAS_NAME,
            u'userIdOnServer': self.user.user_id if self.user else None,
        })
        data[u'logged_in_user'] = self.user
        data[u'message'] = self.get_message()
        data[u'csrf_token'] = self.csrf_token
        data[u'canvas_name'] = conf.FACEBOOK_CANVAS_NAME
        self.response.out.write(template.render(
            os.path.join(
                os.path.dirname(__file__), 'templates', name + '.html'),
            data))

    def init_facebook(self):
        """Sets up the request specific Facebook and User instance"""
        facebook = Facebook()
        user = None

        # initial facebook request comes in as a POST with a signed_request
        if u'signed_request' in self.request.POST:
            facebook.load_signed_request(self.request.get('signed_request'))
            # we reset the method to GET because a request from facebook with a
            # signed_request uses POST for security reasons, despite it
            # actually being a GET. in webapp causes loss of request.POST data.
            self.request.method = u'GET'
            self.set_cookie(
                'u', facebook.user_cookie, datetime.timedelta(minutes=1440))
        elif 'u' in self.request.cookies:
            facebook.load_signed_request(self.request.cookies.get('u'))

        # try to load or create a user object
        if facebook.user_id:
            user = User.get_by_key_name(facebook.user_id)
            if user:
                # update stored access_token
                if facebook.access_token and \
                        facebook.access_token != user.access_token:
                    user.access_token = facebook.access_token
                    user.put()
                # refresh data if we failed in doing so after a realtime ping
                if user.dirty:
                    user.refresh_data()
                # restore stored access_token if necessary
                if not facebook.access_token:
                    facebook.access_token = user.access_token

            if not user and facebook.access_token:
                me = facebook.api(u'/me', {u'fields': _USER_FIELDS})
                try:
                    friends = [user[u'id'] for user in me[u'friends'][u'data']]
                    user = User(key_name=facebook.user_id,
                        user_id=facebook.user_id, friends=friends,
                        access_token=facebook.access_token, name=me[u'name'],
                        email=me.get(u'email'), picture=me[u'picture'])
                    user.put()
                except KeyError, ex:
                    pass # ignore if can't get the minimum fields

        self.facebook = facebook
        self.user = user

    def init_csrf(self):
        """Issue and handle CSRF token as necessary"""
        self.csrf_token = self.request.cookies.get(u'c')
        if not self.csrf_token:
            self.csrf_token = str(uuid4())[:8]
            self.set_cookie('c', self.csrf_token)
        if self.request.method == u'POST' and self.csrf_protect and \
                self.csrf_token != self.request.POST.get(u'_csrf_token'):
            raise CsrfException(u'Missing or invalid CSRF token.')

    def set_message(self, **obj):
        """Simple message support"""
        self.set_cookie('m', base64.b64encode(json.dumps(obj)) if obj else None)

    def get_message(self):
        """Get and clear the current message"""
        message = self.request.cookies.get(u'm')
        if message:
            self.set_message()  # clear the current cookie
            return json.loads(base64.b64decode(message))

class CsrfException(Exception):
    pass

class DisplayCompleteVerification(BaseHandler):
	def post(self):
		if not self.user:
			logging.critical("Invalid display completion verification detected!")
			return
		else:
			game_id = self.request.get('game_id')
			game = Game.get_by_key_name(game_id)
			response = {}
			self.response.headers['Content-type'] = 'application/json'
			response['updated_story'] = getStoryString(game)
			response['scores'] = getScoreInfo(game)
			self.response.out.write(json.dumps(response))
			if game.num_phases < 10:		
				if not game.display_phase and game.can_submit:
					self.response.headers.add_header('response', "v")
					return
				elif datetime.datetime.now() > game.end_display_time:
					game.can_submit = True
					game.can_vote = False
					game.end_submission_time = datetime.datetime.now() + datetime.timedelta(seconds=SUBMISSION_TIME)
					game.display_phase = False
					clearPhaseInformation(game)
					game.put()
					self.response.headers.add_header('response', "v")
					return
				self.response.headers.add_header('response', "i")
				self.response.headers.add_header('updated_story', "")
			else:
				if (not game.display_phase) and game.end_voting:
					self.response.headers.add_header('response', "v")
					return
				elif datetime.datetime.now() > game.end_display_time:
					game.end_voting = True
					game.can_vote = False
					game.end_end_vote_time = datetime.datetime.now() + datetime.timedelta(seconds=END_VOTING_TIME)
					game.display_phase = False
					clearPhaseInformation(game)
					game.put()
					self.response.headers.add_header('response', "v")
					return
				self.response.headers.add_header('response', "i")
		return
class EndVote(BaseHandler):
	def post(self):
		if not self.user:
			logging.critical('Invalid end-vote attempt detected!')
		else:
			game_id = self.request.get('game_id')
			game = Game.get_by_key_name(game_id)
			if (self.user.user_id in game.users) and not (int(self.user.user_id) in game.end_users_voted) and game.end_voting:
				choice = int(self.request.get('selection'))
				game.end_users_voted.append(int(self.user.user_id))
				game.end_votes.append(choice)
				game.put()
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
				if (not game.end_voting and game.can_submit) or (not game.end_voting and game.finished):
					self.response.headers.add_header('response', "e" if game.finished else "c")
					return
				elif datetime.datetime.now() > game.end_end_vote_time:
					outcome = finishGameTally(game)
					if outcome:
						game.finished = True
						game.game_ended = datetime.datetime.now()
						game.put()
						self.response.headers.add_header('response', "e")
						return
					else:
						game.can_submit = True
						game.end_voting = False
						game.can_vote = False
						game.end_voting = False
						game.end_submission_time = datetime.datetime.now() + datetime.timedelta(seconds=SUBMISSION_TIME)
						game.display_phase = False
						game.end_users_voted = []
						end_votes = []
						game.put()
						self.response.headers.add_header('response', "c")
						return
				self.response.headers.add_header('response', "q")		
			return

class FindGame(BaseHandler):
	def get(self):
		if not self.user:
			self.render(u'login_screen')
		else:
			game_id = findGame(self.user)

			if game_id is None:
				self.redirect("/")
				return

			self.render(u'waiting_to_start', game_id=game_id, MAX_PLAYERS=MAX_PLAYERS)
			
		return

class GameScreen(BaseHandler):
	def get(self):
		game_id = self.request.get('game_id')
		game = Game.get_by_key_name(str(game_id))
		self.response.headers['Content-type'] = 'text/html'
		if not self.user:
			self.render(u'login_screen')
		else:
			names = getUserInfo(game_id)
			self.render(u'game_screen', game_id=game_id, name_list=names, user_id=self.user.user_id, end_sentence=game.end_sentence)
		return

	def post(self):
		if not self.user:
			logging.critical("Invalid part submission detected!")
		else:
			info = json.loads(self.request.body)
			game_id = info['game_id']
			game = Game.get_by_key_name(str(game_id))
			if self.user.user_id in game.users and not int(self.user.user_id) in game.users_next_parts and game.can_submit:
				next_part = info['next_part']
				game = Game.get_by_key_name(str(game_id))
				game.next_parts.append(next_part)
				game.users_next_parts.append(int(self.user.user_id))
				game.put()
				self.response.headers.add_header('success', 's')
			else:
				self.response.headers.add_header('success', 'f')
		return

class GameStatus(webapp.RequestHandler):
	def post(self):
		info = json.loads(self.request.body)
		game_id = info['game_id']
		response_info = {}
		game = Game.get_by_key_name(str(game_id))
		response_info['started'] = "y" if game.started else "n"
		response_info['num_players'] = game.current_players
		response_info['num_phases'] = game.num_phases
		self.response.headers['Content-type'] = 'application/json'
		if game.can_vote:
			response_info['phase'] = "v"
			response_info['seconds_left'] = (game.end_vote_time - datetime.datetime.now()).seconds
		elif game.can_submit:
			response_info['phase'] = "s"
			response_info['seconds_left'] = (game.end_submission_time - datetime.datetime.now()).seconds
		elif game.display_phase:
			response_info['phase'] = "d"
			response_info['seconds_left'] = (game.end_display_time - datetime.datetime.now()).seconds
		elif game.end_voting:
			response_info['phase'] = "f"
			response_info['seconds_left'] = (game.end_end_vote_time - datetime.datetime.now()).seconds		

		response = json.dumps(response_info)
		self.response.out.write(response)

		return

class GetChoices(BaseHandler):
	def post(self):
		if not self.user:
			logging.critical('Invalid choice fetching detected!')
		else:
			info = json.loads(self.request.body)
			game_id = str(info['game_id'])
			game = Game.get_by_key_name(game_id)
			json_string = json.dumps({"choices": game.next_parts})
			self.response.out.write(json_string);
			
		return

class MenuPage(BaseHandler):
	def get(self):
		if not self.user:
			self.render(u'login_screen')
		else:
			self.render(u'menu_screen')

class StartEarly(BaseHandler):
	def get(self):
		if not self.user:
			self.render(u'login_screen')
		else:
			game_id = self.request.get('game_id')
			game = Game.get_by_key_name(game_id)
			if not self.user.user_id in game.users:
				self.render(u'error_screen')
			else:
				startGame(game_id)
				self.redirect("/game_screen?" + urllib.urlencode({'game_id':game_id}))
				
		return

class StartGame(BaseHandler):
	def post(self):
		if not self.user:
			self.render(u'login_screen')
		else:
			end_sentence = self.request.get('end_sentence')
			if end_sentence == "":
				end_sentence = defaults.getRandomDefault()
			game_id = initializeGame(getNextGameID(), MAX_PLAYERS, end_sentence)
			joinGame(self.user, game_id)
			self.render(u'game_created_screen', game_id=str(game_id), MAX_PLAYERS=MAX_PLAYERS)
		return

class SubmissionCompleteVerification(BaseHandler):
	def post(self):
		if not self.user:
			logging.critical("Invalid submission completion verification detected!")
		else:
			info = json.loads(self.request.body)
			game_id = str(info['game_id'])
			game = Game.get_by_key_name(game_id)
			if not game.can_submit and game.can_vote:
				self.response.headers.add_header('completed', "v")
				return
			elif datetime.datetime.now() > game.end_submission_time:
				game.can_submit = False
				game.can_vote = True
				game.end_submission_time = None
				resetRecentScoreData(game)
				game.end_vote_time = datetime.datetime.now() + datetime.timedelta(seconds=VOTE_TIME)
				game.put()
				self.response.headers.add_header('completed', "v")
				return
			self.response.headers.add_header('completed', "i")
		
		return

class ViewLobby(BaseHandler):
	def get(self):
		if not self.user:
			self.render(u'login_screen')
		else:
			query = Game.gql("WHERE current_players <:1 ORDER BY current_players DESC", MAX_PLAYERS)
			games = query.fetch(1000000)
			self.render(u'lobby_screen', games=games)
		return

class Vote(BaseHandler):
	def post(self):
		if not self.user:
			logging.critical('Invalid vote attempt detected!')
		else:
			game_id = self.request.get('game_id')
			game = Game.get_by_key_name(game_id)
			if (self.user.user_id in game.users) and not (int(self.user.user_id) in game.users_voted) and game.can_vote:
				choice = int(self.request.get('part_voted'))
				game.users_voted.append(int(self.user.user_id))
				game.votes.append(choice)
				game.put()
				self.response.headers.add_header('response', "s")
				return

		self.response.headers.add_header('response', "n")
		return

class VoteCompleteVerification(BaseHandler):
	def post(self):
		if not self.user:
			logging.critical("Invalid vote completion verification detected!")
		else:
			game_id = self.request.get('game_id')
			game = Game.get_by_key_name(game_id)
			self.response.headers['Content-type'] = 'application/json'
			if not game.can_vote and game.display_phase:
				self.response.headers.add_header('completed', "v")
				recent_winner_string = "\"" + game.winning_sentences[len(game.winning_sentences)-1] + "\" By: " + game.winning_users_names[len(game.winning_users_names) - 1]
				self.response.headers.add_header('recent_winner', recent_winner_string)
			elif datetime.datetime.now() > game.end_vote_time:
				game.can_submit = False
				game.can_vote = False
				game.end_submission_time = None
				game.display_phase = True
				game.end_display_time = datetime.datetime.now() + datetime.timedelta(seconds=DISPLAY_TIME)
				determineWinner(game)
				recent_winner_string = "\"" + game.winning_sentences[len(game.winning_sentences)-1] + "\" By: " + game.winning_users_names[len(game.winning_users_names) - 1]
				self.response.headers.add_header('recent_winner', recent_winner_string)
				game.put()
				self.response.headers.add_header('completed', "v")
			else:
				self.response.headers.add_header('completed', "i")
			response = {}
			response['winning_data'] = getRecentScoreInfo(game)
			self.response.out.write(json.dumps(response))	
		return


def initializeGame(game_id, max_players, end_sentence):
	game_id = getNextGameID()
	newGame = Game(key_name=str(game_id))
	newGame.game_id = game_id
	newGame.can_vote = False
	newGame.story = []
	newGame.users = []
	newGame.current_players = 0
	newGame.num_phases = 1
	newGame.end_sentence = end_sentence
	newGame.can_submit = False
	newGame.display_phase = False
	newGame.finished = False
	newGame.put()
	return game_id

def joinGame(user, game_id):
	result = Game.get_by_key_name(str(game_id))

	if result == None:
		return False
	
	if result.current_players == MAX_PLAYERS:
		return False

	result.users.append(user.user_id)
	result.current_players += 1
	result.put()
	return True

def startGame(game_id):
	game = Game.get_by_key_name(str(game_id))
	if game.started:
		return False

	game.started = True
	current_time = datetime.datetime.now()
	end_submission = current_time + datetime.timedelta(seconds=SUBMISSION_TIME)
	game.end_submission_time = end_submission
	game.can_submit = True
	for user in game.users:
		game.scores.append(0)
	game.put()
	return True	

def findGame(user):
	query = Game.gql("WHERE current_players <:1 ORDER BY current_players ASC", MAX_PLAYERS)
	results = query.fetch(None)
	if len(results) == 0:
		return None

	for result in results:
		if not result.started:
			result.users.append(user.user_id)
			result.current_players += 1
			if result.current_players == MAX_PLAYERS:
				result.started = True
			result.put()
			return result.game_id	
	
	return None

def trimName(name):
	split_name = name.partition(' ')
	return (split_name[0] + ' ' + (split_name[2])[0] + '.')

def getNextGameID():
	previous_game_id = LastUsedGameID.get_by_key_name(LAST_USED_GAME_ID_KEY)
	if previous_game_id.game_id == sys.maxint:
		game_id = 0
	else:
		game_id = previous_game_id.game_id + 1
	previous_game_id.game_id = game_id
	previous_game_id.put()
	return game_id

def getUserInfo(game_id):
	game = Game.get_by_key_name(str(game_id))
	name_list = []
	pic_list = []
	for user_id in game.users:
		user = User.get_by_key_name(user_id)
		name_list.append(trimName(user.name))
	
	return name_list	

def determineWinner(game):
	scores = {}

	for user in game.users:
		scores[user] = 0

	max_votes = 0
	second_place = 0
	second_votes = 0
	winning_index = 0

	for i in range(0, len(game.next_parts)):
		vote_count = game.votes.count(i)		
		scores[str(game.users_next_parts[i])] += vote_count
		if vote_count > max_votes:
			max_votes = vote_count
			winning_index = i

	for i in range(0, len(game.next_parts)):
		if game.votes.count(i) > max_votes and not (i == winning_index):
			second_votes = game.votes.count(i)
			second_place = i

	tie = (max_votes == second_votes)
	if tie:
		scores[str(game.users_next_parts[winning_index])] += FIRST_PLACE_TIE_BONUS
		scores[str(game.users_next_parts[second_place])] += FIRST_PLACE_TIE_BONUS
	else:
		scores[str(game.users_next_parts[winning_index])] += FIRST_PLACE_BONUS
		scores[str(game.users_next_parts[second_place])] += SECOND_PLACE_BONUS

	game.winning_sentences.append(game.next_parts[winning_index])
	game.winning_users.append(game.users_next_parts[winning_index])
	game.winning_users_names.append(trimName((User.get_by_key_name(str(game.users_next_parts[winning_index]))).name))
	game.story.append(game.next_parts[winning_index])

	for i in range(0, len(game.users)):
		game.recent_score_data[i] = scores[game.users[i]]
		game.scores[i] += scores[game.users[i]]

def getStoryString(game):
	string = "" if (len(game.story) == 0) else "    "
	for s in game.story:
		string += s
	string += " ... " + game.end_sentence
	return string

def clearPhaseInformation(game):
	game.next_parts = []
	game.users_next_parts = []
	game.votes = []
	game.users_voted = []
	game.num_phases = game.num_phases + 1

def finishGameTally(game):
	#true is finished
	count_no = game.end_votes.count(0)
	count_yes = game.end_votes.count(1)
	if count_yes > count_no:
		return True
	return False

def getScoreInfo(game):
	scores = []

	for i in range(0, len(game.users)):
		user_id = game.users[i]
		user = User.get_by_key_name(user_id)
		temp = {}
		logging.debug('user id is ' + str(user_id))
		temp['user_name'] = trimName(user.name)
		logging.debug('user_name: ' + trimName(user.name))
		temp['score'] = game.scores[i]
		logging.debug('score: ' + str(game.scores[i]))
		temp['position'] = sorted(game.scores,reverse=True).index(game.scores[i]) + 1
		logging.debug('position: ' + str(sorted(game.scores,reverse=True).index(game.scores[i]) + 1))
		scores.append(temp)

	return scores

def getRecentScoreInfo(game):
	scores = []

	for i in range(0, len(game.users)):
		user_id = game.users[i]
		user = User.get_by_key_name(user_id)
		temp = {}
		temp['user_name'] = trimName(user.name)
		temp['score'] = game.recent_score_data[i]
		temp['position'] = sorted(game.recent_score_data,reverse=True).index(game.recent_score_data[i]) + 1
		temp['sentence'] = game.next_parts[game.users_next_parts.index(int(user_id))]
		scores.append(temp)

	return scores

def resetRecentScoreData(game):
	game.recent_score_data = []
	for user in game.users:
		game.recent_score_data.append(0)
	

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
		('/cast_end_vote', EndVote)
		]
app = webapp.WSGIApplication(routes)

def main():
	LastUsedGameID.get_or_insert(LAST_USED_GAME_ID_KEY, game_id=0)

	run_wsgi_app(app)

if __name__ == '__main__':
	main()		
