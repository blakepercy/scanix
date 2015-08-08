#!/usr/bin/env python

import sys
import socket
import getopt
import threading
import subprocess
from optparse import OptionParser
import os

class netcatcmd:
    def __init__(self, target="", port=0,
                 listen=False, execute="", command=False, upload=""):
        self.target     = target
        self.port       = port
        self.listen     = listen
        self.execute    = execute
        self.command    = command
        self.upload     = upload

    def client_sender(self, buff):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # connect to our target host
            client.connect((self.target, int(self.port)))

            if len(buff):
                client.send(buff)
            while True:
                # now wait for data back
                recv_len = 1
                response = ""
                
                while recv_len:
                    data = client.recv(4096)
                    recv_len = len(data)
                    response += data
                    
                    if recv_len < 4096:
                        break
                
                print response
                
                # wait for more imput
                print "waiting for raw input"
                buff = raw_input("")
                buff += '\n'
                
                print "sending raw input %s" % buff
                # send it off
                client.send(buff)
                
        except:
            print "Exception - client_sender:", sys.exc_info()[0]
            
            # tear down the connection
            client.close()

    def run_command(self, command):
        
        # trim the newline
        command = command.rstrip()
        
        # run the command and get the output back
        try:
            output = subprocess.check_output(command,
                                             stderr = subprocess.STDOUT,
                                             shell = True)
        except:
            print "Exception - run_command:", sys.exc_info()[0]
        
        # send the output back to the client
        return output
    
    def client_handler(self, client_socket):
        try:
            # check for upload
            if self.upload is not None:
                # read in all the bytes and write to our destination
                file_buffer = ""
                
                # keep reading data until none is available
                while True:
                    data = client_socket.recv(1024)
                    
                    if not data:
                        break
                    else:
                        file_buffer += data
                        
                # now we take these bytes and try to write them out
                try:
                    file_descriptor = open(self.upload, "wb")
                    file_descriptor.write(file_buffer)
                    file_descriptor.close()
                    
                    # acknowledge that we wrote the file out
                    client_socket.send("Successfully saved file to %s\r\n"
                                       % self.upload)
                except:
                    client_socket.send("Failed to save file to %s\r\n"
                                       % self.upload)
            
            # check for command execution
            if self.execute is not None:
                
                # run the command
                output = self.run_command(self.execute)
                
                client_socket.send(output)
                
            # now we go into another loop if a command shell was requested
            if self.command:
                
                while True:
                    # show a simple prompt
                    client_socket.send("<BHP:#> ")
                    
                    # now we receive until we see a linefeed (enter key)
                    # the following negative while loop checks each char
                    cmd_buffer = ""
                    while '\n' not in cmd_buffer:
#                        print "receiving a cmd..."
                        cmd_buffer += client_socket.recv(1024)
                        if cmd_buffer == "":
                            break
                    
                    # run the command on the server
                    response = self.run_command(cmd_buffer)
                    print "ran a command..."
                    
                    # send back the response
                    client_socket.send(response)
        except:
            print "Exception - client handler:", sys.exc_info()[0]
            client_socket.close()
            print "Client socket now closed"
    

    def server_loop(self):
        # if no target is defined, we listen on all interfaces
        if self.target is None:
            self.target = "0.0.0.0"
            
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print "binding on %s:%d" % (self.target, int(self.port))
            
            server.bind((self.target, int(self.port)))
            print "about to listen on %s:%d" % (self.target, int(self.port))
            
            server.listen(5)
            print "listening"
            
            while True:
                client_socket, addr = server.accept()
                
                # spin off a thread to handle our new client
                client_thread = threading.Thread(target=self.client_handler, args=(client_socket,))
                client_thread.start()
                print "process id: %d" % os.getpid()
        except:
            print "Exception - server_loop:", sys.exc_info()[0]


def main():
    usage = "usage: %prog -t target_host -p port"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--target", dest="target",
                      help="the TARGET to connect to", metavar="TARGET")
    parser.add_option("-p", "--port", dest="port",
                      help="the PORT to connect to", metavar="PORT")
    parser.add_option("-l", "--listen", dest="listen",  action="store_true",
                      help="listen on [host]:[port] for incoming connections")
    parser.add_option("-e", "--execute", dest="file",
                      help="the FILE to execute upon receiving a connection", metavar="FILE")
    parser.add_option("-c", "--command", dest="command",  action="store_true",
                      help="initiate a command shell")
    parser.add_option("-u", "--upload", dest="destination",
                      help="upon receiving a connection upload file and write to DESTINATION", metavar="DESTINATION")
    (options,  args) = parser.parse_args()
    
    nc = netcatcmd(
        target  = options.target,
        port    = options.port,
        listen  = options.listen,
        execute = options.file,
        command = options.command,
        upload  = options.destination
        )
    
    if not nc.listen and len(nc.target) and nc.port > 0:
        # read in the buffer from the commandline
        # this will block, so send CTRL-D if not sending input
        # to stdin
        buff = sys.stdin.read()
        
        # send data off
        print buff
        nc.client_sender(buff)
        
    # we are going to listen and potentially
    # upload things, execute commands, and drop a shell back
    # depending on our command line options above
    if options.listen:
        nc.server_loop()
        
if __name__ == "__main__":
    main()
