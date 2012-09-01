from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from Models import Game
from UserHandler import User
import RedditLib
import datetime
import time

MAX_GAME_CREATION = 10*60
MAX_TIME_INACTIVE = 5*60

class Cleanup(webapp.RequestHandler):
	def get(self):
		query = Game.all()
		games = query.fetch(None)
		cleanupProcess(games)
		return


def cleanupProcess(games):
	for game in games:
		if game.finished:
			postToReddit(game)
			removeGame(game)
			time.sleep(3) #don't overload requests
		else if not game.started:
			if ((datetime.datetime.now() - game.created).seconds) > MAX_GAME_CREATION:
				db.delete(game)		
		else:
			times = []

			if game.created is not None:
				times.append(game.created)
			if game.end_submission_time is not None:
				times.append(game.end_submission_time)
			if game.end_display_time is not None:
				times.append(game.end_display_time)
			if game.end_end_vote_time is not None:
				times.append(end_end_vote_time)

			for i in range(0, len(times)):
				times[i] = (datetime.datetime.now() - times[i]).seconds

			minimum = min(times)
			if minimum > MAX_TIME_INACTIVE:
				db.delete(game)

def removeGame(game):
	game.delete()

def postToReddit(game):
	RedditLib.postStory(game)

routes = [('/cleanup', Cleanup)]
app = webapp.WSGIApplication(routes)
run_wsgi_app(app)
