# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import random
import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, History, Score
from models import StringMessage, UserForm, UserForms, \
    NewGameForm, GameForm, GameForms, CancelGameForm, \
    HistoryForm, HistoryForms, \
    MakeMoveForm, ScoreForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1))
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
GET_GAME_HISTORY_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1))

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
HIGH_SCORES_REQUEST = endpoints.ResourceContainer(number_of_results=messages.IntegerField(1))



MEMCACHE_WIN_RATES = 'WIN_RATES'




@endpoints.api(name='tic_tac_toe', version='v1')
class TicTacToeApi(remote.Service):
    """Game API"""









# CREATE USER -------------------------------

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email, wins=0, total=0, rate=0)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))



# GET USER RANKS ---------------------------
    @endpoints.method(response_message=UserForms,
                      path='user/rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all scores"""
        return UserForms(items=[user.to_form() for user in User.query().order(-User.rate)])





# --- New GAME ------------------------

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

        game = Game.new_game(user.key, 'Good luck playing Tic Tac Toe!')        

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_win_rates')
        return game.to_form()












# --- GET GAME ------------------------

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            # game.message='Time to make a move!'
            return game.to_form()
        else:
            raise endpoints.NotFoundException('Game not found!')


# GET HISTORY ---------------------------------

    @endpoints.method(request_message=GET_GAME_HISTORY_REQUEST,
                      response_message=HistoryForms,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the game history."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            histories = History.query(History.game==game.key)
            return HistoryForms(items = [history.to_form() for history in histories])
        else:
            raise endpoints.NotFoundException('Game not found!')






# CANCEL GAME --------------------------------

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=CancelGameForm,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            # game.message='Time to make a move!'
            game.key.delete()
            return CancelGameForm(message="cancelled")
        else:
            raise endpoints.NotFoundException('Game not found!')






# --- MAKE MOVE --------------------------

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        if (request.pos < 0 or request.pos > 8):
            raise endpoints.BadRequestException("only move from 0-8!")


        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            game.message = 'Game already over!'
            return game.to_form()
        
        if (game.board[request.pos] != "-"):
            raise endpoints.BadRequestException("can not move here!")    

        # message = ""
        game.board = game.board[:request.pos] + "X" + game.board[request.pos+1:]
        winner = self.get_winner(game.board, "X")
        if winner != None:
            message = "You win!"
            game.end_game(winner, message)
            History(game=game.key, move=request.pos, result=message).put()
            return game.to_form()


        spaces = []
        i = -1
        for state in game.board:
            i += 1
            if (state == "-"):
                spaces.append(i);
        if (len(spaces) > 0):
            robot_move = random.choice(spaces)      
            game.board = game.board[:robot_move] + "O" + game.board[robot_move+1:]
            winner = self.get_winner(game.board, "O")
            if winner != None:
                message = "You lose!"
                game.end_game(winner, message)
                History(game=game.key, move=request.pos, result=message).put()
                return game.to_form()
        
        if game.board.count("-") < 1:
            message = "Tie!"
            game.end_game(None, message)
            History(game=game.key, move=request.pos, result=message).put()            
            return game.to_form()

        message = "Keep moving."
        game.message = message
        game.put()
        History(game=game.key, move=request.pos, result=message).put()                    
        return game.to_form()        



    def get_winner(self, board, chessman): 
        if (board[0] == chessman and board[1] == chessman and board[2] == chessman):
            return chessman
        if (board[3] == chessman and board[4] == chessman and board[5] == chessman):
            return chessman
        if (board[6] == chessman and board[7] == chessman and board[8] == chessman):
            return chessman
        
        if (board[0] == chessman and board[3] == chessman and board[6] == chessman):
            return chessman
        if (board[1] == chessman and board[4] == chessman and board[7] == chessman):
            return chessman
        if (board[2] == chessman and board[5] == chessman and board[8] == chessman):
            return chessman

        if (board[2] == chessman and board[4] == chessman and board[6] == chessman):
            return chessman
        if (board[0] == chessman and board[4] == chessman and board[8] == chessman):
            return chessman




# GET USER GAMES --------------------------

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all of individual active games."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        
        games = Game.query(Game.user == user.key).filter(Game.game_over == False)
        return GameForms(items=[game.to_form() for game in games])








# GET SCORES ---------------------

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])


# GET USER SOCRES -------------------------------

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])



# GET HIGH SCORES ------------------------------------------

    @endpoints.method(request_message=HIGH_SCORES_REQUEST,
                      response_message=ScoreForms,
                      path='scores/high',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query().order(-Score.point).fetch(request.number_of_results)])



# GET AVERAGE WIN RATES -------------------------------------

    @endpoints.method(response_message=StringMessage,
                      path='games/average_win_rates',
                      name='get_average_win_rates',
                      http_method='GET')
    def get_average_win_rates(self, request):
        """Get the cached average win rate"""
        return StringMessage(message=memcache.get(MEMCACHE_WIN_RATES) or '')


# CACHE AVERAGE WIN RATES ----------------------------

    @staticmethod
    def _cache_average_win_rates():
        """Populates memcache with the average win rates of Games"""
        # games_win = len(Game.query(Game.winner == "X").fetch())
        # games_over = len(Game.query(Game.game_over == True).fetch())
        games_win = Game.query(Game.winner == "X").count()        
        games_over = Game.query(Game.game_over == True).count()

        if games_over > 0:
            average = float(games_win)/games_over
            memcache.set(MEMCACHE_WIN_RATES,
                         'The average win rate is {:.2f}'.format(average))


api = endpoints.api_server([TicTacToeApi])
