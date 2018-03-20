import web
import web.webapi
import json

from subprocess import Popen, PIPE
from xml.dom import minidom


urls = (
  '/healthcheck','healthcheck',
  '/aai/v13/cloud-infrastructure/cloud-regions/','get_regions',
  '/aai/v13/cloud-infrastructure/complexes/complex/DLLSTX233','get_complex_DLLSTX233',
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



if __name__ == "__main__": 
    app = web.application(urls, globals())
    app.run()
