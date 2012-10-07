import logging

from django.utils import simplejson as json
from basehandler import BaseHandler
from UserHandler import User

class GetVisibility(BaseHandler):
    def post(self):
        if self.user:
            response_info = {'visibility': self.user.display_type}
            self.response.out.write(json.dumps(response_info))
        else:
            logging.critical('Unauthorized visibility check')
        return
