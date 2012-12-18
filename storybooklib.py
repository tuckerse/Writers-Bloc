import datetime
import random
import sys
import re
import logging

from Models import Game, LastUsedGameID
from UserHandler import User
from cacheLib import retrieveCache, storeCache
from google.appengine.ext import db
from achievementlib import applyAchievements, getAchievement

MAX_PLAYERS = 8
VOTE_TIME = 45
LAST_USED_GAME_ID_KEY = "a45tfyhssert356t"
SUBMISSION_TIME = 90
DISPLAY_TIME = 20
END_VOTING_TIME = 20
FIRST_PLACE_BONUS = 3
SECOND_PLACE_BONUS = 1
FIRST_PLACE_TIE_BONUS = 2
SECOND_PLACE_TIE_BONUS = 1
MAX_GAME_CREATION = 10*60
URL_REGEX = "(((http(s)?)|(ftp))://)?(www\.)?([a-zA-Z0-9]*\.)+[a-zA-Z0-9]+(/[a-zA-Z0-9/?&_=]*)*" 
EMAIL_REGEX = "[a-zA-Z0-9]+@([a-zA-Z0-9\.]+\.)*([a-zA-Z0-9]+)?(\.([a-zA-Z])+)"

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
    user.current_game = str(game_id)
    storeCache(user, user.user_id)
    if result.current_players == MAX_PLAYERS:
        startGame(game_id)
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

def getLobbyGames():
    query = Game.gql("WHERE current_players <:1 AND started =:2 ORDER BY current_players DESC", MAX_PLAYERS, False)
    return query.fetch(1000000)

def startGame(game_id):
    game = Game.get_by_key_name(str(game_id))
    #game = retrieveCache(str(game_id), Game)
    if game.started:
        return False

    game.started = True
    current_time = datetime.datetime.now()
    end_submission = current_time + datetime.timedelta(seconds=SUBMISSION_TIME)
    game.end_submission_time = end_submission
    game.can_submit = True
    game.next_parts = []
    game.users_next_parts = []
    for user in game.users:
        game.scores.append(0)
    game.put()
    #storeCache(game, str(game_id))
    return True

def markAFKS(game, acted_list):
    for user_id in game.users:
        if not user_id in acted_list:
            user = retrieveCache(user_id, User)
            user.rounds_afk += 1
            storeCache(user, user_id)

    for user_id in acted_list:
        user = retrieveCache(user_id, User)
        resetAFK(user)        

def changeToDisplayPhase(game, request_handler = None):
    game.can_submit = False
    game.can_vote = False
    game.display_phase = True
    game.went_to_submission = False
    game.end_display_time = datetime.datetime.now() + datetime.timedelta(seconds=DISPLAY_TIME)
    determineWinner(game)
    recent_winner_string = "\"" + game.winning_sentences[len(game.winning_sentences)-1] + "\" By: " + game.winning_users_names[len(game.winning_users_names) - 1]
    if not request_handler == None:
        request_handler.response.headers.add_header('recent_winner', recent_winner_string)
        request_handler.response.headers.add_header('completed', "v")
    game.put()
    #storeCache(game, str(game.game_id))

