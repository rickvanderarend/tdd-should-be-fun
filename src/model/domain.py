'''
Created on 25 nov. 2010

@author: rickvanderarend
'''
import re
from google.appengine.ext import db
from google.appengine.api import users
from datetime import datetime
import pprint

pp = pprint.PrettyPrinter(indent=4)

class Game(db.Model):
    name = db.StringProperty()
    start_implementation = db.TextProperty()
    published = db.BooleanProperty()   
    author = db.UserProperty()
    date_created = db.DateTimeProperty()
    number_of_tests = db.IntegerProperty()

    @classmethod
    def Create(cls, name = None, author = users.get_current_user(), start_implementation = '', time = datetime.now()):
        game = cls()
        game.name = name if not name is None else "Game_" + str(author) + "_" + str(time)
        game.author = author
        game.published = True   
        game.date_created = time
        game.number_of_tests = 0
        return game
    
    def ChangeName(self, name):
        self.name = name
        return self
    
    def Publish(self):
        self.published = True
        return self
        
    def SetStartImplementation(self, impl):
        self.start_implementation = impl
        return self

    def GetNumberOfTests(self):
        return (self.number_of_tests) if not (self.number_of_tests is None) else 0
    
    def GetTests(self):
        return db.GqlQuery("SELECT * FROM Test Where game = :1 ORDER BY number ASC", self);
    
    def AddTest(self, code):
        new_test = Test()
        if self.number_of_tests is None:
            self.number_of_tests = self.GetTests().count(1000)
        
        self.number_of_tests = self.number_of_tests + 1        
        self.save()

        new_test.game = self
        new_test.number = self.number_of_tests
        
        if users.get_current_user():
            new_test.author = users.get_current_user()
            new_test.date_created = datetime.now()
            new_test.editor = users.get_current_user()

        new_test.code = code
        new_test.put()
        return self
    
    def IsAuthor(self, user):
        return not(self.author is None) and self.author == user

    def SaveIfNotSaved(self):
        if not self.is_saved():
            self.save()

    def StartMatch(self, player, playerName):
        self.SaveIfNotSaved()
        
        match = Match()
        match.game = self
        match.number_of_tests_shown = 1
        match.number_of_tests_ok = 0
        match.number_of_tries = 0
        match.player = player
        match.playerName = playerName
        match.datetime_started = datetime.now()
        match.datetime_lastaction = datetime.now()
        match.finished = False
        match.put()
        
        return match
    
    def Play(self, player = users.get_current_user(), player_name = None):
        if player_name is None:
            if player is None:
                player_name = 'Anonymous'
            else:
                player_name = player.nickname()
            
        match = None
        try :
            match = db.GqlQuery("Select * From Match Where game = :1 AND player = :2 Order by datetime_lastaction DESC", self, player).get()
            match.player_name = player_name
        except:
            match = None

        if match == None:
            match = self.StartMatch(player, player_name)
        else:
            if match.number_of_tests_shown is None:
                match.number_of_tests_shown = match.number_of_tests_ok
        
        return match

# better call this Match   
class GameRun(db.Model):
    game = db.ReferenceProperty(Game) 
    number_of_tests_shown = db.IntegerProperty()
    number_of_tests_ok = db.IntegerProperty() # deprecate as soon as possible
    number_of_tries = db.IntegerProperty()
    player = db.UserProperty()
    playerName = db.StringProperty()
    datetime_started = db.DateTimeProperty()
    datetime_lastaction = db.DateTimeProperty()
    finished = db.BooleanProperty()
    
