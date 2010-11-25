'''
Created on 24 sep. 2010

@author: rvdarend
'''
import unittest
from model.domain import Game
import pprint

pp = pprint.PrettyPrinter(indent=4)

class Test(unittest.TestCase):
    def test_simple_game_without_tests_is_not_finished_immediately(self):
        gameRun = Game.Create().Play()        
        assert(not gameRun.IsFinished())
    
    def test_simple_game_without_tests_is_finished_immediately_after_running(self):
        gameRun = Game.Create().Play()  
        gameRun.GetResultsOfNewTestRun("test = true")   
        assert(gameRun.IsFinished())

    def test_simple_game_with_one_test_should_not_be_finished_immediately(self):
        gameRun = Game.Create().AddTest("assert(result)").Play()      
        assert(not gameRun.IsFinished())

    def test_simple_game_with_one_test_should_not_be_finished_immediately_after_running(self):
        gameRun = Game.Create().AddTest("assert(result)").Play()     
        gameRun.GetResultsOfNewTestRun("result = false")        
        assert(not gameRun.IsFinished())

    def test_simple_game_with_one_test_that_is_finished_after_correct_implementation(self):
        gameRun = Game.Create().AddTest("assert(result)").Play()       
        gameRun.GetResultsOfNewTestRun("result = True")        
        assert(gameRun.IsFinished())

    def test_that_simple_game_after_running_with_correct_implementation_yields_ok_results(self):
        gameRun = Game.Create().AddTest("assert(result)").Play()       
        results = gameRun.GetResultsOfNewTestRun("result = True")        
        assert(gameRun.AreAllResultsSuccessful(results['test_results']))

    def GetRunningGameWithTwoTests(self):
        return Game.Create().AddTest("assert(result1)").AddTest("assert(result2)").Play()

    def GetCorrectImplementationForGameWithTwoTests(self):
        return "result1 = True\nresult2 = True"

    def test_that_simple_game_with_two_tests_after_running_once_with_correct_implementation_yields_all_successful_results(self):
        gameRun = self.GetRunningGameWithTwoTests()      
        results = gameRun.GetResultsOfNewTestRun(self.GetCorrectImplementationForGameWithTwoTests())         
        assert(gameRun.AreAllResultsSuccessful(results['test_results']))

    def test_that_simple_game_with_two_tests_after_running_once_with_correct_implementation_is_not_finished_yet(self):
        gameRun = self.GetRunningGameWithTwoTests()     
        results = gameRun.GetResultsOfNewTestRun(self.GetCorrectImplementationForGameWithTwoTests())         
        assert(not gameRun.IsFinished())

    def test_that_simple_game_with_two_tests_after_running_twice_with_correct_implementation_yields_all_successful_results(self):
        gameRun = self.GetRunningGameWithTwoTests()     
        gameRun.GetResultsOfNewTestRun(self.GetCorrectImplementationForGameWithTwoTests())        
        results = gameRun.GetResultsOfNewTestRun(self.GetCorrectImplementationForGameWithTwoTests())  
        assert(gameRun.AreAllResultsSuccessful(results['test_results']))
        
    def test_that_simple_game_with_two_tests_is_finished_after_running_with_the_correct_implementation_twice(self):
        gameRun = self.GetRunningGameWithTwoTests()      
        gameRun.GetResultsOfNewTestRun(self.GetCorrectImplementationForGameWithTwoTests())        
        gameRun.GetResultsOfNewTestRun(self.GetCorrectImplementationForGameWithTwoTests())  
        assert(gameRun.IsFinished())

    def test_that_simple_game_with_two_tests_has_zero_tries_at_first(self):
        gameRun = self.GetRunningGameWithTwoTests()      
        assert(gameRun.GetCurrentNumberOfTries() == 0)

    def test_that_simple_game_with_two_tests_after_running_once_with_correct_implementation_has_one_try(self):
        gameRun = self.GetRunningGameWithTwoTests()      
        gameRun.GetResultsOfNewTestRun(self.GetCorrectImplementationForGameWithTwoTests())
        assert(gameRun.GetCurrentNumberOfTries() == 1)
        
    def test_that_simple_game_with_two_tests_after_running_once_with_correct_implementation_and_getting_testresults_several_times_stil_has_one_try(self):
        gameRun = self.GetRunningGameWithTwoTests()
        gameRun.GetCurrentTestResults()      
        gameRun.GetResultsOfNewTestRun(self.GetCorrectImplementationForGameWithTwoTests())
        gameRun.GetCurrentTestResults()
        gameRun.GetCurrentTestResults()
        assert(gameRun.GetCurrentNumberOfTries() == 1)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()