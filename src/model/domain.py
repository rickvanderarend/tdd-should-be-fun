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
    def create(cls, name, author = users.get_current_user(), time = datetime.now()):
        game = cls()
        game.name = name if not name is None else "Game_" + str(author) + "_" + str(time)
        game.author = author
        game.published = True   
        game.date_created = time
        game.number_of_tests = 0
        game.put()
        return game
    
    def publish(self):
        self.published = True
        
    def set_start_implementation(self, impl):
        self.start_implementation = impl
    
    def get_tests(self):
        return db.GqlQuery("SELECT * FROM Test Where game = :1 ORDER BY number ASC", self);
    
    def add_test(self, code):
        new_test = Test()
        new_test.game = self
        
        if users.get_current_user():
            new_test.author = users.get_current_user()
            new_test.date_created = datetime.now()
            new_test.editor = users.get_current_user()

        new_test.code = code
        self.number_of_tests = self.number_of_tests + 1
        new_test.number = self.number_of_tests
        new_test.put()
        self.put()
    
    def start_run(self, playerName, player = users.get_current_user()):
        gameRun = GameRun()
        gameRun.game = self
        gameRun.number_of_tests_shown = 1
        gameRun.number_of_tests = 0
        gameRun.player = player
        gameRun.playerName = playerName
        gameRun.datetime_started = datetime.now()
        gameRun.datetime_lastaction = datetime.now()
        gameRun.finished = False
        gameRun.put()
        
        return gameRun
    
    def get_run(self, player):
        gameRun = None
        try :
            gameRun = db.GqlQuery("Select * From GameRun Where game = :1 AND player = :2 Order by datetime_lastaction DESC", self, player).get()
        except:
            gameRun = None

        #print gameRun.game.name

        if gameRun == None:
            gameRun = self.start_run(player.nickname(), player)
        else:
            if gameRun.number_of_tests_shown is None:
                gameRun.number_of_tests_shown = gameRun.number_of_tests
        
        return gameRun
    
class GameRun(db.Model):
    game = db.ReferenceProperty(Game) 
    number_of_tests_shown = db.IntegerProperty()
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
    
    def make_attempt(self, code):
        finished = (self.game.number_of_tests == 0)
    
class Test(db.Model):
    game = db.ReferenceProperty(Game) 
    number = db.IntegerProperty()
    code = db.StringProperty(multiline=True)
    author = db.UserProperty()
    date_created = db.DateTimeProperty()
    editor = db.UserProperty()
    date_edited = db.DateTimeProperty(auto_now_add=True)
    
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

