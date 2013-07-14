import logging
import datetime

from basehandler import BaseHandler
from Models import Game
from cacheLib import retrieveCache
from UserHandler import User
from storybooklib import trimName, getStoryStringForGameScreen
from django.utils import simplejson as json

class GetWinner(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical("Invalid vote completion verification detected!")
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #:game = retrieveCache(game_id, Game)
            self.response.headers['Content-type'] = 'application/json'
            score = max(game.scores)
            index = game.scores.index(score)
            winner_id = game.users[index]
            user = retrieveCache(str(winner_id), User)
            winner = trimName(user.name, user.display_type)
            updatedStory = getStoryStringForGameScreen(game)
            response = {}
            response['winner'] = winner
            response['points'] = score
            response['updatedStory'] = updatedStory
            self.response.out.write(json.dumps(response))
        return
