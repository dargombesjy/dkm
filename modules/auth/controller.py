'''
Created on Aug 31, 2021

@author: warno006089
'''
# import json
from werkzeug.utils import redirect
from app.controller import BaseController, session_store


class AuthController(BaseController):
    def login(self, request):
        attr = {}
        if request.method == 'POST':
            model_ = getattr(self.env['auth'].models, 'AuthUser')
            user = model_.get_by_param(self.db_session(), 'email', request.form['login'])
            if isinstance(user, model_) and user.authenticate(request.form['password']):
                request.session = session_store.new()
                request.session.modified = True
                request.session.update({
                    'logged_in': True,
                    'user': user
                })
                return redirect('/')
            attr['messages'] = ['*Wrong email or password']
        template = '/auth/login.html'
        attr['title'] = 'Login'
        return self.html_response(template, attr)
    
    def register(self, request):
        attr = {}
        if request.method == 'POST':
            form = request.form
            user = self.env['auth'].models.AuthUser
            result = user.create(self.env, **form)
            if result:
                return redirect('/')
        model = self.env['auth'].models.AuthUserGroup
        rows = model.browse([])
        attr['title'] = 'Register'
        attr['data'] = {
            'group': rows}   # json.dumps(rows, cls=self.json_encoder)}
        template = '/auth/register.html'
        return self.html_response(template, attr)
    
    def reset(self, request):
        pass
    
    def logout(self, request):
        pass
    
    def admin(self, request):
        pass
    
    def run(self, request):  # endpoint=None):
        action = getattr(self, request.url_params['action'])
        return action(request)
        