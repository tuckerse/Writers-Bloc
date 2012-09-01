from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from Models import Game
from UserHandler import User
import RedditLib

import time

class Cleanup(webapp.RequestHandler):
	def get(self):
		query = Game.gql("WHERE finished =:1", True)
		games = query.fetch(None)
		cleanupProcess(games)
		return


def cleanupProcess(games):
	for game in games:
		postToReddit(game)
		removeGame(game)
		time.sleep(3) #don't overload requests

def removeGame(game):
	game.delete()

def postToReddit(game):
	RedditLib.postStory(game)

routes = [('/cleanup', Cleanup)]
app = webapp.WSGIApplication(routes)
run_wsgi_app(app)
