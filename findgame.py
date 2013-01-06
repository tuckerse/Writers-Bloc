from basehandler import BaseHandler
from storybooklib import findGame
from django.utils import simplejson as json

import urllib

class FindGame(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            length = int(self.request.get('length'))
            game_id = findGame(self.user, length)

            if game_id is None:
                self.redirect("/no_games")
                return

            self.redirect("/waiting_to_start?" + urllib.urlencode({'game_id':game_id}))
