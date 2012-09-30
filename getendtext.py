import logging

from basehandler import BaseHandler
from storybooklib import getEndText
from Models import Game
from django.utils import simplejson as json

class GetEndText(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical('Invalid end-text attempt detected!')
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            response = {}
            response['end_text'] = getEndText(game)
            self.response.out.write(json.dumps(response))

    return