def determineWinner(game):
    score_structure, other_data = generateScoreStructure(game)

    first_place = (0, '')
    second_place = (0, '')
    tie = False
    
    #No tie for first place
    if len(score_structure[0]['user_list']) <= 1:
        first_place = score_structure[0]['user_list'][0]
        
        #And no tie for second place
        if len(score_structure[1]['user_list']) <= 1:
            if len(score_structure[1]['user_list']) == 0:
                second_place = (-1, '')
            else:
                second_place = score_structure[1]['user_list'][0]
        #And tie for second place
        else:
            second_one, second_two = tieBreaker(score_structure[1]['user_list'])
            second_place = second_one

    #Tie for first place
    else:
        tie = True
        first_one, first_two = tieBreaker(score_structure[0]['user_list'])
        first_place = first_one
        second_place = first_two

    scores = {}
    bonuses = {}

    for user_id in game.users:
        scores[user_id] = other_data[user_id][0] if (user_id in game.users or len(game.next_parts) == 1) else 0
        bonuses[user_id] = 0

    if tie:
        bonuses[first_place[0]] += FIRST_PLACE_TIE_BONUS
        if second_place[0] != -1:
            bonuses[second_place[0]] += FIRST_PLACE_TIE_BONUS
    else:
        bonuses[first_place[0]] += FIRST_PLACE_BONUS
        if second_place[0] != -1:
            bonuses[second_place[0]] += SECOND_PLACE_BONUS

    game.winning_sentences.append(first_place[1])
    game.winning_users.append(first_place[0])
    user = retrieveCache(str(first_place[0]), User)
    game.winning_users_names.append(trimName(user.name, user.display_type))
    game.story.append(first_place[1])
    
    for i in range(0, len(game.users)):
        bonus_str = '0'

        if (game.users[i] == first_place[0] or game.users[i] == second_place[0])  and tie:
            bonus_str = str(FIRST_PLACE_TIE_BONUS)
        elif (game.users[i] == first_place[0]):
            bonus_str = str(FIRST_PLACE_BONUS)
        elif (game.users[i] == second_place[0]):
            bonus_str = str(SECOND_PLACE_BONUS)

        game.recent_score_data[i] = str(scores[game.users[i]]) + ';' + bonus_str
        game.scores[i] += scores[game.users[i]] + bonuses[game.users[i]]

    game.put()
        
    
def tieBreaker(score_struct_list):
    #For shortest sentence wins tie
    #sorted_list = sorted(score_struct_list, key=lambda x: len(x[1]))
    sorted_list = list(score_struct_list)
    random.shuffle(sorted_list)
    return sorted_list[0], sorted_list[1]

def generateScoreStructure(game):
    users_submitted = game.users_next_parts
    votes = game.votes
    next_parts = game.next_parts
    
    user_vote_score = {}
    
    for i in range(0, len(game.users)):
        user_vote_score[game.users[i]] = (0, "")

    for i in range(0, len(users_submitted)):
        user_vote_score[users_submitted[i]] = (votes.count(i), next_parts[i])
    
    top_score, second_score = getTopScores(user_vote_score)
    top_score = int(top_score)
    second_score = int(second_score)
    logging.debug(str(top_score) + " " + str(second_score))
    
    score_struct = ({}, {})
    score_struct[0]['score'] = top_score
    score_struct[0]['user_list'] = []
    score_struct[1]['score'] = second_score
    score_struct[1]['user_list'] = []
    
    for key in user_vote_score.keys():
        logging.debug(str(user_vote_score[key][0]) + "&&" + str(top_score) + " " + str(type(user_vote_score[key][0])) + " " + str(type(top_score)))
        if user_vote_score[key][0] == top_score:
            score_struct[0]['user_list'].append((key, user_vote_score[key][1]))
        elif user_vote_score[key][0] == second_score:
            score_struct[1]['user_list'].append((key, user_vote_score[key][1]))

    logging.debug(score_struct[0]['user_list'])
    logging.debug(score_struct[1]['user_list'])
    return score_struct, user_vote_score    

def getTopScores(score_struct):
    top = -1
    for entry in score_struct:
        if entry[0] > top:
            top = entry[0]

    second = -1
    for entry in score_struct:
        if entry[0] > second and not entry[0] == top:
            second = entry[0]      
 
    if second == -1:
        second = top

    return top, second

def trimName(name, display_type):
    split_name = name.partition(' ')
    return_string = ''
    if display_type == 0:
        return 'Anonymous'
    elif display_type == 1:
        for name in split_name:
            return_string += name[0] + '. '
        return return_string
    elif display_type == 2:
        for i in range(0, len(split_name)):
            if i == (len(split_name) - 1):
                return_string += split_name[i][0] + '.'
            else:
                return_string += split_name[i] + ' '
        return return_string
    else:
        for name in split_name:
            return_string += name + ' '
        return return_string

    return (split_name[0] + ' ' + (split_name[2])[0] + '.')


