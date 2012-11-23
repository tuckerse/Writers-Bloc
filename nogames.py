from basehandler import BaseHandler

class NoGames(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            self.render(u'no_games')
