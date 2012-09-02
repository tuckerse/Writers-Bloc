import datetime

from Models import Game
from UserHandler import User
from cacheLib import retrieveCache, storeCache
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

def changeToDisplayPhase(game, request_handler = None):
    game.can_submit = False
    game.can_vote = False
    game.end_submission_time = None
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
    scores = {}
    all_voted_one = False

    for user in game.users:
        scores[user] = 0

    max_votes = 0
    second_place = 0
    second_votes = 0
    winning_index = 0

    for i in range(0, len(game.next_parts)):
        vote_count = game.votes.count(i)
        scores[str(game.users_next_parts[i])] += vote_count
        if vote_count > max_votes:
            max_votes = vote_count
            winning_index = i

    if max_votes == len(game.votes):
        all_voted_one = True

    for i in range(0, len(game.next_parts)):
        vote_count = game.votes.count(i)
        if (vote_count > second_votes and not (i == winning_index)) or ((vote_count == max_votes) and not (i == winning_index)):
            second_votes = vote_count
            second_place = i

    tie = (max_votes == second_votes) and (len(game.next_parts) > 1)

    if all_voted_one:
        scores[str(game.users_next_parts[winning_index])] += FIRST_PLACE_BONUS
    elif tie:
        scores[str(game.users_next_parts[winning_index])] += FIRST_PLACE_TIE_BONUS
        scores[str(game.users_next_parts[second_place])] += FIRST_PLACE_TIE_BONUS
    elif len(game.next_parts) > 1:
        scores[str(game.users_next_parts[winning_index])] += FIRST_PLACE_BONUS
        scores[str(game.users_next_parts[second_place])] += SECOND_PLACE_BONUS
    else:
        scores[str(game.users_next_parts[winning_index])] += FIRST_PLACE_BONUS

    game.winning_sentences.append(game.next_parts[winning_index])
    game.winning_users.append(game.users_next_parts[winning_index])
    #game.winning_users_names.append(trimName((User.get_by_key_name(str(game.users_next_parts[winning_index]))).name))
    winning_user = retrieveCache(str(game.users_next_parts[winning_index]), User)
    game.winning_users_names.append(trimName(winning_user.name, winning_user.display_type))
    game.story.append(game.next_parts[winning_index])

    for i in range(0, len(game.users)):
        user_score = scores[game.users[i]] if (game.users[i] in game.users_voted) else 0
        game.recent_score_data[i] = user_score
        game.scores[i] += user_score

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
        temp['score'] = game.recent_score_data[i]
        submitted = game.users_next_parts.count(user_id) > 0
        if submitted:
            temp['sentence'] = game.next_parts[game.users_next_parts.index(user_id)]
        else:
            temp['sentence'] = 'User did not submit'
        scores.append(temp)

    scores = sortByScore(scores)
    for i in range(0, len(scores)):
        (scores[i])['position'] = i+1

    return scores

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
        if user.rounds_afk >= 2:
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
