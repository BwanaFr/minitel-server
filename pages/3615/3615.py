'''
Created on 5 Nov 2019

@author: mdonze
'''

import logging
import os

from MinitelServer.page import MinitelPageHandler
from MinitelServer.page import MinitelPage
from MinitelServer.page import MinitelPageContext
from MinitelServer.pynitel import Pynitel
import time

logger = logging.getLogger('3615page')

class Handler3615(MinitelPageHandler):
    '''
    Handler for 3615 connection
    '''
    
    def __init__(self, minitel, context):
        super().__init__(minitel, context)
    
    async def before_rendering(self):
        self.minitel.resetzones()
        self.minitel.zone(17, 12, 29, '', Pynitel.JAUNE)
    
    async def render(self):
        page = self.context.current_page
        #Send the page content
        self.minitel.drawscreen(page.get_page_data())
    
    async def after_rendering(self):
        zones = await self.minitel.waitzones(0)
        key = zones[1]
        logger.debug('Got zone: {zone},{key}'.format(zone=zones[0], key=key))
        if key == Pynitel.ENVOI:
            logger.debug("Envoi from {}".format(self.context.current_page.pagefolder))
            nextpage = self.getpage(self.minitel.zones[0]['texte'])
            if nextpage is not None:
                return MinitelPageContext(self.context, self.minitel.zones, nextpage)
            else:
                self.shownotfound()
        if key == Pynitel.GUIDE:
            logger.debug("Guide from {}".format(self.context.current_page.pagefolder))
            return await self.showavailableservice()
        if key == Pynitel.SOMMAIRE:
            return await self.showprice()
        if key == Pynitel.CONNEXIONFIN:
            self.minitel.end()
        return None
    
    def getpage(self, name):
        ''' Gets a new page if found in child folder '''
        name = name.lower()
        nextpage = None
        for dirName in next(os.walk(self.context.current_page.pagefolder))[1]:
            if dirName.lower() == name:
                logger.debug("Found page {}".format(name))
                nextpage = MinitelPage.get_page(self.context.current_page.service, name)
        return nextpage

    def shownotfound(self):
        ''' Show a not found message '''
        self.minitel.message(0, 1, 2, 'Service non trouvé', True)
    
    async def showavailableservice(self):
        ''' Show list of available pages '''
        self.minitel.cls()
        self.minitel.pos(2, 1)
        self.minitel.doublehauteur()
        self.minitel._print("Services disponibles")
        self.minitel.simpletaille()
        self.minitel.pos(3, 1)
        self.minitel.forecolor(Pynitel.BLEU)
        self.minitel.plot('`', 40)
        self.minitel.pos(23, 1)
        self.minitel.forecolor(Pynitel.BLEU)
        self.minitel.plot('`', 40)
        self.minitel.pos(24, 1)
        self.minitel.forecolor(Pynitel.BLANC)
        self.minitel._print("          Numéro du service: ..  + ")
        self.minitel.inverse(1)
        self.minitel._print("ENVOI")
        self.minitel.inverse(0)        
        i = 0
        x = 1
        pagesnum = []
        for dirName in next(os.walk(self.context.current_page.pagefolder))[1]:
            if not dirName.startswith('_'):
                self.minitel.pos(4+i, x)
                pagesnum.append(dirName)
                self.minitel._print("{:02d} {}".format(len(pagesnum), 
                                                       dirName[0:16]))
                i = i + 1
                if i > 18:
                    x = 21
                    i = 0
        ''' Make zone '''
        self.minitel.resetzones()
        self.minitel.zone(24, 30, 2, '', Pynitel.BLANC)
        while True:
            zones = await self.minitel.waitzones(0)
            key = zones[1]
            logger.debug('Got zone: {zone},{key}'.format(zone=zones[0], key=key))
            if key == Pynitel.ENVOI:
                try:
                    pageindex = int(self.minitel.zones[0]['texte'])
                    logger.debug('Selected page {:d}/{}'.format(pageindex,pagesnum[pageindex-1]))
                    nextpage = MinitelPage.get_page(self.context.current_page.service, pagesnum[pageindex-1])
                    return MinitelPageContext(self.context, self.minitel.zones, nextpage)
                except:
                    self.minitel.message(0, 1, 2, 'Mauvais numéro', True)
            if key == Pynitel.ANNULATION:
                break
            if key == Pynitel.SOMMAIRE:
                break
            if key == Pynitel.GUIDE:
                break
        return None
    
    async def showprice(self):
        self.minitel.cls()
        self.minitel.pos(2, 1)
        self.minitel.doublehauteur()
        self.minitel._print("Prix des services")
        self.minitel.simpletaille()
        self.minitel.pos(3, 1)
        self.minitel.forecolor(Pynitel.BLEU)
        self.minitel.plot('`', 40)
        self.minitel.pos(5, 1)
        self.minitel.doublehauteur()
        self.minitel._print("A l'époque ces services")
        self.minitel.pos(7, 1)
        self.minitel.doublehauteur()
        self.minitel._print("Minitels coutaient tellement cher!")
        time.sleep(2.0)
        self.minitel.pos(10, 1)
        self.minitel.doublehauteur()
        self.minitel._print("Cela a fait la fortune de certains...")
        time.sleep(2.0)
        return None