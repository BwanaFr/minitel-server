'''
Created on 18 Oct 2019

@author: mdonze
'''

import logging
import os
import yaml
import re
from . import constant

logger = logging.getLogger('page')


class MinitelPage(object):
    '''
    Represents a minitel page template
    '''
    pages = {}
    
    @staticmethod
    def get_page(name):
        "Get a page from the collection"
        if len(MinitelPage.pages) == 0:
            logging.info('Getting list of pages')
            # Gets all pages from folders
            for dirName in next(os.walk(constant.PAGES_LOCATION))[1]:
                logging.info('Found page {folderName}'.format(folderName=dirName))
                MinitelPage.pages[dirName] = MinitelPage(dirName)
        return MinitelPage(name) #MinitelPage.pages[name];


    def __init__(self, name):
        '''
        Constructor
        '''
        self.name = name
        self.forms = None
        self.handler = None
        #Load page configuration from its yaml
        pageFile = os.path.join(constant.PAGES_LOCATION, name, name + '.yaml');
        with open(pageFile) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            if data is None:
                return
            #get list of forms
            
            self.forms = data.get('forms', None)
            self.handler = data.get('handler', None)
    
    def get_page_data(self):
        """ Get page VTX data """
        return os.path.join(constant.PAGES_LOCATION, self.name, self.name + '.vdt');
    
    def get_handler(self):
        """" Gets custom handler """
        return self.handler
        
    def get_module_name(self):
        """ Gets module name for resolving custom handler """
        if self.handler is None:
            return None
        else:
            return constant.PAGES_LOCATION + '.' + self.name

class MinitelPageContext(object):
    '''
    Navigation context
    '''
    
    def __init__(self, previous, data, current_page):
        "Previous page before this one"
        self.previous = previous
        self.data = data
        self.current_page = current_page


 
class MinitelDefaultHandler(object):
    '''
    Default page handler
    '''
    
    def __init__(self, minitel, context):
        self.minitel = minitel
        self.context = context
        self.forms = None
        
    async def before_rendering(self):
        pass
    
    async def render(self):
        page = self.context.current_page
        self.forms = page.forms
        self.minitel.resetzones()
        #add all zones in the document (if any)
        if self.forms is not None:
            for value in self.forms:
                row = value['location'][0]
                col = value['location'][1]
                lenght = value.get('lenght', 10)
                color = value.get('color', self.minitel.blanc)
                text = str(value.get('text', ''))
                self.minitel.zone(row, col, lenght, text, color)
        #Send the page content
        self.minitel.drawscreen(page.get_page_data())
                
    async def after_rendering(self):
        newcontext = None
        if self.forms is not None:
            #Wait for zones
            zones = await self.minitel.waitzones(0)
            logger.info('Got zone: {zone},{key}'.format(zone=zones[0], key=zones[1]))
            i = 0
            data = []
            nextpage = None
            for value in self.forms:
                #Save forms values in a array
                zonetext = self.minitel.zones[i]['texte']
                data.append({"text": zonetext})
                #test if zone match
                #Check if forms matches regular expression
                if 'actions' in value:
                    for action in value['actions']:
                        if 'value' in action:
                            valuepattern = str(action['value'])
                            if re.match(valuepattern, zonetext):
                                #value match. what to do now?
                                if 'page' in action:
                                    nextpage = MinitelPage.get_page(str(action['page']))
                                    break                
                i = i + 1
                if nextpage is not None:
                    newcontext = MinitelPageContext(self.context, data, nextpage)
                    break
        else:
            userinput = await self.minitel.waituserinput()
            logger.info('Got: {minitel},{code}'.format(minitel=userinput[0], code=userinput[1]))
            if userinput[0] and userinput[1] == self.minitel.retour:
                newcontext = self.context.previous
        return newcontext