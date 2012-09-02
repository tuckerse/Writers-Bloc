from basehandler import BaseHandler

class UserSettings(BaseHandler):
    def get(self):
        if self.user:
            self.render(u'user_settings')
        else:
            self.render(u'login_screen')
