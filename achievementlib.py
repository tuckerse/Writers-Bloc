import logging
import random
import operator

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
    first_author = Achievement(0, 'First Author', 'Lead author of this story', 0, firstAuthorDetermination)
    achievements[first_author.iden] = first_author

    team_edward = Achievement(0, 'Team Edward', 'Most mention of vampires', 25, teamEdwardDetermination)
    achievements[team_edward.iden] = team_edward

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

def teamEdwardDetermination(game):
    #Words we are looking for
    associated_words = ['vampire', 'vampiric', 'vampirism', 'dracula']
    
    #Initialize scores to 0
    user_scores = dict()
    
    for user in game.users:
        user_scores[user] = 0

    for i in range(0, len(game.story)):
        part = game.story[i]
        user = game.winning_users[i]
        lower_case = part.lower()
        for word in associated_words:
            user_scores[user] += part.count(word)

    winning_user = max(user_scores.iterkeys(), key=lambda x: user_scores[x])
    if user_score[winning_user] == 0
        return []

    value = random.random()
    
    if value > 0.8:
        return [{'winner_id':winning_user}]
    

loadAchievements()
