"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date, datetime
from protorpc import messages
from google.appengine.ext import ndb






class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    wins = ndb.IntegerProperty(required=True)
    total = ndb.IntegerProperty(required=True)
    rate = ndb.FloatProperty(required=True)

    def to_form(self):
        """Returns a User Form representation of the Game"""
        form = UserForm()
        form.name = self.name
        form.wins=self.wins
        form.total = self.total
        form.rate = self.rate
        return form


class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    wins = messages.IntegerField(2, required=True)
    total = messages.IntegerField(3, required=True)
    rate = messages.FloatField(4, required=True)


class UserForms(messages.Message):
    """Multi GameForms"""
    items = messages.MessageField(UserForm, 1, repeated=True)
    







class History(ndb.Model):
    """Game History"""
    game = ndb.KeyProperty(required=True, kind="Game")
    move = ndb.IntegerProperty(required=True)
    result = ndb.StringProperty(required=True)
    datetime = ndb.DateTimeProperty(required=True)

    def to_form(self):
        """Returns a hisotry form representation of the game history"""
        form = HistoryForm()
        form.move = self.move
        form.result = self.result
        # if (self.datetime):
        #     form.datetime=self.datetime.strftime("%Y-%m-%d %H:%M:%S")
        form.datetime=self.datetime.strftime("%Y-%m-%d %H:%M:%S")
        return form


class HistoryForm(messages.Message):
    """History Form"""
    move = messages.IntegerField(1, required=True)
    result = messages.StringField(2, required=True)
    datetime = messages.StringField(3)


class HistoryForms(messages.Message):
    """History Forms"""
    items = messages.MessageField(HistoryForm, 1, repeated=True)








class Game(ndb.Model):
    """Game object"""
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    board = ndb.StringProperty()
    winner = ndb.StringProperty()
    message = ndb.StringProperty()

    @classmethod
    def new_game(cls, user, message): #, min, max, attempts):
        """Creates and returns a new game"""
        game = Game(user=user,
                    board="---------",
                    message=message,
                    game_over=False)
        game.put()
        return game

    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.game_over = self.game_over
        form.message = self.message
        form.board = self.board
        form.winner = self.winner
        return form

    def end_game(self, winner, message):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.message = message
        self.winner = winner
        self.game_over = True
        self.put()
        # Add the game to the score 'board'    
        score = Score(user=self.user, date=date.today(), winner=winner) #,
                    #   guesses=self.attempts_allowed - self.attempts_remaining)
        if (winner == "X"):
            score.point = 1
        elif (winner == "O"):
            score.point = -1
        else: 
            score.point = 0
        score.put()
        # set user wins
        user = self.user.get()    
        if (winner == "X"):
            user.wins += 1
        user.total += 1
        user.rate = float(user.wins)/user.total
        user.put()


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    winner = messages.StringField(2)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    board = messages.StringField(6, required=True)


class GameForms(messages.Message):
    """Multi GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class CancelGameForm(messages.Message):
    """Multi GameForms"""
    message = messages.StringField(1, required=True)
    

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    pos = messages.IntegerField(1, required=True)







class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    # won = ndb.BooleanProperty(required=True)
    winner = ndb.StringProperty()    
    point = ndb.IntegerProperty(required=True)
    # guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, winner=self.winner,
                         date=str(self.date), point=self.point) #, guesses=self.guesses)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    winner = messages.StringField(3)
    point = messages.IntegerField(4)
    # guesses = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)








class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
