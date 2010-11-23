'''
Created on 24 sep. 2010

@author: rvdarend
'''
import unittest

from datetime import datetime

from google.appengine.api import users

from model.domain import Game

class Test(unittest.TestCase):
    
    def test_Game_name_gets_a_default_value(self):
        author = users.User("author@example.com")
        time = datetime.now()
        game = Game.create(None, author, time)
        assert(game.name == "Game_" + str(author) + "_" + str(time))

    def test_GameRun_game_author_stays_the_same(self):
        author = users.User("author@example.com")
        time = datetime.now()
        game = Game.create(None, author, time)
        
        player = users.User("player@example.com")
        gameRun = game.get_run(player) 
        
        assert(gameRun.game.author == author)  
    
    #def test_


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()