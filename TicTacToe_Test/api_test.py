import unittest

import operator
import os

import import_app_engine
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.api import taskqueue
import endpoints
from protorpc import message_types


import sys
sys.path.append("..")
from TicTacToe.api import *
from TicTacToe.models import User, Game, Score


class TicTacToeApiTestCase(unittest.TestCase):

    def setUp(self):
        self.api = TicTacToeApi()
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        ndb.get_context().clear_cache()
        
        # root_path must be set the the location of queue.yaml.
        # Otherwise, only the 'default' queue will be available.
        self.testbed.init_taskqueue_stub()
            # root_path=os.path.join(os.path.dirname(__file__), 'resources'))
        self.taskqueue_stub = self.testbed.get_stub(
            testbed.TASKQUEUE_SERVICE_NAME)
            
        self.user = User(name="lisa", email="abc@xyz", wins=0, total=0, rate=0)        
        self.user.put()    
        self.gameToAdd = Game(
            # target = 1,
            # attempts_allowed=1,
            # attempts_remaining=1,
            game_over=False,
            user=self.user.key,
            board="--O-X----"
        )
        self.gameToAdd.put()   

    def tearDown(self):
        self.testbed.deactivate()  




    def testOne(self):
        self.assertTrue(True)
        
    def test_create_user(self):
        # 0.arrange
        container = USER_REQUEST.combined_message_class(
                user_name="lulu",
                email="amc@xyz")        
        # 1.action
        self.api.create_user(container)
        # 2.assert
        user = User.query().fetch()[-1];        
        self.assertEqual("lulu", user.name)
        
        
 # --- new game -----------------------------
    def test_new_game(self):
        # 0.arrange
        self.user.put()
        container = NEW_GAME_REQUEST.combined_message_class(
            user_name="lisa")   
        # 1.action
        self.api.new_game(container)
        # 2.assert
        game = Game.query().fetch()[-1]
        self.assertEqual("lisa", game.user.get().name)
        self.assertEqual("---------", game.board)
        self.assertEqual(False, game.game_over)
        self.assertEqual(None, game.winner)
    
    
# --- get game -------------------------     
    def test_get_game(self):
        # 0.arrange 
        container = GET_GAME_REQUEST.combined_message_class(
                urlsafe_game_key=self.gameToAdd.key.urlsafe())                
        # 1.action
        game = self.api.get_game(container)
        # 2.assert
        # print "\n   origin: " + game.board + "\n"                
        self.assertEqual("--O-X----", game.board)
        
        

# todo: do game -----------------------------------
    def test_make_move_done(self):        
        # 0.arrange      
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 5,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        self.assertEqual("X", game.board[5])
        

    def test_make_move_middle_done(self):        
        # 0.arrange      
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        # print "\n put in 6: " + game.board + "\n"        
        self.assertEqual("X", game.board[6])
        
        
    def test_make_move_head_done(self):        
        # 0.arrange      
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 0,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        # print "\n put in 0: " + game.board + "\n"
        self.assertEqual("X", game.board[0])
        

    def test_make_move_tail_done(self):        
        # 0.arrange      
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 8,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        # print "\n put in 8: " + game.board + "\n"
        self.assertEqual("X", game.board[8])


    def test_make_move_less_then_0_exception(self):        
        # 0.arrange      
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = -1,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion 
        # 2.assert    
        with self.assertRaises(endpoints.BadRequestException):
            game = self.api.make_move(container);
            

    def test_make_move_can_not_move_here_exception(self):        
        # 0.arrange      
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 2,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion 
        # 2.assert    
        with self.assertRaises(endpoints.BadRequestException):
            game = self.api.make_move(container);



    def test_make_move_robot_move(self):        
        # 0.arrange      
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 8,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        # print "\n put in 8: " + game.board + "\n"
        self.assertEqual(2, game.board.count("O"))


    def test_make_move_if_board_is_full_robot_not_move(self):        
        # 0.arrange      
        self.gameToAdd.board = "XXOOXXOO-"
        self.gameToAdd.put();

        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 8,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        # print "\n put in 8: " + game.board + "\n"
        self.assertEqual(4, game.board.count("O"))




