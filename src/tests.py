'''
Created on 25 nov. 2010

@author: rickvanderarend
'''
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from TddPage import TddPage
from datetime import datetime

class TestsPage(TddPage):
    
    def main_form_action(self):
        return "/tests"
       
    def render_with_tests(self, view):
        self.render_with("main_tests_" + view, self.template_values)
    
    def get_tests(self):       
        return self.template_values['selected_game'].GetTests()

    def delete(self, key):
        db.delete(key)
        self.template_values['tests'] = self.get_tests()
        return "index"       

    def edit(self, key):
        self.template_values['test'] = db.get(key)
        return "edit"

    def view(self, key):
        self.template_values['test'] = db.get(key)
        return "view"
    
    def index(self):
        self.template_values['tests'] = self.get_tests()
        return "index"       
    

    def user_has_no_rights(self):
        return not (self.template_values['user_owns_game'] or self.template_values['is_admin'])
            

    def get(self, game = "", subject = "", command = "view"):
        self.set_selected_game(game)
        self.template_values = self.get_default_template_values()
        
        if self.user_has_no_rights():
            self.render_error_with(self.template_values)
            return
        
        if subject == "details" and command == "edit":
            self.render_with("main_tests_game_edit" , self.template_values)
            return
        
        if command == 'delete' and subject <> "":
            view = self.delete(subject)
        elif command == 'edit' and subject <> "":
            view = self.edit(subject)
        elif command == 'view' and subject <> "":
            view = self.view(subject)
        else:
            view = self.index()

        self.render_with_tests(view)           

    def post(self):
        self.template_values = self.get_default_template_values()

        number_of_tests = 1
        command = self.request.get('command')
        
        if self.user_has_no_rights():
            self.render_error_with(self.template_values)
            return
                   
        game = self.template_values['selected_game']
        
        if command == "EditGameDetails":  
            game.name = self.request.get('game_name')
            game.SetStartImplementation(self.request.get('game_start_implementation'))
            game.put()
        
        tests = self.get_tests()
        
        for test in tests:
            number_of_tests += 1
        
        if command == "Add":
            game.AddTest(self.request.get('new_test_code'))
        if command == "Edit":
            test = db.get(self.request.get('test_key'))   
            test.code = self.request.get('test_code')
            test.number = int(self.request.get('test_number'))
            if users.get_current_user():
                test.editor = users.get_current_user()
                test.date_edited = datetime.now()              
            test.put()   
        
        self.template_values['tests'] = self.get_tests()
        self.render_with_tests('index')
        
        
application = webapp.WSGIApplication([('/tests', TestsPage),('/tests/([^/]*)/([^/]*)/(.*)', TestsPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()