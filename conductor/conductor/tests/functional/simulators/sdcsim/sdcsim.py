#
# -------------------------------------------------------------------------
#   Copyright (C) 2021 Wipro Limited.
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

from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import requests


PORT = 9595





class MockServerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        # Process an HTTP GET request and return a response with an HTTP 200 status.
                    # Add response status code.
            if self.path=="/sdc/v1/catalog/services/5d345ca8-1f8e-4f1e-aac7-6c8b33cc33e7/toscaModel":
                self.send_response(requests.codes.ok)

                # Add response headers.
                self.send_header('Content-Type', 'application/octet-stream; charset=utf-8')
                self.end_headers()

                # Add response content.
                fileres=open("newembbnst.csar",'rb')
                response_content = fileres.read()
                self.wfile.write(response_content)
                return
            else:
                self.wfile.write("incorrect url".encode())
                return

handlerobj = MockServerRequestHandler

myserver = socketserver.TCPServer(('', PORT), handlerobj)
myserver.serve_forever()
