from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from model.domain import TestRun
from model.domain import Implementation
from model.domain import GameRun
from model.domain import Game

from performTest import tester
from TddPage import TddPage
from datetime import datetime

class MainPage(TddPage): 
   
    def get(self, code = False):
        self.output_body(code)   
    
    def post(self):
        self.output_body(self.request.get('code'))
    
    def main_form_action(self):
        return "/"
    
    def get_player_name(self, template_values):
        return self.request.get('playerName') if not self.request.get('playerName') is None else template_values['username']

    def output_body(self, code):
        template_values = self.get_default_template_values()
        
        number_of_tests = 1
        number_of_tries = 0
        template_values['game_number_of_tests'] = str(number_of_tests);
        template_values['game_tries'] = str(number_of_tries);  
        template_values['playerName'] = self.get_player_name(template_values)
                          
        if template_values['is_logged_in']:
            game = template_values['selected_game']
            
            gameRun = game.get_run(users.get_current_user())             
            tests =  game.get_tests()
                        
            if self.request.get('command') == "Test":         
                is_attempt = True
            elif self.request.get('command') == "GetTheStartImplementationAgain":                              
                code = game.start_implementation
                is_attempt = False
            else:
                code = gameRun.get_last_implementation_code()                   
                template_values['playerName'] = template_values['username']
                is_attempt = False 
            
            gameRun.playerName = template_values['playerName']        
            template_values['game_current_input'] = code;           

            number_of_tests = gameRun.number_of_tests_shown
            number_of_tries = (gameRun.number_of_tries + (1 if is_attempt else 0)) if not (gameRun.number_of_tries is None) else (1 if is_attempt else 0)
                              
            template_values['testresults'] = [None] * gameRun.number_of_tests_shown
            number_of_tests_in_game = 0
            
            implementation = Implementation(gameRun = gameRun, code = code, author = users.get_current_user(), date_created = datetime.now());
            if is_attempt: implementation.put()
            
            for test in tests:
                if number_of_tests_in_game < gameRun.number_of_tests_shown:
                    template_values['testresults'][number_of_tests_in_game] = tester(TestRun(game = game, test = test, tester = users.get_current_user(), date_created = datetime.now()), implementation)
                    if is_attempt:
                        template_values['testresults'][number_of_tests_in_game].implementation = implementation
                        template_values['testresults'][number_of_tests_in_game].put()              
                elif number_of_tests_in_game == gameRun.number_of_tests_shown:
                    new_test = test
                    
                number_of_tests_in_game = number_of_tests_in_game + 1
            
            if (gameRun.number_of_tests_shown > number_of_tests_in_game):
                gameRun.number_of_tests_shown = number_of_tests_in_game
                template_values['testresults'] = template_values['testresults'][0:gameRun.number_of_tests_shown]
                        
            if number_of_tests_in_game > 0 and gameRun.number_of_tests_shown < number_of_tests_in_game or not all(map(lambda t: t.result == True, template_values['testresults'])):
                if all(map(lambda t: t.result == True, template_values['testresults'])):             
                    if gameRun.number_of_tests_shown < number_of_tests_in_game:
                        template_values['new_test'] = new_test;
                    gameRun.number_of_tests_shown = gameRun.number_of_tests_shown + 1   
                template_values['game_show_input'] = True; 
             
            template_values['game_number_of_tests'] = str(gameRun.number_of_tests_shown);
            template_values['game_tries'] = str(number_of_tries);         
            
            gameRun.number_of_tries = number_of_tries   
            gameRun.datetime_lastaction = datetime.now()
            if is_attempt: gameRun.put()
            
            number_of_tests = gameRun.number_of_tests_shown
        else:
            template_values['playerName'] = "Anonymous"
            template_values['new_test'] = template_values['selected_game'].get_tests().get();
            template_values['game_show_input'] = True;
            template_values['game_current_input'] = template_values['selected_game'].start_implementation;
             
             
        template_values['game_number_of_tests'] = str(number_of_tests);
        template_values['game_tries'] = str(number_of_tries);              
        
        self.render_with('main_home', template_values)


application = webapp.WSGIApplication([('/', MainPage)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
