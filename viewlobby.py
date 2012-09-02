from helperfunctions import getLobbyGames
from basehandler import BaseHandler

class ViewLobby(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            games = getLobbyGames()
            self.render(u'lobby_screen', games=games)
        return
