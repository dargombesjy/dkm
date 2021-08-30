'''
Created on Aug 28, 2021

@author: warno006089
'''

from werkzeug.serving import run_simple
from app.dgbz import create_app

if __name__ == '__main__':
    app = create_app()
    run_simple('127.0.0.1', 5000, app)