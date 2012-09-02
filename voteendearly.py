import logging

from basehandler import BaseHandler
from django.utils import simplejson as json
from Models import GAme

class VoteEndEarly(BaseHandler):
    def post(self):
        if self.user:
            info = json.loads(self.request.body)
            game_id = info['game_id']
            user_id = self.user.user_id
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if not user_id in game.users_voted_end_early:
                game.users_voted_end_early.append(user_id)
            #storeCache(game, game_id)
            game.put()
            returnData = {'success': True}
            self.response.out.write(json.dumps(returnData))
            return
        else:
            logging.critical("Unauthorized vote early attempt")
