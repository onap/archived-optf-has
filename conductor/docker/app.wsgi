"""Use this file for deploying the API under mod_wsgi.
See http://pecan.readthedocs.org/en/latest/deployment.html for details.
"""
from conductor import service
from conductor.api import app

# Initialize the oslo configuration library and logging

# Prepare service-wide components (e.g., config)
conf = service.prepare_service(
     [], config_files=['/usr/local/etc/conductor/conductor.conf'])

#conf = service.prepare_service([])
application = app.load_app(conf)
