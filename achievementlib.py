from cacheLib import retrieveCache, storeCache
from UserHandler import User

class Achievement:
    def __init__(self, iden, name, description, points, determination_function):
        self.iden = iden
        self.name = name
        self.description = description
        self.points = points
        self.determination_function = determination_function

    def resolve(self, game):
        return self.addAchievementData(self.determination_function(game))

    def addAchievementData(self, output):
        for entry in output:
            entry['achievement_id'] = self.iden
            entry['score'] = self.points

achievements = {}

def loadAchievements():
    achieve = Achievement(0, 'First Author', 'Lead author of this story', 10, firstAuthorDetermination)
    achievements[achieve.iden] = achieve

def applyAchievements(game):
    return_list = []
    for key in achievements:
        return_list += achievements[key].resolve(game)

    updateGameAchievements(return_list, game)
    return return_list

def updateGameAchievements(achievements, game):
    achievement_string_list = []
    for achievement in achievements:
        achievement_string_list.append((str(achievement['winner_id']) + '^' + str(achievement['achievement_id'])))
        index = game.users.index(achievement['winner_id'])
        game.scores[index] += achievement['score']

    game.achievements = achievement_string_list
    game.put()
    return

def getAchievement(identifier):
    return achievments[identifier]

#####################################################################################################
# Different Determination Functions
#####################################################################################################

def firstAuthorDetermination(game):
    return_list = []
    scores = game.scores
    user_id = game.users[scores.index(max(game.scores))]
    return [{'winner_id': user_id}]


loadAchievements()
