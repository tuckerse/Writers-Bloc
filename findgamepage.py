from basehandler import BaseHandler
from cacheLib import storeCache
from Models import Game

class FindGamePage(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            self.render(u'find_game')
