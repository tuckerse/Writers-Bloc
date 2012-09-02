from basehandler import BaseHandler
from storybooklib import MAX_PLAYERS

class WaitingToStart(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            game_id = self.request.get('game_id')
            user_id = self.user.user_id
            self.render(u'waiting_to_start', game_id=game_id, MAX_PLAYERS=MAX_PLAYERS, user_id=user_id)

        return
