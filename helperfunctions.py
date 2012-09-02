import datetime

from Models import Game
from UserHandler import User
from cacheLib import retrieveCache
from google.appengine.ext import db

MAX_PLAYERS = 8
VOTE_TIME = 45

def findGame(user):
    query = Game.gql("WHERE current_players <:1 ORDER BY current_players ASC", MAX_PLAYERS)
    results = query.fetch(None)
    if len(results) == 0:
        return None

    for result in results:
        game_id = joinGame(user, result.game_id)
        if game_id is False:
            continue
        else:
            return result.game_id

    return None

def getUserInfo(game_id):
    #game = Game.get_by_key_name(str(game_id))
    game = retrieveCache(str(game_id), Game)
    name_list = []
    pic_list = []
    for user_id in game.users:
        #user = User.get_by_key_name(user_id)
        user = retrieveCache(user_id, User)
        name_list.append(trimName(user.name, user.display_type))
        pic_list.append(user.picture)

    return name_list, pic_list

def resetAFK(user):
    user.rounds_afk = 0
    storeCache(user, user.user_id)

def joinGame(user, game_id):
    result = Game.get_by_key_name(str(game_id))
    #result = retrieveCache(str(game_id), Game)
    if result.current_players == MAX_PLAYERS or result.started or (str(user.user_id) in result.users):
        return False
    result.users.append(user.user_id)
    result.current_players += 1
    resetAFK(user)
    if result.current_players == MAX_PLAYERS:
        result.started = True
        result.put()
        #storeCache(result, str(game_id))
        return result.game_id
    result.put()
    #storeCache(result, str(game_id))
    return result.game_id

def allUsersSubmitted(game):
    return (len(game.users) == len(game.users_next_parts))

def changeToVotingPhase(game, request_handler = None):
    game.can_submit = False
    game.can_vote = True
    game.end_submission_time = None
    game.went_to_submission = False
    resetRecentScoreData(game)
    game.end_vote_time = datetime.datetime.now() + datetime.timedelta(seconds=VOTE_TIME)
    game.put()
    #storeCache(game, str(game.game_id))
    if not request_handler == None:
        request_handler.response.headers.add_header('completed', "v")
