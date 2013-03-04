import logging

from basehandler import BaseHandler
from Models import Game
from storybooklib import changeToDisplayPhase, allUsersVoted, removeVote

class Vote(BaseHandler):
    def post(self):
        if not self.user:
            logging.critical('Invalid vote attempt detected!')
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if (self.user.user_id in game.users) and game.can_vote:
                if self.user.user_id in game.users_voted:
                    game = removeVote(game, self.user)
                choice = int(self.request.get('part_voted'))
                if str(self.user.user_id) == game.users_next_parts[choice]:
                    logging.critical('Attempt to vote for self detected. user_id: ' + str(self.user.user_id))
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
