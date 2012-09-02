import logging

from google.appengine.ext import db
from django.utils import simplejson as json
from Models import Game
from storybooklib import getPlayerNames, MAX_GAME_CREATION

class GameStatus(webapp.RequestHandler):
    def post(self):
        info = json.loads(self.request.body)
        game_id = info['game_id']
        response_info = {}
        game = Game.get_by_key_name(str(game_id))
        #game = retrieveCache(str(game_id), Game)
        if game is None:
            response_info['deleted'] = True
            response = json.dumps(response_info)
            self.response.out.write(response)
            return
        response_info['deleted'] = False
        response_info['started'] = "y" if game.started else "n"
        response_info['num_players'] = game.current_players
        response_info['players'] = getPlayerNames(game)
        response_info['num_phases'] = game.num_phases
        response_info['vote_this_turn'] = (len(game.users_voted_end_early) >= len(game.users)/2)
        self.response.headers['Content-type'] = 'application/json'
        if game.can_vote:
            response_info['phase'] = "v"
            response_info['seconds_left'] = (game.end_vote_time - datetime.datetime.now()).seconds
            response_info['waiting_on'] = len(game.users) - len(game.votes)
        elif game.can_submit:
            response_info['phase'] = "s"
            response_info['seconds_left'] = (game.end_submission_time - datetime.datetime.now()).seconds
            response_info['waiting_on'] = len(game.users) - len(game.next_parts)
        elif game.display_phase:
            response_info['phase'] = "d"
            response_info['seconds_left'] = (game.end_display_time - datetime.datetime.now()).seconds
        elif game.end_voting:
            response_info['phase'] = "f"
            response_info['seconds_left'] = (game.end_end_vote_time - datetime.datetime.now()).seconds

        response = json.dumps(response_info)
        logging.debug(response_info)

        if ((datetime.datetime.now() - game.created).seconds) > MAX_GAME_CREATION and not game.started:
            db.delete(game)
            #deleteData(game, str(game.game_id))

        self.response.out.write(response)

        return

