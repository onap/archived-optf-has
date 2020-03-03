#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
#   Copyright (C) 2020 Wipro Limited.
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
import json

import web
import web.webapi

urls = (
  '/healthcheck','healthcheck',
  '/aai/v14/cloud-infrastructure/cloud-regions/','get_regions',
  '/aai/v14/cloud-infrastructure/complexes/complex/DLLSTX233','get_complex_DLLSTX233',
  '/aai/v14/cloud-infrastructure/cloud-regions/cloud-region/HPA-cloud/cloud-region-1/flavors/', 'get_flavors_region_1',
  '/aai/v14/cloud-infrastructure/cloud-regions/cloud-region/HPA-cloud/cloud-region-2/flavors/', 'get_flavors_region_2',
  '/aai/v14/nodes/service-instances', 'get_nssi',
)


myhelp = {"/conductorsim/help":"provides help"}
myok = {"ok":"ok"}
json_data={}

replydir = "./responses/"

def replyToAaiGet(web, replydir, replyfile):
        print ("------------------------------------------------------")
        fullreply = replydir + replyfile
        trid=web.ctx.env.get('X_TRANSACTIONID','111111')
        #print ("X-TransactionId : {}".format(trid))
        print ("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            print(json_data)
   
        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)

class healthcheck:
    def GET(self):
        print ("------------------------------------------------------")
        replyfile = "healthcheck.json"
        #replyToAaiGet (web, replydir, replyfile)
        fullreply = replydir + replyfile
        trid=web.ctx.env.get('X_TRANSACTIONID','111111')
        #print ("X-TransactionId : {}".format(trid))
        print ("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            print(json_data)
   
        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)

class get_regions:
    def GET(self):
        print ("------------------------------------------------------")
        replyfile = "get_onap_regions.json"
        #replyToAaiGet (web, replydir, replyfile)
        fullreply = replydir + replyfile
        trid=web.ctx.env.get('X_TRANSACTIONID','111111')
        #print ("X-TransactionId : {}".format(trid))
        print ("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            print(json_data)
   
        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)

class get_complex_DLLSTX233:
    def GET(self):
        print ("------------------------------------------------------")
        replyfile = "get_onap_complex_DLLSTX233.json"
        #replyToAaiGet (web, replydir, replyfile)
        fullreply = replydir + replyfile
        trid=web.ctx.env.get('X_TRANSACTIONID','111111')
        #print ("X-TransactionId : {}".format(trid))
        print ("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            print(json_data)
   
        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)

class get_flavors_region_1:
    def GET(self):
        print ("------------------------------------------------------")
        replyfile = "get_flavors_cloud_region_1.json"
        #replyToAaiGet (web, replydir, replyfile)
        fullreply = replydir + replyfile
        trid=web.ctx.env.get('X_TRANSACTIONID','111111')
        #print ("X-TransactionId : {}".format(trid))
        print ("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            print(json_data)
   
        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)

class get_flavors_region_2:
    def GET(self):
        print ("------------------------------------------------------")
        replyfile = "get_flavors_cloud_region_2.json"
        #replyToAaiGet (web, replydir, replyfile)
        fullreply = replydir + replyfile
        trid=web.ctx.env.get('X_TRANSACTIONID','111111')
        #print ("X-TransactionId : {}".format(trid))
        print ("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            print(json_data)
   
        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)


class get_nssi:
    def GET(self):
        print("------------------------------------------------------")
        replyfile = "get_nssi_response.json"
        # replyToAaiGet (web, replydir, replyfile)
        fullreply = replydir + replyfile
        trid = web.ctx.env.get('X_TRANSACTIONID', '111111')
        # print ("X-TransactionId : {}".format(trid))
        print("this is the context : {}".format(web.ctx.fullpath))
        with open(fullreply) as json_file:
            json_data = json.load(json_file)
            print(json_data)

        web.header('Content-Type', 'application/json')
        web.header('X-TransactionId', trid)
        return json.dumps(json_data)


if __name__ == "__main__": 
    app = web.application(urls, globals())
    app.run()
