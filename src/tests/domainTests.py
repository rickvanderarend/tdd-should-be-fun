'''
Created on 24 sep. 2010

@author: rvdarend
'''
import unittest

from datetime import datetime

from google.appengine.api import users

from model.domain import Game
from model.domain import Test
from model.domain import Implementation

class DomainTest(unittest.TestCase):
    
    def test_Game_name_gets_a_default_value(self):
        author = users.User("author@example.com")
        time = datetime.now()
        game = Game.Create(author = author, time = time)
        assert(game.name == "Game_" + str(author) + "_" + str(time))

    def test_GameRun_game_author_stays_the_same(self):
        author = users.User("author@example.com")
        game = Game.Create(author = author)
        
        player = users.User("player@example.com")
        match = game.Play(player = player) 
        
        assert(match.game.author == author)  

    def test_it_should_be_possible_to_add_a_test_to_a_game(self):
        game = Game.Create().AddTest("assert(result)")
        
        assert(game.number_of_tests == 1)   
        
    def test_it_should_be_possible_to_get_an_added_test_from_a_game(self):
        game = Game.Create().AddTest("assert(result)")
        
        tests = game.GetTests()
        nr_of_tests = 0
        for test in tests:
            nr_of_tests += 1
            assert(test.code == "assert(result)")
        assert(nr_of_tests == 1)

    def test_when_getting_a_match_it_has_the_number_of_tests_of_the_game(self):
        game = Game.Create().AddTest("assert(result)")
        match = game.Play()
        
        assert(match.GetNumberOfTestsInGame() == 1)
        assert(match.GetCurrentNumberOfTestsShown() == 1)
        
    def test_when_getting_a_match_it_shows_the_first_test_of_the_game(self):
        game = Game.Create().AddTest("assert(result)").AddTest("assert(result2)")
        match = game.Play()
        
        assert(match.GetNumberOfTestsInGame() == 2)
        assert(match.GetCurrentNumberOfTestsShown() == 1)
        assert(match.HasMoreTestsThanShown(match.GetNumberOfTestsInGame()))
        assert(match.GetTestsToShow()[0].code == "assert(result)")
    
    def test_running_with_correct_implementation_should_yield_a_positive_result(self):
        game = Game.Create()
        game.put()
        test = Test()
        test.game = game
        test.code = "assert(result)" 
        test.put() 
        implementation = Implementation()
        implementation.code = "result = True"
        implementation.put()      
        testrun = test.Run(implementation)
        assert(testrun.result)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()