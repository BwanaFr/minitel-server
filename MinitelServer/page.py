'''
Created on 18 Oct 2019

@author: mdonze
'''

import logging
import os
import yaml
import re
from . import constant
from MinitelServer.pynitel import Pynitel

logger = logging.getLogger('page')


class MinitelPage(object):
    '''
    Represents a minitel page template
    '''
       
    @staticmethod
    def get_page(service, name):
        return MinitelPage(service, name) #MinitelPage.pages[name];


    def __init__(self, service, name):
        '''
        Constructor
        '''
        self.service = service
        self.forms = None
        self.handler = None
        if name is None:
            self.name = str(service)
            self.fullname = ''
            self.pagefolder = os.path.join(constant.PAGES_LOCATION, str(self.service))
        else:
            tokens = name.split('.')
            self.fullname = name
            self.name = tokens[len(tokens)-1]            
            self.pagefolder = os.path.join(constant.PAGES_LOCATION, str(self.service))
            for x in range(len(tokens)):
                self.pagefolder = os.path.join(self.pagefolder, tokens[x])
            
        #Load page configuration from its yaml
        pageFile = os.path.join(self.pagefolder, self.name + '.yaml')
        try:
            with open(pageFile) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if data is None:
                    return
                #get list of forms            
                self.forms = data.get('forms', None)
                self.handler = data.get('handler', None)
        except FileNotFoundError:
            pass
        
    def get_page_data(self):
        """ Get page VTX data file """
        filepath = os.path.join(self.pagefolder, self.name + '.vdt')
        if os.path.exists(filepath):
            return filepath
        
        filepath = os.path.join(self.pagefolder, self.name + '.vtx')
        if os.path.exists(filepath):
            return filepath
        
        return None
    
    def get_handler(self):
        """" Gets custom handler """
        return self.handler
        
    def get_module_name(self):
        """ Gets module name for resolving custom handler """
        if self.handler is None:
            return None
        else:
            if len(self.fullname) == 0:
                return constant.PAGES_LOCATION + '.' + str(self.service) + '.' + self.name
            else:
                return constant.PAGES_LOCATION + '.' + str(self.service) + '.' + self.fullname + '.' + self.name

class MinitelPageContext(object):
    '''
    Navigation context
    '''
    
    def __init__(self, previous, data, current_page):
        "Previous page before this one"
        self.previous = previous
        self.data = data
        self.current_page = current_page

class MinitelPageHandler(object):
    '''
    Abstract page handler for custom handlers
    '''
    
    def __init__(self, minitel, context):
        self.minitel = minitel
        self.context = context
    
    async def before_rendering(self):
        '''
        Called before rendering the page
        Useful for setting forms
        '''
        pass

    async def render(self):
        '''
        Send the page content to the Minitel
        '''
        pass
    
    async def after_rendering(self):
        '''
        Called after render() to handle keyboard inputs (or redirects)
        '''
        return None

class MinitelDefaultHandler(MinitelPageHandler):
    '''
    Default page handler for simple pages described in YAML
    '''
    
    def __init__(self, minitel, context):
        super().__init__(minitel, context)
        self.page = self.context.current_page
        self.forms = self.page.forms
        
    async def before_rendering(self):
        self.minitel.resetzones()
        #add all zones in the document (if any)
        if self.forms is not None:
            for value in self.forms:
                row = value['location'][0]
                col = value['location'][1]
                lenght = value.get('lenght', 0)
                color = value.get('color', Pynitel.BLANC)
                text = str(value.get('text', ''))
                self.minitel.zone(row, col, lenght, text, color)
    
    async def render(self):
        #Send the page content
        self.minitel.drawscreen(self.page.get_page_data())
                
    async def after_rendering(self):
        newcontext = None
        if self.forms is not None:
            #Wait for zones
            zones = await self.minitel.waitzones(0)
            logger.debug('Got zone: {zone},{key}'.format(zone=zones[0], key=zones[1]))
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
                            if re.match(valuepattern, zonetext, re.RegexFlag.IGNORECASE):
                                #value match. what to do now?
                                if 'page' in action:
                                    nextpage = MinitelPage.get_page(self.context.current_page.service, str(action['page']))
                                    break                
                i = i + 1
                if nextpage is not None:
                    newcontext = MinitelPageContext(self.context, data, nextpage)
                    break
        else:
            userinput = await self.minitel.waituserinput()
            logger.debug('Got: {minitel},{code}'.format(minitel=userinput[0], code=userinput[1]))
            if userinput[0] and userinput[1] == Pynitel.RETOUR:
                newcontext = self.context.previous
        return newcontext