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
from joingame import JoinGame
from waitingtostart import WaitingToStart
from cancelgame import CancelGame
from gamedeleted import GameDeleted
from leavebeforestart import LeaveBeforeStart
from getlobby import GetLobby
from getvisibility import GetVisibility
from setvisibility import SetVisibility
from usersettings import UserSettings
from creategame import CreateGame
from updateuserinfo import UpdateUserInfo
from getendtext import GetEndText
from othergames import OtherGames
from donationpage import DonationPage
from nogames import NoGames
from findgamepage import FindGamePage
from rulespage import RulesPage
from getwinner import GetWinner
from timeout import Timeout

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
    ('/join_game', JoinGame),
    ('/waiting_to_start', WaitingToStart),
    ('/cancel_game', CancelGame),
    ('/game_deleted_error', GameDeleted),
    ('/leave_before_start', LeaveBeforeStart),
    ('/get_lobby', GetLobby),
    ('/get_visibility', GetVisibility),
    ('/set_visibility', SetVisibility),
    ('/user_settings', UserSettings),
    ('/create_game', CreateGame),
    ('/update_user_info', UpdateUserInfo),
    ('/get_end_text', GetEndText),
    ('/other_games', OtherGames),
    ('/donation_page', DonationPage),
    ('/no_games', NoGames),
    ('/find_game_page', FindGamePage),
    ('/rules_page', RulesPage),
    ('/get_winner', GetWinner),
    ('timeout', Timeout)
]
app = webapp.WSGIApplication(routes)

def main():
    LastUsedGameID.get_or_insert(LAST_USED_GAME_ID_KEY, game_id=0)

    run_wsgi_app(app)

if __name__ == '__main__':
    main()
