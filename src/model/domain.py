'''
Created on 25 nov. 2010

@author: rickvanderarend
'''
import re
from google.appengine.ext import db
from google.appengine.api import users
from datetime import datetime

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
    

    def SaveIfNotSaved(self):
        if not self.is_saved():
            self.save()

    def StartRun(self, player, playerName):
        self.SaveIfNotSaved()
        
        gameRun = GameRun()
        gameRun.game = self
        gameRun.number_of_tests_shown = 1
        gameRun.number_of_tests_ok = 0
        gameRun.number_of_tries = 0
        gameRun.player = player
        gameRun.playerName = playerName
        gameRun.datetime_started = datetime.now()
        gameRun.datetime_lastaction = datetime.now()
        gameRun.finished = False
        gameRun.put()
        
        return gameRun
    
    def Play(self, player = users.get_current_user(), player_name = None):
        if player_name is None:
            player_name = player.nickname()
            
        gameRun = None
        try :
            gameRun = db.GqlQuery("Select * From GameRun Where game = :1 AND player = :2 Order by datetime_lastaction DESC", self, player).get()
            gameRun.player_name = player_name
        except:
            gameRun = None

        if gameRun == None:
            gameRun = self.StartRun(player, player_name)
        else:
            if gameRun.number_of_tests_shown is None:
                gameRun.number_of_tests_shown = gameRun.number_of_tests_ok
        
        return gameRun
    
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

    def SaveIfNotSaved(self):
        if not self.is_saved():
            self.save()
    
    def GetImplementation(self, code = None):
        last = self.GetLastImplementation()
        
        if not last is None and (code is None or last.code == code):
            implementation = last
        elif code is None:
            implementation = self.GetStartImplementation()
        else:
            self.SaveIfNotSaved()
            implementation = Implementation(gameRun = self, code = code, author = self.player, date_created = datetime.now())
            implementation.save()
        
        return implementation
    
    def GetLastImplementation(self):
        last_implementation = None
        try :
            last_implementation = db.GqlQuery("Select * From Implementation Where gameRun = :1 Order by date_created DESC", self).get()
        except:
            last_implementation = None
            
        return last_implementation

    def GetStartImplementation(self):
        self.SaveIfNotSaved()
        return Implementation(gameRun = self, code = self.game.start_implementation, author = self.player, date_created = datetime.now())
        
    def IsFinished(self):
        return self.finished
    
    def GetCurrentNumberOfTries(self):
        return (self.number_of_tries) if not (self.number_of_tries is None) else 0
    
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

    def AreTestResultsEnoughToFinish(self, test_results, number_of_tests_in_game):      
        return number_of_tests_in_game > 0 and self.HasMoreTestsThanShown(number_of_tests_in_game) or not self.AreAllResultsSuccessful(test_results)

    def ShowOneMoreTest(self):
        self.number_of_tests_shown = self.number_of_tests_shown + 1

    def GetTestResults(self, implementation, is_attempt = False):      
        tests =  self.game.GetTests()
        
        results = {}
        results['for'] = implementation                 
        results['test_results'] = [None] * self.number_of_tests_shown
        number_of_tests_in_game = 0
        
        for test in tests:
            if number_of_tests_in_game < self.number_of_tests_shown:
                results['test_results'][number_of_tests_in_game] = test.Run(implementation)
                if is_attempt:
                    results['test_results'][number_of_tests_in_game].put()              
            elif number_of_tests_in_game == self.number_of_tests_shown:
                new_test = test
                
            number_of_tests_in_game = number_of_tests_in_game + 1
        
        if (self.number_of_tests_shown > number_of_tests_in_game):
            self.number_of_tests_shown = number_of_tests_in_game
            results['test_results'] = results['test_results'][0:self.number_of_tests_shown]
                    
        if self.AreTestResultsEnoughToFinish(results['test_results'], number_of_tests_in_game):
            if self.AreAllResultsSuccessful(results['test_results']):             
                if self.HasMoreTestsThanShown(number_of_tests_in_game):
                    results['new_test'] = new_test;
                self.ShowOneMoreTest()   
            self.finished = False
        else:
            self.finished = True
             
        self.datetime_lastaction = datetime.now()
        if is_attempt: self.put()
        
        return results
    
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
    
class Implementation(db.Model):
    gameRun = db.ReferenceProperty(GameRun) 
    code = db.TextProperty()
    author = db.UserProperty()
    date_created = db.DateTimeProperty()

class TestRun(db.Model):
    game = db.ReferenceProperty(Game)
    gameRun = db.ReferenceProperty(GameRun) 
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
    

