import logging

from basehandler import BaseHandler
from Models import Game
from django.utils import simplejson as json
from storybooklib import checkForDoubleSubmissions

class GetChoices(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical('Invalid choice fetching detected!')
        else:
            info = json.loads(self.request.body)
            game_id = str(info['game_id'])
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            game = checkForDoubleSubmissions(game)
            json_string = json.dumps({"choices": game.next_parts})
            self.response.out.write(json_string);

        return
