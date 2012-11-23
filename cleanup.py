from google.appengine.ext import db, webapp
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.util import run_wsgi_app
from Models import Game
from google.appengine.api import memcache
from UserHandler import User
from cacheLib import deleteData
from storybooklib import MAX_GAME_CREATION

import RedditLib
import datetime
import time

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
            #postToReddit(game)
            #removeGame(game)
            taskqueue.add(url='/clean_games', params={'game_id':game.game_id}, queue_name='redditqueue')
            #time.sleep(3) #don't overload requests

        elif not game.started:
            if ((datetime.datetime.now() - game.created).seconds) > MAX_GAME_CREATION:
                removeGame(game)

        else:
            times = []

            if game.created is not None:
                times.append(game.created)
            if game.end_submission_time is not None:
                times.append(game.end_submission_time)
            if game.end_display_time is not None:
                times.append(game.end_display_time)
            if game.end_end_vote_time is not None:
                times.append(game.end_end_vote_time)

            for i in range(0, len(times)):
                times[i] = (datetime.datetime.now() - times[i]).seconds

            minimum = min(times)

            if minimum > MAX_TIME_INACTIVE:
                removeGame(game)


def removeGame(game):
    deleteData(game, str(game.game_id))

def postToReddit(game):
    RedditLib.postStory(game)

class CleanGames(webapp.RequestHandler):
    def post(self):
        game_id = self.request.get('game_id')
        game = Game.get_by_key_name(game_id)
        postToReddit(game)
        removeGame(game)

routes = [('/cleanup', Cleanup),
          ('/clean_games', CleanGames)]
app = webapp.WSGIApplication(routes)
run_wsgi_app(app)