def getRecentScoreInfo(game):
    scores = []

    for i in range(0, len(game.users)):
        user_id = game.users[i]
        #user = User.get_by_key_name(user_id)
        user = retrieveCache(user_id, User)
        temp = {}
        temp['user_name'] = trimName(user.name, user.display_type)
        votes, bonus = game.recent_score_data[i].split(";")
        votes = int(votes)
        bonus = int(bonus)
        temp['score_votes'] = votes
        temp['score_bonus'] = bonus
        temp['score'] = votes + bonus
        submitted = game.users_next_parts.count(user_id) > 0
        if submitted:
            temp['sentence'] = game.next_parts[game.users_next_parts.index(user_id)]
        else:
            temp['sentence'] = 'User did not submit'
        scores.append(temp)

    scores = sortByScore(scores)
    winning_users_name = game.winning_users_names[len(game.winning_users_names) - 1]
    if not scores[0]['user_name'] ==  winning_users_name:
        makeFirst(scores, winning_users_name)
    
    for i in range(0, len(scores)):
        (scores[i])['position'] = i+1

    return scores

def makeFirst(scores, winning_users_name):
    index = -1
    
    for i in range(0, len(scores)):
        if scores[i]['user_name'] == winning_users_name:
            index = i
            break

    temp = scores[0]
    scores[0] = scores[index]
    scores[index] = temp        

def sortByScore(scores):
    return quicksort(scores)

def quicksort(L):
    pivot = 0
    if len(L) > 1:
        pivot = random.randrange(len(L))
        elements = L[:pivot]+L[pivot+1:]
        left  = [element for element in elements if element > L[pivot]]
        right =[element for element in elements if element <= L[pivot]]
        return quicksort(left)+[L[pivot]]+quicksort(right)
    return L


def getStoryString(game):
    string = game.start_sentence + " ... "
    for s in game.story:
        string += s
    string += " ... " + game.end_sentence
    return string

def getStoryStringForGameScreen(game):
    string = game.start_sentence + " ...<br><br><br>"
    for s in game.story:
        string += s + ' '
    string += "<br><br><br>... " + game.end_sentence
    return string

def getScoreInfo(game):
    scores = []
    haveUsed = []
    for i in range(0, len(game.users)):
        user_id = game.users[i]
        #user = User.get_by_key_name(user_id)
        user = retrieveCache(user_id, User)
        temp = {}
        temp['user_name'] = trimName(user.name, user.display_type)
        temp['user_id'] = user_id
        temp['score'] = game.scores[i]
        scores.append(temp)

    scores = sortByScore(scores)
    for i in range(0, len(scores)):
        (scores[i])['position'] = i+1

    return scores

def getProfilesAndAFKS(scoreList):
    profiles = []
    afks = []
    for entry in scoreList:
        user_id = entry['user_id']
        #user = User.get_by_key_name(user_id)
        user = retrieveCache(user_id, User)
        profiles.append(user.picture)
        if user.rounds_afk >= 3:
            afks.append(True)
        else:
            afks.append(False)

    return profiles, afks

def changeToSubmissionPhase(game, request_handler = None):
    game.can_submit = True
    game.can_vote = False
    game.end_voting = False
    game.can_vote = False
    game.end_submission_time = datetime.datetime.now() + datetime.timedelta(seconds=SUBMISSION_TIME)
    game.display_phase = False
    game.end_users_voted = []
    game.end_votes = []
    clearPhaseInformation(game)
    if not request_handler == None:
        request_handler.response.headers.add_header('response', "v")
    game.put()
    #storeCache(game, str(game.game_id))

def clearPhaseInformation(game):
    game.next_parts = []
    game.users_next_parts = []
    game.votes = []
    game.users_voted = []
    game.num_phases = game.num_phases + 1

def changeToEndVotingPhase(game, request_handler = None):
    game.end_voting = True
    game.can_vote = False
    game.end_end_vote_time = datetime.datetime.now() + datetime.timedelta(seconds=END_VOTING_TIME)
    game.display_phase = False
    if not request_handler == None:
        request_handler.response.headers.add_header('response', "v")
    game.put()
    #storeCache(game, str(game.game_id))


def finishGameTally(game):
    #true is finished
    removeAFKVotes(game)
    count_no = game.end_votes.count(0)
    count_yes = game.end_votes.count(1)
    if count_yes > count_no:
        return True
    return False

