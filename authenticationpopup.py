from basehandler import BaseHandler

class AuthenticationPopup(BaseHandler):
    def get(self):
        self.render(u'authentication_popup')
