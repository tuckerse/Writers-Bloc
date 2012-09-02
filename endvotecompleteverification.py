import logging
import datetime

from basehandler import BaseHandler
from Models import Game
from storybooklib import finishGameTally, finishGame, changeToSubmissionPhase

class EndVoteCompleteVerification(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical("Invalid end-vote completion verification detected!")
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if (not game.end_voting and game.can_submit) or (not game.end_voting and game.finished):
                self.response.headers.add_header('response', "e" if game.finished else "c")
                return
            elif datetime.datetime.now() > game.end_end_vote_time:
                outcome = finishGameTally(game)
                if outcome:
                    finishGame(game)
                    self.response.headers.add_header('response', "e")
                    return
                else:
                    changeToSubmissionPhase(game, self)
                    self.response.headers.add_header('response', "c")
                    return
            self.response.headers.add_header('response', "q")
        return
