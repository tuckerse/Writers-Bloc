import logging

from basehandler import BaseHandler
from Models import Game
from storybooklib import getUserInfo, resetAFK, allUsersSubmitted, changeToVotingPhase
from django.utils import simplejson as json

class GameScreen(BaseHandler):
    def get(self):
        game_id = self.request.get('game_id')
        game = Game.get_by_key_name(str(game_id))
        #game = retrieveCache(str(game_id), Game)
        self.response.headers['Content-type'] = 'text/html'
        if not self.user:
            self.render(u'login_screen')
        else:
            names, pictures = getUserInfo(game_id)
            self.render(u'game_screen', game_id=game_id, user_id=self.user.user_id, end_sentence=game.end_sentence, start_sentence=game.start_sentence, zipList=zip(names,pictures))
        return

    def post(self):
        if not self.user:
            logging.critical("Invalid part submission detected!")
        else:
            info = json.loads(self.request.body)
            game_id = info['game_id']
            game = Game.get_by_key_name(str(game_id))
            #game = retrieveCache(str(game_id), Game)
            if self.user.user_id in game.users and not int(self.user.user_id) in game.users_next_parts and game.can_submit:
                resetAFK(self.user)
                next_part = info['next_part']
                game = Game.get_by_key_name(str(game_id))
                #game = retrieveCache(str(game_id), Game)
                game.next_parts.append(next_part)
                game.users_next_parts.append(self.user.user_id)
                if allUsersSubmitted(game):
                    changeToVotingPhase(game)
                else:
                    game.put()
                    #storeCache(game, str(game_id))
                self.response.headers.add_header('success', 's')
            else:
                self.response.headers.add_header('success', 'f')
        return
