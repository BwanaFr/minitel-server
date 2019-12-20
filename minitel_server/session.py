'''
Created on 18 Dec 2019

@author: mdonze
'''

import logging
from threading import Thread
from minitel_server.terminal import Terminal, FormInput
from minitel_server.exceptions import DisconnectedError,\
    UserTerminateSessionError
from minitel_server.page import Page, PageContext, DefaultPageHandler

logger = logging.getLogger('Session')


class Session(Thread):
    '''
    A Session of Minitel
    '''

    def __init__(self, ip, port, conn):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self.ip = ip 
        self.port = port 
        self.conn = conn
        self.terminal = Terminal(conn)
        self.context = None
        logger.info("Starting a new Minitel Session " 
                        "for IP {ip} on service {port}".
                        format(ip=self.ip, port=self.port))

    def run(self):
        try:
            logger.debug("Minitel session started")
            ''' Waits for first -garbage- characters '''
            self.terminal.wait_connection()
            self.terminal.clear_screen()
            self.terminal.home_cursor()
            ''' Loads the root page and create the default context '''
            page = Page.get_page(self.port, None)
            self.context = PageContext(None, None, page)
            while True:
                ''' Get custom page handler '''
                handler_name = self.context.current_page.get_handler()
                if handler_name is None:
                    logger.debug("Using default handler")
                    handler = DefaultPageHandler(self.terminal, self.context)
                else:
                    ''' Import the module handler '''
                    modulename = self.context.current_page.get_module_name()
                    module = Session.full_import(modulename)
                    class_ = getattr(module, handler_name)
                    handler = class_(self.terminal, self.context)
                ''' Call before rendering handler '''
                handler.before_rendering()
                ''' Render page '''
                handler.render()
                ''' Get new context from the rendered page '''
                new_context = handler.after_rendering()
                if new_context is not None:
                    self.context = new_context
                    
                    
        except DisconnectedError:
            logger.info("IP {} disconnected".format(self.ip))
        except UserTerminateSessionError:
            logger.info("User {} disconnection request".format(self.ip))
            self.conn.close()
            
    @staticmethod
    def full_import(name):
        ''' Import a module by using the full qualifier '''
        m = __import__(name)
        for n in name.split(".")[1:]:
            m = getattr(m, n)
        return m