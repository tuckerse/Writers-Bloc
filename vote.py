import logging

from basehandler import BaseHandler
from Models import Game
from storybooklib import changeToDisplayPhase, allUsersVoted

class Vote(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical('Invalid vote attempt detected!')
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if (self.user.user_id in game.users) and not (self.user.user_id in game.users_voted) and game.can_vote:
                resetAFK(user)
                choice = int(self.request.get('part_voted'))
                game.users_voted.append(self.user.user_id)
                game.votes.append(choice)
                if allUsersVoted(game):
                    changeToDisplayPhase(game)
                else:
                    game.put()
                    #storeCache(game, game_id)
                self.response.headers.add_header('response', "s")
                return

        self.response.headers.add_header('response', "n")
        return
