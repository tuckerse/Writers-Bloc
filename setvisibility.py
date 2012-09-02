import logging

from basehandler import BaseHandler
from django.utils import simplejson as json
from cacheLib import storeCache

class SetVisibility(BaseHandler):
    def post(self):
        if self.user:
            info = json.loads(self.request.body)
            self.user.display_type = int(info['visibility'])
            storeCache(self.user, self.user.user_id)
            response_info = {'success': True}
            self.response.out.write(json.dumps(response_info))
            logging.debug(json.dumps(response_info))
        else:
            logging.critical('Unauthorized visibility set attempt')

        return