class Match(db.Model):
    game = db.ReferenceProperty(Game) 
    number_of_tests_shown = db.IntegerProperty()
    number_of_tries = db.IntegerProperty()
    player = db.UserProperty()
    playerName = db.StringProperty()
    datetime_started = db.DateTimeProperty()
    datetime_lastaction = db.DateTimeProperty()
    finished = db.BooleanProperty()

    def SaveIfNotSaved(self):
        if not self.is_saved():
            self.save()
    
    def GetImplementation(self, code = None):
        last = self.GetLastImplementation()
        
        if not last is None and (code is None or last.code == code):
            implementation = last
        elif code is None:
            implementation = self.GetStartImplementation()
            implementation.save()
        else:
            self.SaveIfNotSaved()
            implementation = Implementation(match = self, code = code, author = self.player, date_created = datetime.now())
            implementation.save()
        
        return implementation
    
    def GetLastImplementation(self):
        last_implementation = None
        try :
            last_implementation = db.GqlQuery("Select * From Implementation Where match = :1 Order by date_created DESC", self).get()
        except:
            last_implementation = None
            
        return last_implementation

    def GetStartImplementation(self):
        self.SaveIfNotSaved()
        return Implementation(match = self, code = self.game.start_implementation, author = self.player, date_created = datetime.now())
        
    def IsFinished(self):
        return self.finished
    
    def GetCurrentNumberOfTries(self):
        return (self.number_of_tries) if not (self.number_of_tries is None) else 0

    def GetCurrentNumberOfTestsShown(self):
        return (self.number_of_tests_shown) if not (self.number_of_tests_shown is None) else 0
 
    def GetNumberOfTestsInGame(self):
        return self.game.GetNumberOfTests()
 
    tests = None
    tests_to_show = None
    new_test = None
 
    def InitializeTestsCache(self):
        if self.tests is None:
            self.tests = self.game.GetTests()
            self.tests_to_show = [None] * self.GetCurrentNumberOfTestsShown()
            testnr = 0
            
            for test in self.tests:               
                if testnr < self.GetCurrentNumberOfTestsShown():
                    self.tests_to_show[testnr] = test
                elif testnr == self.GetCurrentNumberOfTestsShown():
                    self.new_test = test
                testnr += 1
 
    def GetTestsToShow(self):
        self.InitializeTestsCache()     
        return self.tests_to_show
  
    def GetNewTest(self):
        self.InitializeTestsCache()     
        return self.new_test
    
    def RegisterTry(self):
        self.number_of_tries = self.GetCurrentNumberOfTries() + 1
        return self

    def GetResultsOfNewTestRun(self, code):     
        return self.RegisterTry().GetTestResults(self.GetImplementation(code), True)
    
    def GetCurrentTestResults(self):
        return self.GetTestResults(self.GetImplementation(), False)
 
    def GetCurrentTestResultsUsingStartImplementation(self):
        return self.GetTestResults(self.GetStartImplementation(), False)
        
    def AreAllResultsSuccessful(self, test_results):
        return all(map(lambda t:t.result == True, test_results))

    def HasMoreTestsThanShown(self, number_of_tests_in_game):
        return self.number_of_tests_shown < number_of_tests_in_game

    def AreTestResultsNotEnoughToFinish(self, test_results, number_of_tests_in_game):      
        return number_of_tests_in_game > 0 and self.HasMoreTestsThanShown(number_of_tests_in_game) or not self.AreAllResultsSuccessful(test_results)

    def ShowOneMoreTest(self):
        self.number_of_tests_shown = self.number_of_tests_shown + 1

    def GetTestResults(self, implementation, is_attempt = False):      
        tests =  self.game.GetTests()
            
        results = {}
        results['for'] = implementation                 
        number_of_tests = 0
        shown_tests = []
        
        for test in tests:
            if number_of_tests < self.number_of_tests_shown:
                shown_tests.append(test)         
            elif number_of_tests == self.number_of_tests_shown:
                new_test = test
                
            number_of_tests = number_of_tests + 1
        
        attempt = Attempt.Create(match = self, implementation = implementation, number = self.number_of_tries + 1, tests = shown_tests)
        
        results['test_results'] = attempt.results
                    
        if self.AreTestResultsNotEnoughToFinish(results['test_results'], number_of_tests):
            if self.AreAllResultsSuccessful(results['test_results']):             
                if self.HasMoreTestsThanShown(number_of_tests):
                    results['new_test'] = new_test;
                self.ShowOneMoreTest() 
            self.finished = False
        else:
            self.finished = True
             
        self.datetime_lastaction = datetime.now()
        if is_attempt: self.put()
        
        return results

class Implementation(db.Model):
    match = db.ReferenceProperty(Match) 
    code = db.TextProperty()
    author = db.UserProperty()
    date_created = db.DateTimeProperty()

class Attempt(db.Model):
    match = db.ReferenceProperty(Match)
    implementation = db.ReferenceProperty(Implementation)
    number = db.IntegerProperty()
    attempt_made_on = db.DateTimeProperty(auto_now_add=True)
    player = db.UserProperty()
    
    number_of_tests_to_run = db.IntegerProperty()
    number_of_tests_run = db.IntegerProperty()
    number_of_testruns_successful = db.IntegerProperty()
    
    results = []
 
    @classmethod
    def Create(cls, match = None, implementation = None, number = 1, tests = [], player = users.get_current_user(), time = datetime.now()):
        Attempt = cls()
        Attempt.match = match
        Attempt.implementation = implementation
        Attempt.number = number
 
        Attempt.attempt_made_on = time
        Attempt.player = player
        Attempt.results = []
        Attempt.number_of_tests = len(tests)
        Attempt.put()
        Attempt.Run(tests)
        
        return Attempt
   
    def Run(self, tests):
        for test in tests:
            testrun = test.Run(self.implementation)
            testrun.attempt = self
            testrun.put()
            self.results.append(testrun) 
    
