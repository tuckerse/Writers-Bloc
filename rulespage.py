from basehandler import BaseHandler

class RulesPage(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            self.render(u'rules_page')
