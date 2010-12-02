'''
Created on 25 nov. 2010

@author: rickvanderarend
'''
import os
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from model.domain import Game

class TddPage(webapp.RequestHandler): 
   
    def __init__(self):
        self.selected_game = None
    
    def get_default_template_values(self):
        user = users.get_current_user()
        if user:
            is_logged_in = True
            username = user.nickname()
            is_admin = users.is_current_user_admin()
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            is_logged_in = False
            username = 'Anonymous'
            is_admin = False
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        return self.add_selected_game({
            'main_form_action' : self.main_form_action(),
            'is_logged_in': is_logged_in,
            'username': username,
            'user' : user,
            'is_admin': is_admin,
            'login_link': url,
            'login_linktext': url_linktext
            })
     

    def render_error_with(self, template_values):
        return self.render_with('main_error', template_values)

    def refresh_selected_game(self):
        self.template_values = self.add_selected_game(self.template_values)

    def set_selected_game(self, selected_game_key):
        if not selected_game_key is None and selected_game_key != '':
            self.selected_game = db.get(selected_game_key)

    def get_selected_game(self):
        game = self.selected_game if not(self.selected_game is None) else None
        if game is None and not(self.request.get('selected_game') is None) and self.request.get('selected_game') != '':
            game = db.get(self.request.get('selected_game'))
            
        return game

    def get_published_games(self):
        published_games = []
        for agame in db.GqlQuery("Select * From Game"):
            if not agame.published:
                continue
            published_games.append(agame)
        return published_games

    def add_selected_game(self, template_values):
        template_values['games'] = self.get_published_games()

        selected_game = self.get_selected_game()         
        lastowngame = None

        if not template_values['games'] is None:
            for agame in template_values['games']:
                if self.request.get('command') == "SelectGame":                  
                    if str(agame.key()) == self.request.get('game_to_select'):  
                        selected_game = agame     
                if agame.IsAuthor(template_values['user']):
                    lastowngame = agame
              
        if selected_game is None and not lastowngame is None:
            selected_game = lastowngame
        
        if selected_game is None and not template_values['games'] is None and len(template_values['games']) > 0:
            selected_game = template_values['games'][len(template_values['games']) - 1]

        if selected_game is None:
            selected_game = Game.Create('Default')
            selected_game.put()

        template_values['user_owns_game'] = selected_game.IsAuthor(template_values['user']) 
        template_values['selected_game'] = selected_game
            
        return template_values
       
    def render_with(self, name, values):
        path = os.path.join(os.path.dirname(__file__), 'templates/'+ name +'.html')
        self.response.out.write(template.render(path, values)) 