__author__ = 'Mael Beuget, Pierre Monnin & Thibaut Smith'

from BaseHandler import *


class SignupHandler(BaseHandler):
    def __init__(self, request=None, response=None):
        self.initialize(request, response)
        self.page_name = "signup"

    def get(self):
        self.render('signup.html')