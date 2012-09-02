import logging
import datetime

from basehandler import BaseHandler
from Models import Game
from helperfunctions import getStoryStringForGameScreen, getScoreInfo, getProfilesAndAFKS, changeToSubmissionPhase, changeToEndVotingPhase

class DisplayCompleteVerification(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical("Invalid display completion verification detected!")
            return
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            response = {}
            self.response.headers['Content-type'] = 'application/json'
            response['updated_story'] = getStoryStringForGameScreen(game)
            response['scores'] = getScoreInfo(game)
            response['profiles'], response['afks'] = getProfilesAndAFKS(response['scores'])
            self.response.out.write(json.dumps(response))
            if (game.num_phases < 10 or game.went_to_submission) and (len(game.users_voted_end_early) < len(game.users)/2):
                if not game.display_phase and game.can_submit:
                    self.response.headers.add_header('response', "v")
                    logging.debug(self.response.headers)
                    return
                elif datetime.datetime.now() > game.end_display_time:
                    changeToSubmissionPhase(game, self)
                    game.went_to_submission = True
                    game.put()
                    #storeCache(game, game_id)
                    logging.debug(self.response.headers)
                    return
                self.response.headers.add_header('response', "i")
                self.response.headers.add_header('updated_story', "")
            else:
                if (not game.display_phase) and game.end_voting:
                    self.response.headers.add_header('response', "v")
                    logging.debug(self.response.headers)
                    return
                elif datetime.datetime.now() > game.end_display_time:
                    changeToEndVotingPhase(game, self)
                    logging.debug(self.response.headers)
                    return
                self.response.headers.add_header('response', "i")
        logging.debug(self.response.headers)
        return
