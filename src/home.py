from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from TddPage import TddPage

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
        
        template_values['playerName'] = self.get_player_name(template_values)
                          
        if template_values['is_logged_in']:
            game = template_values['selected_game']
            
            gameRun = game.Play(player_name = template_values['playerName'])             
                                 
            if self.request.get('command') == "Test":     
                template_values['results'] = gameRun.GetResultsOfNewTestRun(self.request.get('code'))
            elif self.request.get('command') == "GetTheStartImplementationAgain":                              
                template_values['results'] = gameRun.GetCurrentTestResultsUsingStartImplementation()
            else:               
                template_values['results'] = gameRun.GetCurrentTestResults() 
                    
            template_values['game_current_input'] = template_values['results']['for'].code;           
            template_values['game_show_input'] = not gameRun.IsFinished()            
            template_values['game_number_of_tests'] = str(gameRun.number_of_tests_shown);
            template_values['game_tries'] = str(gameRun.number_of_tries);         
            
        else:
            template_values['game_number_of_tests'] = str(1);
            template_values['game_tries'] = str(0); 
            template_values['playerName'] = "Anonymous"
            template_values['new_test'] = template_values['selected_game'].GetTests().get();
            template_values['game_show_input'] = True;
            template_values['game_current_input'] = template_values['selected_game'].start_implementation;          
        
        self.render_with('main_home', template_values)


application = webapp.WSGIApplication([('/', MainPage)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
