from Models import Game
from UserHandler import User

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