#todo: do game win
    def test_make_move_you_win(self):        
        # 0.arrange      
        self.gameToAdd.board = "XXOXXO---"
        self.gameToAdd.put();

        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        # print "\n put in 8: " + game.board + "\n"
        self.assertEqual("X", game.winner)
        self.assertEqual(True, game.game_over)
        self.assertEqual("You win!", game.message)



    def test_make_move_you_lost(self):        
        # 0.arrange      
        self.gameToAdd.board = "OOOOOOO--"
        self.gameToAdd.put();

        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 7,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        # print "\n put in 8: " + game.board + "\n"
        self.assertEqual("O", game.winner)
        self.assertEqual(True, game.game_over)
        self.assertEqual("You lose!", game.message)

    def test_make_move_no_winner(self):        
        # 0.arrange      
        self.gameToAdd.board = "XXOOXX-O-"
        self.gameToAdd.put();

        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        # print "\n put in 8: " + game.board + "\n"
        self.assertEqual(None, game.winner)
        self.assertEqual(True, game.game_over)
        self.assertEqual("Tie!", game.message)


    def test_make_move_not_over(self):        
        # 0.arrange      
        self.gameToAdd.board = "---------"
        self.gameToAdd.put();

        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        # 1.acion        
        game = self.api.make_move(container);
        # 2.assert
        # print "\n put in 8: " + game.board + "\n"
        self.assertEqual(None, game.winner)
        self.assertEqual(False, game.game_over)
        self.assertEqual("Keep moving.", game.message)





# todo: who is the winner -----------------------------------
    def test_get_winner_the_first_line(self):
        # 0.arrange                   
        # 1.acion
        winner = self.api.get_winner("XXXO--O--", "X")
        # 2.assert
        self.assertEqual("X", winner)
     

    def test_get_winner_the_second_line(self):
        # 0.arrange                   
        # 1.acion
        winner = self.api.get_winner("XX-OOOX--", "O")
        # 2.assert
        self.assertEqual("O", winner)

    def test_get_winner_the_third_line(self):
        # 0.arrange                   
        # 1.acion
        winner = self.api.get_winner("XX-OO-XXX", "X")
        # 2.assert
        self.assertEqual("X", winner)


    def test_get_winner_the_first_col(self):
        # 0.arrange                   
        # 1.acion
        winner = self.api.get_winner("XX-XO-X--", "X")
        # 2.assert
        self.assertEqual("X", winner)

    def test_get_winner_the_second_col(self):
        # 0.arrange                   
        # 1.acion
        winner = self.api.get_winner("-X-OX-OX-", "X")
        # 2.assert
        self.assertEqual("X", winner)

    def test_get_winner_the_third_col(self):
        # 0.arrange                   
        # 1.acion
        winner = self.api.get_winner("--X-OX-OX", "X")
        # 2.assert
        self.assertEqual("X", winner)


    def test_get_winner_the_slash(self):
        # 0.arrange                   
        # 1.acion
        winner = self.api.get_winner("--X-XOX--", "X")
        # 2.assert
        self.assertEqual("X", winner)


    def test_get_winner_the_back_slash(self):
        # 0.arrange                   
        # 1.acion
        winner = self.api.get_winner("X---XO--X", "X")
        # 2.assert
        self.assertEqual("X", winner)


    def test_get_winner_not_the_correct_chessman_return_none(self):
        # 0.arrange                   
        # 1.acion
        winner = self.api.get_winner("X---XO--X", "O")
        # 2.assert
        self.assertEqual(None, winner)





# todo: get scores
    def test_get_scores_no_scores(self):            
        # 0.arrange
        void_message = message_types.VoidMessage()
        # 1.acion
        scores = self.api.get_scores(void_message)
        # 2.assert
        self.assertEqual(0, len(scores.items))


    def test_get_scores_one_score(self):            
        # 0.arrange
        self.gameToAdd.board = "XXOXXO---"
        self.gameToAdd.put();
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        game = self.api.make_move(container)
        # 1.acion
        scores = self.api.get_scores(message_types.VoidMessage())
        # 2.assert
        self.assertEqual(1, len(scores.items))


    
    def test_get_scores_user_score_one(self):            
        # 0.arrange
        self.gameToAdd.board = "XXOXXO---"
        self.gameToAdd.put();
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        game = self.api.make_move(container)
        # 1.acion
        container = USER_REQUEST.combined_message_class(
            user_name="lisa",
            email="abc@xyz")
        scores = self.api.get_user_scores(container)
        # 2.assert
        self.assertEqual(1, len(scores.items))

    
    def test_get_scores_user_score_zero(self):            
        # 0.arrange
        container = USER_REQUEST.combined_message_class(
            user_name="lulu",
            email="amc@xyz")              
        self.api.create_user(container)
        
        self.gameToAdd.board = "XXOXXO---"
        self.gameToAdd.put();
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        game = self.api.make_move(container)
        # 1.acion
        container = USER_REQUEST.combined_message_class(
            user_name="lulu",
            email="abc@xyz")
        scores = self.api.get_user_scores(container)
        # 2.assert
        self.assertEqual(0, len(scores.items))




