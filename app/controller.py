'''
Created on Aug 28, 2021

@author: warno006089
'''

import json
import decimal
import datetime
from pathlib import Path
from mako.lookup import TemplateLookup
from werkzeug.wrappers import Response, response
from werkzeug.utils import redirect
from mypy.dmypy.client import request


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

    def html_response(self, template_uri, data=None):
        template = self.template_lookup.get_template(template_uri)
        html = template.render(data=data)
        return Response(html, mimetype='text/html')

    def json_response(self, data):
        return Response(
            json.dumps(data, cls=self.json_encoder),
            mimetype='application/json'
        )

class Controller(BaseController):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
    
    def home(self, request):
        return self.html_response('/home.html', {
            'title': 'Home'})
        
    def auth(self, request):
        pass
    
    def web(self, request):
        data = {
            'title': 'Course'}
        return self.html_response('/app.html', data)
    
    def api(self, request):
        pass
    
    def init_app(self, app):
        self.app = app
    
    def __call__(self, request, endpoint):
        method_ = getattr(self, endpoint)
        response = method_(request)
        return response
