from basehandler import BaseHandler
from cacheLib import storeCache

class MenuPage(BaseHandler):
    def get(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            if self.user.first_time:
                self.user.first_time = False
                storeCache(self.user, self.user.user_id)
                self.render(u'user_settings')
            else:
                self.render(u'menu_screen')
