from google.appengine.ext import db
from google.appengine.api import users
import re
from datetime import datetime

class Game(db.Model):
    name = db.StringProperty()
    start_implementation = db.TextProperty()
    published = db.BooleanProperty()   
    author = db.UserProperty()
    date_created = db.DateTimeProperty()
    number_of_tests = db.IntegerProperty()

    @classmethod
    def Create(cls, name = None, author = users.get_current_user(), time = datetime.now()):
        game = cls()
        game.name = name if not name is None else "Game_" + str(author) + "_" + str(time)
        game.author = author
        game.published = True   
        game.date_created = time
        game.number_of_tests = 0
        return game
    
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
    
    def Run(self, playerName, player = users.get_current_user()):
        if not self.is_saved():
            self.save()
        
        gameRun = GameRun()
        gameRun.game = self
        gameRun.number_of_tests_shown = 1
        gameRun.number_of_tests_ok = 0
        gameRun.player = player
        gameRun.playerName = playerName
        gameRun.datetime_started = datetime.now()
        gameRun.datetime_lastaction = datetime.now()
        gameRun.finished = False
        gameRun.put()
        
        return gameRun
    
    def GetLastRun(self, player = users.get_current_user()):
        gameRun = None
        try :
            gameRun = db.GqlQuery("Select * From GameRun Where game = :1 AND player = :2 Order by datetime_lastaction DESC", self, player).get()
        except:
            gameRun = None

        if gameRun == None:
            gameRun = self.Run(player.nickname(), player)
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
    
    def get_last_implementation_code(self):
        last_implementation = None
        try :
            last_implementation = db.GqlQuery("Select * From Implementation Where gameRun = :1 Order by date_created DESC", self).get()
        except:
            last_implementation = None
            
        return last_implementation.code if not last_implementation is None else self.game.start_implementation

    def is_finished(self):
        return self.finished
    
    def attempt(self, code):
        self.finished = (self.game.number_of_tests == 0)
    
class Test(db.Model):
    game = db.ReferenceProperty(Game) 
    number = db.IntegerProperty()
    code = db.StringProperty(multiline=True)
    author = db.UserProperty()
    date_created = db.DateTimeProperty()
    editor = db.UserProperty()
    date_edited = db.DateTimeProperty(auto_now_add=True)
    
    def test(self, implementation):
        testRun = TestRun()
        testRun.result = False
        local_scope = {}
        global_scope = self.get_global_scope()
        try:
            exec self.replace_dangerous_statements(self.remove_carriage_return(implementation.code)) in global_scope, local_scope           
            try:
                exec self.remove_carriage_return(testRun.test.code) in global_scope.update(local_scope), local_scope
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

