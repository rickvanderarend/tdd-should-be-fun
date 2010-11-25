'''
Created on 25 nov. 2010

@author: rickvanderarend
'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from TddPage import TddPage
import pprint

pp = pprint.PrettyPrinter(indent=4)

def cmp_scores(x, y):
    return cmp(x['score'], y['score'])

class HighScoresPage(TddPage): 
      
    def main_form_action(self):
        return "/highscores"
 
    def get(self):
        template_values = self.get_default_template_values()
        
        testruns  =  db.GqlQuery("SELECT * FROM TestRun")
        
        impl_scores = {}
        for testrun in testruns:
            if testrun.HasImplementation():
                key = str(testrun.implementation.author) +", "+ str(testrun.implementation.date_created)
                if not (key in impl_scores):
                    impl_scores[key] = {'user' : testrun.implementation.author, 'score' : 0, 'tests' : 0 }
                if testrun.result:
                    impl_scores[key]['score'] = impl_scores[key]['score'] + 1
                impl_scores[key]['tests'] = impl_scores[key]['tests'] + 1
                          
        
        template_values['scores'] = sorted(impl_scores.values(), cmp_scores, None, True) 
        
        #self.response.out.write(pp.pprint(template_values['scores'])) 
        
        self.render_with('main_highscores', template_values)  


application = webapp.WSGIApplication([('/highscores', HighScoresPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()