def removeAFKVotes(game):
    for user_id in game.users:
        user = retrieveCache(user_id, User)
        if user.rounds_afk >= 2:
            if user_id in game.end_users_voted:
                index = game.end_users_voted.index(user_id)
                del game.end_users_voted[index]
                del game.end_votes[index]

    game.put()

def finishGame(game):
    game.finished = True
    game.game_ended = datetime.datetime.now()
    applyAchievements(game)
    clearUsersFromGame(game)
    #game.put()
    #^^ Will need to uncomment this if you change the put() in the achievement framework
    #storeCache(game, str(game.game_id))

def clearUsersFromGame(game):
    for user_id in game.users:
        user = retrieveCache(user_id, User)
        user.current_game = None
        storeCache(user, user_id)

def removeUser(game_id, user_id):
    game = Game.get_by_key_name(game_id)
    user = retrieveCache(user_id, User)
    user.current_game = None
    game.users.remove(str(user_id))
    storeCache(user, user_id)
    try:
        game.put()
        #storeCache(game, str(game.game_id))
    except Exception, ex:
        logging.critical(ex)


def initializeGame(game_id, max_players, start_sentence, end_sentence):
    game_id = getNextGameID()
    newGame = Game(key_name=str(game_id))
    newGame.game_id = game_id
    newGame.created = datetime.datetime.now()
    newGame.can_vote = False
    newGame.story = []
    newGame.users = []
    newGame.current_players = 0
    newGame.num_phases = 1
    #newGame.num_phases = 9
    newGame.end_sentence = end_sentence
    newGame.start_sentence = start_sentence
    newGame.can_submit = False
    newGame.display_phase = False
    newGame.finished = False
    newGame.started = False
    newGame.users_voted_end_early = []
    newGame.users
    newGame.put()
    #storeCache(newGame, str(game_id))
    return game_id


def getNextGameID():
    previous_game_id = LastUsedGameID.get_by_key_name(LAST_USED_GAME_ID_KEY)
    if previous_game_id.game_id == sys.maxint:
        game_id = 0
    else:
        game_id = previous_game_id.game_id + 1
    previous_game_id.game_id = game_id
    previous_game_id.put()
    return game_id


def allUsersVoted(game):
    return (len(game.users) == len(game.users_voted))

def getPlayerNames(game):
    nameList = []
    for user_id in game.users:
        user = retrieveCache(user_id, User)
        nameList.append(trimName(user.name, user.display_type))
        #nameList.append(trimName(retrieveCache(user, User).name))
    return nameList

def resetRecentScoreData(game):
    game.recent_score_data = []
    for user in game.users:
        game.recent_score_data.append('')

def removeVote(game, user):
    index = game.users_voted.index(user.user_id)
    del game.users_voted[index]
    del game.votes[index]
    game.put()

def getEndText(game):
    achievements = parseAchievements(game.achievements)
    end_text = ''
    for achievement in achievements:
        user = User.get_by_key_name(achievement['winner_id'])
        achievement_data = getAchievement(achievement['achievement_id'])
        end_text += 'Achievement: ' + achievement_data.name + '<br>'
        end_text += 'Description: ' + achievement_data.description + '<br>'
        end_text += 'Winner: ' + trimName(user.name, user.display_type) + '<br>'
        end_text += 'Points Awarded: ' + str( achievement_data.points) + '<br><br>'

    return end_text

def parseAchievements(input_string_list):
    return_list = []
    for input_string in input_string_list:
        parts = input_string.split('^')
        return_list.append({'winner_id':parts[0], 'achievement_id':int(parts[1])})

    return return_list

def cleanSubmission(next_part):
    ret = re.sub(URL_REGEX, "URL", next_part)	
    ret = re.sub(EMAIL_REGEX, "EMAIL", ret)
    return ret

def checkForDoubleSubmissions(game):
    new_parts = []
    new_users = []
    
    for part in game.next_parts:
        if part not in new_parts:
            new_parts.append(part)

    for user in game.users_next_parts:
        if user not in new_users:
            new_users.append(user)

    game.next_parts = new_parts
    game.users_next_parts = new_users

    game.put()

    return game
