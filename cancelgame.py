import logging

from django.utils import simplejson as json
from basehandler import BaseHandler
from Models import Game
from google.appengine.ext import db
from cacheLib import resetPlayerHost, storeCache

class CancelGame(BaseHandler):
    def post(self):
        if self.user:
            info = json.loads(self.request.body)
            game_id = info['game_id']
            user = self.user
            try:
                game = Game.get_by_key_name(game_id)
                #game = retrieveCache(game_id, Game)
                db.delete(game)
                #deleteData(game, game_id)
                user = resetPlayerHost(user.user_id)
                self.user.current_game = None
                storeCache(user, user.user_id)
            except Exception, ex:
                logging.critical(ex)
        else:
            logging.critical('Unauthorized Game Canceling Request Made')
