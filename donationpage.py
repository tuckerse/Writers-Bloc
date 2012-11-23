from basehandler import BaseHandler

class DonationPage(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            self.render(u'donation_page')
