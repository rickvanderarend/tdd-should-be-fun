from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from model.domain import Test
from TddPage import TddPage
from datetime import datetime
from model.domain import Game

class GamesPage(TddPage):
    
    def main_form_action(self):
        return "/games"
       
    def render_with_tests(self, view):
        self.render_with("main_games_" + view, self.template_values)

    def delete(self, key):
        db.delete(key)
        self.template_values['game'] = self.add_selected_game(self.template_values)
        return "index"       

    def edit(self, key):
        self.template_values['game'] = db.get(key)
        return "edit"

    def view(self, key):
        self.template_values['game'] = db.get(key)
        return "view"
    
    def index(self):
        return "index"

    def get(self, key = "", command = "view"):
        self.template_values = self.get_default_template_values()
        
        if command == 'delete' and key <> "":
            view = self.delete(key)
            
        elif command == 'edit' and key <> "":
            view = self.edit(key)
        elif command == 'view' and key <> "":
            view = self.view(key)
        else:
            view = self.index()

        self.render_with_tests(view)           

    def post(self, key = ""):
        self.template_values = self.get_default_template_values()
        
        command = self.request.get('command')
       
        try:
            author = users.User(self.request.get('new_game_author'))
        except Exception, inst:
            author = users.get_current_user()
        
        if command == "Add":
            game = Game.Create(self.request.get('new_game_name'), author)
            game.SetStartImplementation(self.request.get('new_game_start_implementation'))
        if command == "Edit":
            game = db.get(self.request.get('game_key'))   
            game.name = self.request.get('game_name')
            game.SetStartImplementation(self.request.get('game_start_implementation'))
                
        game.put()
        
        self.template_values = self.add_selected_game(self.template_values)
        self.render_with_tests('index')
        
        
application = webapp.WSGIApplication([('/games', GamesPage),('/games/([^/]*)', GamesPage),('/games/([^/]*)/(.*)', GamesPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()