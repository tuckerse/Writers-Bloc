import logging

from basehandler import BaseHandler
from django.utils import simplejson as json
from storybooklib import joinGame

class JoinGame(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical('Invalid game join attempt')
        else:
            info = json.loads(self.request.body)
            game_id = info['game_id']
            joined = joinGame(self.user, game_id)
            response = {}
            response['valid'] = "v" if joined else "i"
            self.response.out.write(json.dumps(response))
        return
