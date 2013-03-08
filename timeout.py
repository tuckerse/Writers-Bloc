from basehandler import BaseHandler

class Timeout(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            self.render(u'timeout')
