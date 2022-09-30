#  coding: utf-8 
import socketserver
from datetime import datetime

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        print(self)

        # This is just me trying to mimic a proper HTML response
        current_time = datetime.now()

        byte_to_string = self.data.decode('utf-8')
        print(byte_to_string)

        lines = byte_to_string.split("\n")

        command = lines[0].split(" ")[0]
        location = lines[0].split(" ")[1]
        host = lines[1].split(" ")[1]

        if (command == 'PUT' or command == "DELETE" or command== "POST"):
            self.request.sendall(bytearray("HTTP/1.1 405 Moved Permanently\r\n",'utf-8'))
            return

        else:
            try:
                redirected = False
                file_found = False

                if ('../' in location):
                    self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n",'utf-8'))
                    return

                if (location[-1] != '/'):
                    redirect_url = location + '/'   #This might come in handy if we want to redirect

                location = 'www' + location

                #Now we will fix the location here
                temp_location = list(location)
                length = len(temp_location)
                i=0
                while (True):
                    if (i >= (length-1)):
                        break
                    print(i)
                    if (temp_location[i] == '/' and temp_location[i] == temp_location[i+1]):
                        temp_location.pop(i)
                        length = length-1
                        i = i-1
                    i+=1
                
                location = ''.join(temp_location)
        
                index = location.rfind(".")
                if (index == -1):
                    if (location[-1] != '/'):
                        # We'll use 301 here
                        redirected = True
                        
                        location = location + '/index.html'
                    else:
                        location = location + 'index.html'


                print(location)
                #location fixing ends here   
                # This is used to find the format of the file which will be used to find the content-type
                index = location.rfind(".")
                content_type = 'text/' + location[(index+1):]

                file_to_open = open(location)
                data = file_to_open.read()
                data_length = len(data)

                file_found = True

                if (redirected == True and file_found == True):
                    self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\n",'utf-8'))
                    self.request.sendall(bytearray("Location: " + redirect_url + "\r\n",'utf-8'))
                self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n",'utf-8'))
                self.request.sendall(bytearray('Date: ' + str(current_time) + '\r\n','utf-8'))
                self.request.sendall(bytearray('Content-Length: ' + str(data_length) + '\r\n','utf-8'))
                self.request.sendall(bytearray('Content-Type: ' + content_type + '\r\n\r\n','utf-8'))
                
                self.request.sendall(bytearray(data + '\r\n','utf-8'))
                
                return
            except:
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n",'utf-8'))
                return

        # # if (command == 'GET'):
        # #     if (location == '/'):


    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
