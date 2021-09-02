'''
Created on Aug 28, 2021

@author: warno006089
'''

import json
import decimal
import datetime
import pkgutil
from werkzeug.utils import import_string
from werkzeug.wrappers import Response
from mako.lookup import TemplateLookup
from .session import FilesystemSessionStore
from .config import config

session_store = FilesystemSessionStore()


class DynamicJSONEncoder(json.JSONEncoder):
    """ JSON encoder for custom classes:

        Uses __json__() method if available to prepare the object.
        Especially useful for SQLAlchemy models
    """

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            # return (str(o) for o in [o])
            return str(o)
        
        elif isinstance(o, datetime.datetime):
            return str(o)
        
        elif isinstance(o, datetime.date):
            return str(o)

        # Custom JSON-encodeable objects
        elif hasattr(o, '__json__'):
            return o.__json__()

        # Default
        return super(DynamicJSONEncoder, self).default(o)


class BaseController(object):
    template_lookup = TemplateLookup([
            'templates', 'templates/modules',])
    json_encoder = DynamicJSONEncoder
    
    def __init__(self):
        '''
        Constructor
        '''
        env = self._load_packages(config['config']['module_path'], 'modules', None)
        self.env = env

    def html_response(self, template_uri, data=None):
        template = self.template_lookup.get_template(template_uri)
        html = template.render(data=data)
        return Response(html, mimetype='text/html')

    def json_response(self, data):
        return Response(
            json.dumps(data, cls=self.json_encoder),
            mimetype='application/json'
        )
    
    def _load_packages(self, path, basename, append=None):
        packages = dict()   
        if isinstance(path, str):
            path = path.split(',')
        # if basename is None:
        #     basename = self._module_basename
        for _importer, modname, ispkg in pkgutil.iter_modules(path):
            if ispkg:
                import_name = basename + '.' + modname
                module = import_string(import_name)
                packages[modname] = module
        return packages
    

class Controller(BaseController):
    '''
    classdocs
    '''
        
    def home(self, request):
        return self.html_response('/home.html', {
            'title': 'Home'})
        
    def auth(self, request):
        auth = self.env['auth'].controller.AuthController()
        return auth.run(request)
    
    def web(self, request):
        data = {
            'title': 'Course'}
        rows = self.create(request)
        return self.html_response('/app.html', data)
    
    def api(self, request):
        pass
    
    def create(self, request):
        model = self.env['auth'].models.AuthUser
        res = model.create(self.env, **{})
        return res
    
    def run(self, request, endpoint):
        method_ = getattr(self, endpoint)
        response = method_(request)
        return response
    
    
