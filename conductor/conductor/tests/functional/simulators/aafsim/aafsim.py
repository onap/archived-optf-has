#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 OAM Technology Consulting LLC Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#
import web
import web.webapi
import json

from subprocess import Popen, PIPE
from oslo_log import log
LOG = log.getLogger(__name__)

urls = (
  '/healthcheck','healthcheck',
  '/authz/perms/user/','get_perms_user',
)

myhelp = {"/conductorsim/help":"provides help"}
myok = {"ok":"ok"}
json_data={}

replydir = "./responses/"

def replyToAafGet(web, replydir, replyfile):
        LOG.debug("------------------------------------------------------")
        fullreply = replydir + replyfile
        trid=web.ctx.env.get('X_TRANSACTIONID','111111')
        #print ("X-TransactionId : {}".format(trid))
        LOG.debug("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            LOG.debug(json_data)   
        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)

class healthcheck:
    def GET(self):
        LOG.debug("------------------------------------------------------")
        replyfile = "healthcheck.json"
        #replyToAaiGet (web, replydir, replyfile)
        fullreply = replydir + replyfile
        trid=web.ctx.env.get('X_TRANSACTIONID','111111')
        #print ("X-TransactionId : {}".format(trid))
        LOG.debug("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            LOG.debug(json_data)
        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)

class get_perms_user:
    def GET(self):
        LOG.debug("------------------------------------------------------")
        replyfile = "get_perms_user.json"
        #replyToAafGet (web, replydir, replyfile)
        fullreply = replydir + replyfile
        trid=web.ctx.env.get('X_TRANSACTIONID','111111')
        #print ("X-TransactionId : {}".format(trid))
        LOG.debug("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            LOG.debug(json_data)   
        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)



if __name__ == "__main__": 
    app = web.application(urls, globals())
    app.run()
