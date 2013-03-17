from basehandler import BaseHandler
from django.utils import simplejson as json
from storybooklib import removeUser, jsonLoad

class LeaveBeforeStart(BaseHandler):
    def post(self):
        info = jsonLoad(self.request.body)
        game_id = info['game_id']
        user_id = info['user_id']
        removeUser(game_id, user_id)
