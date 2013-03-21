from basehandler import BaseHandler

class AuthenticationPage(BaseHandler):
    def get(self):
        self.render(u'authentication_page')
