"""Use this file for deploying the API under mod_wsgi.
See http://pecan.readthedocs.org/en/latest/deployment.html for details.
"""
from conductor import service
from conductor.api import app

# Initialize the oslo configuration library and logging
conf = service.prepare_service([])
application = app.load_app(conf)