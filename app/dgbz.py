'''
Created on Aug 28, 2021

@author: warno006089
'''

# -*- coding: utf-8 -*-
import os
import pkgutil
import configparser
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.wrappers import Request
from werkzeug.utils import import_string, redirect
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from .controller import Controller


class Backend(object):
    _modules = dict()
    _module_basename = 'modules'
    
    def __init__(self, config):
        self.config = config['config']
        self.url_map = Map([
            Rule('/', endpoint='home'),
            Rule('/auth/<action>', endpoint='auth'),
            Rule('/app/<module>', methods=['GET', 'POST'], endpoint='web'),
            Rule('/api/<module>', methods=['GET', 'POST', 'PUT'], endpoint='api')
        ])
        self.controller = Controller()
        self.controller.init_app(self)
        self._load_packages(self.config['module_path'])
        
    def wsgi_app(self, environ, start_response):
        request = Request(environ)  
        response = self.dispatch_request(request)
        return response(environ, start_response)
    
    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, url_params = adapter.match()
            request.url_params = url_params
            response = self.controller(request, endpoint)
        except HTTPException as e:
            return e
        return response
        
    def _load_packages(self, path, basename=None, append=None):
        if isinstance(path, str):
            path = path.split(',')
        if basename is None:
            basename = self._module_basename
        for _importer, modname, ispkg in pkgutil.iter_modules(path):
            if ispkg:
                import_name = basename + '.' + modname
                module = import_string(import_name)
                self._modules[modname] = module
    
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
    
config_file = './config.conf'
config = configparser.ConfigParser()
config.read(config_file)

def create_app():
    app = Backend(config)
    app = SharedDataMiddleware(app, {
            '/static': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
            '/modules': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules')
    })
    return app
    
            