'''
Created on 18 Dec 2019

@author: mdonze
'''
import logging
import socket
from threading import Thread
from minitel_server.session import Session

TCP_IP = '0.0.0.0'
logger = logging.getLogger('TCPServer')

class TCPServer(Thread):
    '''
    Listen for TCP connection on specified port
    '''

    def __init__(self, port):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self.port = port;
        
    
    def run(self):
        logger.info("Listening for connection on port {}".format(self.port))
        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        tcpServer.bind((TCP_IP, self.port)) 
        threads = []
        while True :
            tcpServer.listen()
            (conn, (ip,_port)) = tcpServer.accept()
            logger.info("Got connection from {}".format(ip))
            conn.setblocking(0)
            newthread = Session(ip, self.port, conn) 
            newthread.start() 
            threads.append(newthread) 
 
        for t in threads: 
            t.join() 
        