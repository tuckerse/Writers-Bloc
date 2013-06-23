import logging

from basehandler import BaseHandler
from Models import Game
from django.utils import simplejson as json
from storybooklib import checkForDoubleSubmissions, jsonLoad, whichCantVote
from cacheLib import retrieveCache
from UserHandler import User

class GetChoices(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical('Invalid choice fetching detected!')
        else:
            info = jsonLoad(self.request.body)
            game_id = str(info['game_id'])
            user_id = self.user.user_id
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            game = checkForDoubleSubmissions(game)
            cant_vote = whichCantVote(user_id, game)
            json_string = json.dumps({"choices": game.next_parts, "cant_vote" : cant_vote})
            self.response.out.write(json_string);

        return
