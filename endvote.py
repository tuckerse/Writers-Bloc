import logging

from basehandler import BaseHandler
from Models import Game

class EndVote(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical('Invalid end-vote attempt detected!')
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if (self.user.user_id in game.users) and not (int(self.user.user_id) in game.end_users_voted) and game.end_voting:
                resetAFK(self.user)
                choice = int(self.request.get('selection'))
                game.end_users_voted.append(self.user.user_id)
                game.end_votes.append(choice)
                game.put()
                #storeCache(game, game_id)
                self.response.headers.add_header('response', "s")
                return

        self.response.headers.add_header('response', "n")
        return
