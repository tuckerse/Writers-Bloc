from basehandler import BaseHandler

class AuthenticationPage(BaseHandler):
    def get(self):
        if self.user:
            self.render(u'menu_screen')
        else:
            self.render(u'authentication_page')
