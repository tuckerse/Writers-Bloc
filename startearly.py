import urllib

from basehandler import BaseHandler
from Models import Game
from storybooklib import startGame

class StartEarly(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            game_id = self.request.get('game_id')
            game = Game.get_by_key_name(game_id)
            #game = retrieveCache(game_id, Game)
            if not self.user.user_id in game.users:
                self.render(u'error_screen')
            elif len(game.users) > 1:
                startGame(game_id)
                self.redirect("/game_screen?" + urllib.urlencode({'game_id':game_id}))

        return
