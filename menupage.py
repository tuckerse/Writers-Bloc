from basehandler import BaseHandler
from cacheLib import storeCache
from Models import Game

class MenuPage(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            if self.user.first_time:
                self.user.first_time = False
                storeCache(self.user, self.user.user_id)
                self.render(u'user_settings')
            else:
                in_game = False
                if not self.user.current_game is None:
                    game = Game.get_by_key_name(str(self.user.current_game))
                    in_game = game.started 
                self.render(u'menu_screen', in_game=in_game, game_id=self.user.current_game)
