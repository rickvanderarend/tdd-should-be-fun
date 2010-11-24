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
        gameRun = Game.Create().GetLastRun()
        
        assert(not gameRun.is_finished())
        
        gameRun.attempt("test = true")
        
        assert(gameRun.is_finished())

    def test_simple_game_with_one_test_should_not_succeed_immediately(self):
        gameRun = Game.Create().AddTest("assert(result)").GetLastRun()

        assert(not gameRun.is_finished())
        
        gameRun.attempt("result = false")       
        
        assert(not gameRun.is_finished())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()