class Test(db.Model):
    game = db.ReferenceProperty(Game) 
    number = db.IntegerProperty()
    code = db.StringProperty(multiline=True)
    author = db.UserProperty()
    date_created = db.DateTimeProperty()
    editor = db.UserProperty()
    date_edited = db.DateTimeProperty(auto_now_add=True)
    
    def Run(self, implementation, tester = users.get_current_user()):
        if not implementation.is_saved():
            implementation.save()
            
        testRun = TestRun(game = self.game, test = self, implementation = implementation, tester = tester, date_created = datetime.now(), result = False)
        
        local_scope = {}
        global_scope = self.get_global_scope()
        
        try:
            exec self.replace_dangerous_statements(self.remove_carriage_return(implementation.code)) in global_scope, local_scope           
            try:
                exec self.remove_carriage_return(self.code) in global_scope.update(local_scope), local_scope
                testRun.result = True
            except AssertionError, inst:
                testRun.error = "Assertion failed: " + str(inst);
            except SyntaxError, inst:
                testRun.error = "Parsing the test failed: " + str(inst);
            except Exception, inst:
                testRun.error = "Running the test failed: " + str(inst);
    
        except SyntaxError, inst:
            testRun.error = "Parsing the implementation failed: " + str(inst);
        except Exception, inst:
            testRun.error = "Couldn't execute your implementation: " + str(inst);
        
        return testRun
    
    def replace_dangerous_statements(self, code):
        p = re.compile( '(\W|^)(eval|exec|import)(\W|$)')
        return p.sub( '#', code)
    
    def remove_carriage_return(self, input):
        return input.replace("\r", ""); 
    
    def get_global_scope(self):
        global_scope = {}
        global_scope['__builtins__'] = {}
        whitelist = ['bytearray','IndexError','all','help','vars','SyntaxError','unicode','UnicodeDecodeError','isinstance', 'hasattr', 'getattr'
                     'copyright','NameError','BytesWarning','dict','oct','bin','StandardError','format','repr','sorted','False',
                     'RuntimeWarning','list','iter','Warning','round','cmp','set','bytes','reduce','intern','issubclass','Ellipsis',
                     'EOFError','BufferError','slice','FloatingPointError','sum','abs','print','True','FutureWarning','ImportWarning',
                     'None','hash','ReferenceError','len','credits','frozenset','ord','super','TypeError','license','KeyboardInterrupt',
                     'UserWarning','filter','range','staticmethod','SystemError','BaseException','pow','RuntimeError','float',
                     'MemoryError','StopIteration','divmod','enumerate','apply','LookupError','basestring','UnicodeError','zip','hex',
                     'long','next','ImportError','chr','xrange','type','Exception','tuple','UnicodeTranslateError','reversed',
                     'UnicodeEncodeError','IOError','SyntaxWarning','ArithmeticError','str','property','GeneratorExit','int','KeyError',
                     'coerce','PendingDeprecationWarning','EnvironmentError','unichr','id','OSError','DeprecationWarning','min',
                     'UnicodeWarning','any','complex','bool','ValueError','NotImplemented','map','buffer','max','object','TabError',
                     'ZeroDivisionError','IndentationError','AssertionError','classmethod','UnboundLocalError','NotImplementedError',
                     'AttributeError','OverflowError','WindowsError','__name__']
        
        for key in __builtins__:
            if key in whitelist:
                global_scope['__builtins__'][key] = __builtins__[key]
        
        return global_scope


class TestRun(db.Model):
    game = db.ReferenceProperty(Game)
    attempt = db.ReferenceProperty(Attempt) 
    implementation = db.ReferenceProperty(Implementation) 
    test = db.ReferenceProperty(Test)
    result = db.BooleanProperty()
    error = db.StringProperty()
    tester = db.UserProperty()
    date_created = db.DateTimeProperty()
    
    def HasImplementation(self):
        try:
            return not self.implementation is None
        except: 
            return False
    

