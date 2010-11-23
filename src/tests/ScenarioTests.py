'''
Created on 24 sep. 2010

@author: rvdarend
'''
import unittest

from datetime import datetime

from google.appengine.api import users

from model.domain import Game
from model.domain import GameRun

class Test(unittest.TestCase):
    
    def test_simple_game_without_tests_succeeds_immediately(self):
        author = users.User("author@example.com")
        player = users.User("player@example.com")
        time = datetime.now()
        game = Game.create(None, author, time)
        gameRun = game.get_run(player)
        
        assert(not gameRun.is_finished())
        
        gameRun.make_attempt("test = true")
        
        assert(gameRun.is_finished())

    def test_simple_game_with_one_test_should_not_succeed_immediately(self):
        author = users.User("author@example.com")
        player = users.User("player@example.com")
        time = datetime.now()
        game = Game.create(None, author, time)
        
        game.add_test("assert(result)")
        gameRun = game.get_run(player)

        assert(not gameRun.is_finished())
        
        gameRun.make_attempt("result = false")       
        
        assert(not gameRun.is_finished())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()