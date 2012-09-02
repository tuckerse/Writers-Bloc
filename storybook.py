import os

from google.appengine.dist import use_library
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from Models import LastUsedGameID

from menupage import MenuPage
from findgame import FindGame
from gamescreen import GameScreen
from gamestatus import GameStatus
from viewlobby import  ViewLobby
from startgame import StartGame
from startearly import StartEarly
from submissioncompleteverification import SubmissionCompleteVerification
from getchoices import GetChoices
from vote import Vote
from votecompleteverification import VoteCompleteVerification
from displaycompleteverification import DisplayCompleteVerification
from endvotecompleteverification import EndVoteCompleteVerification
from endvote import EndVote
from joingame import JoinGame
from waitingtostart import WaitingToStart
from cancelgame import CancelGame
from gamedeleted import GameDeleted
from leavebeforestart import LeaveBeforeStart
from voteendearly import VoteEndEarly
from getlobby import GetLobby
from getvisibility import GetVisibility
from setvisibility import SetVisibility
from usersettings import UserSettings
from creategame import CreateGame

from storybooklib import LAST_USED_GAME_ID_KEY

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
use_library('django', '0.96')

routes = [
    ('/', MenuPage),
    ('/find_game', FindGame),
    ('/game_screen', GameScreen),
    ('/game_status', GameStatus),
    ('/view_lobby', ViewLobby),
    ('/start_game', StartGame),
    ('/start_early', StartEarly),
    ('/submission_complete_verification', SubmissionCompleteVerification),
    ('/get_choices', GetChoices),
    ('/vote', Vote),
    ('/vote_complete_verification', VoteCompleteVerification),
    ('/display_complete_verification', DisplayCompleteVerification),
    ('/end_vote_complete_verification', EndVoteCompleteVerification),
    ('/cast_end_vote', EndVote),
    ('/join_game', JoinGame),
    ('/waiting_to_start', WaitingToStart),
    ('/cancel_game', CancelGame),
    ('/game_deleted_error', GameDeleted),
    ('/leave_before_start', LeaveBeforeStart),
    ('/vote_end_early', VoteEndEarly),
    ('/get_lobby', GetLobby),
    ('/get_visibility', GetVisibility),
    ('/set_visibility', SetVisibility),
    ('/user_settings', UserSettings),
    ('/create_game', CreateGame)
]
app = webapp.WSGIApplication(routes)

def main():
    LastUsedGameID.get_or_insert(LAST_USED_GAME_ID_KEY, game_id=0)

    run_wsgi_app(app)

if __name__ == '__main__':
    main()
