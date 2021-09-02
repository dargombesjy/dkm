'''
Created on Aug 28, 2021

@author: warno006089
'''

# -*- coding: utf-8 -*-
import os
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.wrappers import Request
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from app.config import config
from app.controller import Controller


class Backend(object):
    # _modules = dict()
    # _module_basename = 'modules'
    
    def __init__(self, config):
        self.config = config['config']
        self.url_map = Map([
            Rule('/', endpoint='home'),
            Rule('/auth/<action>', endpoint='auth'),
            Rule('/app/<module>', methods=['GET', 'POST'], endpoint='web'),
            Rule('/api/<module>', methods=['GET', 'POST', 'PUT'], endpoint='api')
        ])
        # packages = self._load_packages(self.config['module_path'], 'modules', None)
        self.controller = Controller()
        
    def wsgi_app(self, environ, start_response):
        request = Request(environ)  
        response = self.dispatch_request(request)
        return response(environ, start_response)
    
    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, url_params = adapter.match()
            request.url_params = url_params
            response = self.controller.run(request, endpoint)
        except HTTPException as e:
            return e
        return response
    
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
    

def create_app():
    app = Backend(config)
    app = SharedDataMiddleware(app, {
        '/static': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
        '/modules': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules')
    })
    return app
    
            