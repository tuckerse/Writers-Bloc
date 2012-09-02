from basehandler import BaseHandler

class FindGame(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            game_id = findGame(self.user)

            if game_id is None:
                self.redirect("/")
                return

            self.redirect("/waiting_to_start?" + urllib.urlencode({'game_id':game_id}))

