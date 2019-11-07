'''
Created on 7 Nov 2019

@author: mdonze
'''
from MinitelServer.page import MinitelDefaultHandler, MinitelPageContext,\
    MinitelPage
import logging
from MinitelServer.pynitel import Pynitel

logger = logging.getLogger('Ullapage')

class HandlerUlla(MinitelDefaultHandler):
    '''
    classdocs
    '''


    def __init__(self, minitel, context):
        '''
        Constructor
        '''
        super().__init__(minitel, context)
        logger.info('in our custom handler')
    
    async def after_rendering(self):
        logger.debug('In after_rendering callback')
        zones = await self.minitel.waitzones(0)
        key = zones[1]
        logger.debug('Got zone: {zone},{key}'.format(zone=zones[0], key=key))
        if key == Pynitel.ENVOI:
            logger.debug("Envoi from {}".format(self.context.current_page.fullname))
            nextpage = MinitelPage.get_page(self.context.current_page.service, "ulla.home")
            return MinitelPageContext(self.context, self.minitel.zones, nextpage)
        if key == Pynitel.GUIDE:
            logger.debug("Guide from {}".format(self.context.current_page.fullname))
        if key == Pynitel.SOMMAIRE:
            logger.debug("Sommaire from {}".format(self.context.current_page.fullname))
        if key == Pynitel.CONNEXIONFIN:
            logger.debug("Connection/fin from {}".format(self.context.current_page.fullname))
            self.minitel.end()
        return None