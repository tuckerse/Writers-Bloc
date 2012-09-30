from cacheLib import retrieveCache, storeCache
from UserHandler import User

class Achievement:
    def __init__(self, iden, name, description, points, determination_function):
        self.iden = iden
        self.name = name
        self.description = description
        self.points = points
        self.determination_function = determination_function

    def resolve(game):
        return addAchievementData(determination_function(game))

    def addAchievementData(output):
        for entry in output:
            entry['achievement_id'] = self.iden
            entry['score'] = self.points

achievements = {}

def applyAchievements(game):
    return_list = []
    for achievement in achievements:
        return_list += achievement.resolve(game)

    addAchievementPoints(return_list, game)

    return return_list

def addAchievementPoints(achievements, game):
    for achievement in achievements:
        index = user.index(achievement['winner_id'])
        scores[index] += achievement['score']

    game.put()
    return

#####################################################################################################
# Different Determination Functions
#####################################################################################################

def firstAuthorDetermination(game):
    scores = game.scores
    user_id = game.users[scores.index(max(game.scores))]
    return [{'winner_id', user_id}]
