'''
Created on 18 Oct 2019

@author: mdonze
'''
import asyncio
import logging
import importlib

from asyncio import IncompleteReadError
from builtins import object
from MinitelServer.pynitel import Pynitel
from MinitelServer.page import MinitelPage
from MinitelServer.page import MinitelDefaultHandler
from MinitelServer.page import MinitelPageContext
from MinitelServer.exceptions import MinitelDisconnected

logger = logging.getLogger('server')

def even_parity(character):
    """ Adds the parity bit to a character """
    character_int = character

    # Add the parity bit
    if bin(character_int).count('1') % 2:
        character_int += 128

    return character_int

def remove_parity(data):
    """ Removes the parity bit to a character """
    MASK = 0b01111111
    character = chr(data & MASK).encode()
    return character[0]

class MinitelServer(object):
    '''
    TCP server for serving TCP connections
    '''


    def __init__(self, port):
        '''
        Constructor
        '''
        self.port = port
            
    def run(self):
        """ Run the Minitel server """
        loop = asyncio.get_event_loop()
        handler = MinitelConnection
        coro = asyncio.start_server(
                handler.handle_connection, port=self.port, loop=loop)
        server = loop.run_until_complete(coro)
        # Serve requests until Ctrl+C is pressed
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        
        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

        
class MinitelConnection(object):
    '''
        Connection to a TCP socket
    '''
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        peer = writer.get_extra_info('peername')
        logger.info('Received connection from {peer[0]}:{peer[1]}'.format(
            peer=peer))

    @classmethod
    async def handle_connection(cls, reader, writer):
        """ Generate a client connection handler """
        await cls(reader, writer).run()
        
    async def run(self):
        """ Runs the connection """
        app = MinitelSession(self)
        await app.run();
        peer = self.writer.get_extra_info('peername')
        logger.info('Disconnected from {peer[0]}:{peer[1]}'.format(
            peer=peer))
    
    async def read(self, size=1):
        """ Read a character from connection """
        while True:
            try:
                data = await self.reader.readexactly(size)
                break
            except IncompleteReadError:
                raise MinitelDisconnected
        # TODO: Check parity of the received data
        converted_value = bytes([
            remove_parity(character) for character in data
        ])
        return converted_value
    
    async def readAll(self):
        """ Read a character from connection """
        data = await self.reader.read()
        if not data:
            raise MinitelDisconnected
        # TODO: Check parity of the received data
        converted_value = bytes([
            remove_parity(character) for character in data
        ])
        return converted_value
    
    def readUntil(self, char):
        try:
            self.reader.readuntil(char)
        except IncompleteReadError:
            raise MinitelDisconnected
        
    def write(self, value):
        converted_value = bytes([
            even_parity(character) for character in value
        ])
        self.writer.write(converted_value)
        self.writer.drain()
        
class MinitelSession(object):
    """ A user session for handling pages flow """
    
    ROOT_PAGE = 'root'
    
    def __init__(self, conn):
        self.conn = conn
        self.context = None
        
    async def run(self):
        self.m = Pynitel(self.conn)
        try:
            """ Waits for the connection """
            self.m.wait()
            self.m.home()
            """ Loads the root page """
            page = MinitelPage.get_page(self.ROOT_PAGE)
            self.context = MinitelPageContext(None, None, page)
            while True:
                handler_name = self.context.current_page.get_handler()
                """ handler is a string representation of class """
                if handler_name is None:
                    handler = MinitelDefaultHandler(self.m, self.context)
                else:
                    """ Import module dynamically """
                    module = importlib.import_module(
                                    self.context.current_page.get_module_name())
                    class_ = getattr(module, handler)
                    handler = class_(self.m, self.context)
                    
                await handler.before_rendering()
                await handler.render()
                newcontext = await handler.after_rendering()
                if newcontext is not None:
                    self.context = newcontext
        except MinitelDisconnected:
            pass