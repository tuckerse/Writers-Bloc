import logging
import datetime

from basehandler import BaseHandler
from Models import Game
from storybooklib import getStoryStringForGameScreen, getScoreInfo, getProfilesAndAFKS, changeToSubmissionPhase
from django.utils import simplejson as json

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
            if (game.num_phases < 10 or game.went_to_submission):
                if not game.display_phase and game.can_submit:
                    self.response.headers.add_header('response', "v")
                    return
                elif datetime.datetime.now() > game.end_display_time:
                    changeToSubmissionPhase(game, self)
                    game.went_to_submission = True
                    game.put()
                    #storeCache(game, game_id)
                    return
                self.response.headers.add_header('response', "i")
                self.response.headers.add_header('updated_story', "")
            else:
                if (not game.display_phase) and game.finished:
                    self.response.headers.add_header('response', "v")
                    return
                elif datetime.datetime.now() > game.end_display_time:
                    finishGame(game)
                    return
                self.response.headers.add_header('response', "i")
        return
