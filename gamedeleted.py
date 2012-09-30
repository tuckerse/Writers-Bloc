from basehandler import BaseHandler

class GameDeleted(BaseHandler):
    def get(self):
        self.render(u'game_deleted')
