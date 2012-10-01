import logging

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
        return output

achievements = dict()

def loadAchievements():
    achieve = Achievement(0, 'First Author', 'Lead author of this story', 10, firstAuthorDetermination)
    achievements[achieve.iden] = achieve

def applyAchievements(game):
    return_list = []
    for key in achievements:
        logging.debug(achievements[key])
        return_list.append(achievements[key].resolve(game))

    updateGameAchievements(return_list, game)
    return return_list

def updateGameAchievements(achievement_list, game):
    achievement_string_list = []
    for achievement in achievement_list:
        for winner_data in achievement:
            
            user = retrieveCache(winner_data['winner_id'], User)
            if not winner_data['achievement_id'] in user.achievements:
                user.achievements.append(winner_data['achievement_id'])
            storeCache(user, user.user_id)
            
            achievement_string_list.append((str(winner_data['winner_id']) + '^' + str(winner_data['achievement_id'])))
            index = game.users.index(winner_data['winner_id'])
            game.scores[index] += winner_data['score']

    game.achievements = achievement_string_list
    game.put()
    return

def getAchievement(identifier):
    return achievements[identifier]

#####################################################################################################
# Different Determination Functions
#####################################################################################################

def firstAuthorDetermination(game):
    scores = game.scores
    high_score = max(game.scores)
    if scores.count(high_score) > 1:
        #Tie, do not award
        return []
    
    user_id = game.users[scores.index(high_score)]
    return [{'winner_id': user_id}]


loadAchievements()
