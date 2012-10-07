import logging

from basehandler import BaseHandler
from django.utils import simplejson as json
from storybooklib import getScoreInfo, getProfilesAndAFKS
from Models import Game

class UpdateUserInfo(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical("Invalid user info request detected")
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            response = {}
            self.response.headers['Content-type'] = 'application/json'
            response['scores'] = getScoreInfo(game)
            response['profiles'], response['afks'] = getProfilesAndAFKS(response['scores'])
            self.response.out.write(json.dumps(response))

        return
