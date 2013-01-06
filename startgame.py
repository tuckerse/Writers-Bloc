from basehandler import BaseHandler
from UserHandler import User
from cacheLib import canPlayerHost, markPlayerHostedGame, retrieveCache
from DefaultStartSentences import defaultStart
from DefaultEndSentences import defaultEnd
from storybooklib import joinGame, initializeGame, MAX_PLAYERS, getNextGameID
from django.utils import simplejson as json

import logging

class StartGame(BaseHandler):
    def post(self):
        if not self.user:
            self.render(u'login_screen')
        else:
            if canPlayerHost(self.user.user_id):
                info = json.loads(self.request.body)
                logging.error(self.request.body)
                end_sentence = info['end_sentence']
                start_sentence = info['start_sentence']
                length = info['length']
                if end_sentence == "":
                    end_sentence = defaultEnd.getRandomDefault()
                    if start_sentence == "":
                        start_sentence = defaultStart.getRandomDefault()
                game_id = initializeGame(getNextGameID(), MAX_PLAYERS, start_sentence, end_sentence, length)
                markPlayerHostedGame(self.user.user_id)
                #joinGame(self.user, game_id)
                joinGame(retrieveCache(self.user.user_id, User), game_id)
                self.render(u'game_created_screen', game_id=str(game_id), MAX_PLAYERS=MAX_PLAYERS)
            else:
                self.render(u'cant_host_yet')
        return