# todo: get user games
    def test_get_user_games(self):            
        # 0.arrange
        # 1.acion
        container = USER_REQUEST.combined_message_class(
            user_name="lisa",
            email="abc@xyz")
        games = self.api.get_user_games(container)
        # 2.assert
        self.assertEqual(1, len(games.items))


# todo: cancel game
    def test_cancel_game(self):            
        # success cancel
        container = CANCEL_GAME_REQUEST.combined_message_class(
                urlsafe_game_key=self.gameToAdd.key.urlsafe())    
        result = self.api.cancel_game(container)
        self.assertEqual("cancelled", result.message)

        # no games
        container = USER_REQUEST.combined_message_class(
            user_name="lisa",
            email="abc@xyz")
        games = self.api.get_user_games(container)
        self.assertEqual(0, len(games.items))



    def test_get_high_scores(self):            
        # 0.arrange
        self.gameToAdd.board = "XXOXXO---"
        self.gameToAdd.put();
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        game = self.api.make_move(container)
        # 1.acion
        h_score_req = HIGH_SCORES_REQUEST.combined_message_class(
            number_of_results=2)
        scores = self.api.get_high_scores(h_score_req)
        # 2.assert
        self.assertEqual(1, len(scores.items))



    def test_get_user_ranks(self):            
        # 0.arrange
        self.gameToAdd.board = "XXOXXO---"
        self.gameToAdd.put();
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        game = self.api.make_move(container)
        # 1.acion
        user_ranks = self.api.get_user_rankings(message_types.VoidMessage())
        # 2.assert
        self.assertEqual(1, len(user_ranks.items))
        self.assertEqual(1, user_ranks.items[0].wins)
        self.assertEqual(1, user_ranks.items[0].total)
        self.assertEqual(1, user_ranks.items[0].rate)





    def test_game_history(self):
        # 0.arrange
        self.gameToAdd.board = "XXOXXO---"
        self.gameToAdd.put();
        container = MAKE_MOVE_REQUEST.combined_message_class(
            pos = 6,
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        game = self.api.make_move(container)
        # 1.acion
        history_request = GET_GAME_HISTORY_REQUEST.combined_message_class(
            urlsafe_game_key = self.gameToAdd.key.urlsafe())
        game_histories = self.api.get_game_history(history_request)
        # 2.assert
        self.assertEqual(1, len(game_histories.items))
        self.assertEqual(6, game_histories.items[0].move)
        self.assertEqual("You win!", game_histories.items[0].result)







    # def test_get_scores_one_score(self):            
    #     # 0.arrange
    #     self.gameToAdd.board = "XXOXXO---"
    #     self.gameToAdd.put();
    #     container = MAKE_MOVE_REQUEST.combined_message_class(
    #         pos = 6,
    #         urlsafe_game_key = self.gameToAdd.key.urlsafe())
    #     game = self.api.make_move(container)
    #     # 1.acion
    #     scores = self.api.get_scores(message_types.VoidMessage())
    #     # 2.assert
    #     self.assertEqual(1, len(scores.items))





    # def test_get_game(self):
    #     # 0.arrange 
    #     container = GET_GAME_REQUEST.combined_message_class(
    #             urlsafe_game_key=self.gameToAdd.key.urlsafe())                
    #     # 1.action
    #     game = self.api.get_game(container)
    #     # 2.assert
    #     # print "\n   origin: " + game.board + "\n"                
    #     self.assertEqual("--O-X----", game.board)

        
        # 0.arrange
        
        # 1.acion
        
        # 2.assert
     
     
     
     
        
if __name__=='__main__':
    unittest.main()  
