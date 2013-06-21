import logging
import datetime

from basehandler import BaseHandler
from Models import Game
from storybooklib import getRecentScoreInfo, changeToDisplayPhase
from django.utils import simplejson as json

class VoteCompleteVerification(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical("Invalid vote completion verification detected!")
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            self.response.headers['Content-type'] = 'application/json'
            if not game.can_vote and game.display_phase:
                self.response.headers.add_header('completed', "v")
                recent_winner_string = "\"" + game.winning_sentences[len(game.winning_sentences)-1] + "\" By: " + game.winning_users_names[len(game.winning_users_names) - 1]
                self.response.headers.add_header('recent_winner', recent_winner_string)
            elif datetime.datetime.now() > game.end_vote_time:
                changeToDisplayPhase(game, self)
            else:
                self.response.headers.add_header('completed', "i")
            
            #Update the game data after the recent score data is added
            game = Game.get_by_key_name(game_id)
            response = {}
            response['winning_data'] = getRecentScoreInfo(game)
            self.response.out.write(json.dumps(response))
        return
