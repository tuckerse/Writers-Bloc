import logging
import datetime

from basehandler import BaseHandler
from django.utils import simplejson as json
from Models import Game
from storybooklib import changeToVotingPhase, jsonLoad

class SubmissionCompleteVerification(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical("Invalid submission completion verification detected!")
        else:
            info = jsonLoad(self.request.body)
            game_id = str(info['game_id'])
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if game is None:
                self.response.headers.add_header('completed', "d")
                return
            if not game.can_submit and game.can_vote:
                self.response.headers.add_header('completed', "v")
                return
            elif datetime.datetime.now() > game.end_submission_time:
                changeToVotingPhase(game, self)
                return
            self.response.headers.add_header('completed', "i")
        return
