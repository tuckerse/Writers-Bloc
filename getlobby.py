import logging

from basehandler import BaseHandler
from storybooklib import getLobbyGames
from django.utils import simplejson as json

class GetLobby(BaseHandler):
    def post(self):
        if self.user:
            games = getLobbyGames()
            response = {'games':[]}
            for game in games:
                response['games'].append({
                    'game_id':game.game_id,
                    'current_players':game.current_players,
                    'end_sentence':game.end_sentence
                })
            self.response.out.write(json.dumps(response))
        else:
            logging.critical("Unauthorized lobby post request")
