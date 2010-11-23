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


    def set_selected_game(self, selected_game_key):
        self.selected_game = selected_game_key

    def get_selected_game(self):
        return self.selected_game if not(self.selected_game is None) else self.request.get('selected_game')

    def add_selected_game(self, template_values):
        games = db.GqlQuery("Select * From Game")
        n = 0

        for agame in games:
            print str(n) +": "+ agame.name
            if not agame.published:
                continue
            n += 1
        
        template_values['games'] = [None] * n
        n = 0
        game = None           
        #print "I"+ self.request.get('command') +"I"
        #print "I"+ self.request.get('selected_game') +"I"
        #print "I"+ self.request.get('game_to_select') +"I"
        for agame in games:
            print str(n) +": "+ agame.name
            if not agame.published:
                continue
            
            if game is None:
                #print "game is not none I"
                #not(self.request.get('selectAnotherGame') is None) and
                if  (self.request.get('command') == "SelectGame"):
                    
                    if (str(agame.key()) ==  self.request.get('game_to_select')):  
                        game = agame
                        agame.selected = True
                        #print "I selected gts "+ self.request.get('game_to_select') +"I"
                elif not (self.get_selected_game() is None):
                    if (str(agame.key()) ==  self.get_selected_game()):
                        game = agame
                        agame.selected = True
                        #print "I selected sg "+ self.request.get('selected_game') +"I"
            
            template_values['games'][n] = agame
            print str(n) +": "+ template_values['games'][n].name
            n += 1
        
        #print "'"+self.get_selected_game()+"'"
        #print "'"+self.request.get('selected_game')+"'"
        
        myowngame = None
        
        if game is None:
            for agame in template_values['games']:
                if not(agame.author is None) and agame.author == template_values['user']:
                    if myowngame is None:
                        myowngame = agame
                        myowngame.selected = True
                    else:
                        myowngame.selected = False              
        
        if not(myowngame is None) and myowngame.selected:
            game = myowngame
        
        if game is None:
            game = template_values['games'][n-1]
            game.selected = True
        
        if game is None:
            template_values['message'] = "Sorry, the game you requested doesn't exist.";                     
            self.render_error_with(template_values)
        
        #print game.author()
        if not(game.author is None) and game.author == template_values['user']:
            template_values['user_owns_game'] = True
        else:
            template_values['user_owns_game'] = False
        
        template_values['selected_game'] = game
        
        return template_values
       
    def render_with(self, name, values):
        path = os.path.join(os.path.dirname(__file__), 'templates/'+ name +'.html')
        self.response.out.write(template.render(path, values)) 