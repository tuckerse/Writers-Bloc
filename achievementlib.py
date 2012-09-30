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
		return determination_function(game)

achievements = []

def applyAchievements(game):
	return_list = []
	for achievement in achievements:
		return_list += achievement.resolve(game)

	addAchievementPoints(return_list, game)
	
	return return_list

def addAchievementPoints(achievements, game)
	for achievement in achievements:
		index = user.index(achievement['winner_id'])
		scores[index] += achievement['score']
	
	game.put()
	return	
