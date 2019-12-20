'''
Created on 5 Nov 2019

@author: mdonze
'''

import logging
import os

from minitel_server.page import PageHandler
from minitel_server.page import Page
from minitel_server.page import PageContext
from minitel_server.terminal import Terminal, FormInput
import time
from minitel_server.exceptions import UserTerminateSessionError

logger = logging.getLogger('3615page')

class Handler3615(PageHandler):
    '''
    Handler for 3615 connection
    '''
    
    def __init__(self, minitel, context):
        super().__init__(minitel, context)
    
    def before_rendering(self):
        self.minitel.clear_form_inputs()
        form_input = FormInput(12, 17, 29, '', Terminal.YELLOW)
        self.minitel.add_form_input(form_input)
            
    def render(self):
        page = self.context.current_page
        #Send the page content
        self.minitel.draw_file(page.get_page_data())
    
    def after_rendering(self):
        key = self.minitel.wait_form_inputs()
        
        if key == Terminal.ENVOI:
            logger.debug("Envoi from {}".format(self.context.current_page.pagefolder))
            nextpage = self.getpage(self.minitel.forms[0].text)
            if nextpage is not None:
                return PageContext(self.context, self.minitel.forms, nextpage)
            else:
                self.shownotfound()
        if key == Terminal.GUIDE:
            logger.debug("Guide from {}".format(self.context.current_page.pagefolder))
            return self.showavailableservice()
        if key == Terminal.SOMMAIRE:
            return self.showprice()
        if key == Terminal.CONNEXION_FIN:
            raise UserTerminateSessionError
        return None
    
    def getpage(self, name):
        ''' Gets a new page if found in child folder '''
        name = name.lower()
        nextpage = None
        for dirName in next(os.walk(self.context.current_page.pagefolder))[1]:
            if dirName.lower() == name:
                logger.debug("Found page {}".format(name))
                nextpage = Page.get_page(self.context.current_page.service, name)
        return nextpage

    def shownotfound(self):
        ''' Show a not found message '''
        self.minitel.message(0, 1, 2, 'Service non trouvé', True)
    
    def showavailableservice(self):
        ''' Show list of available pages '''
        self.minitel.clear_screen()
        self.minitel.move_cursor(1, 2)
        self.minitel.double_height_size()
        self.minitel.print_text("Services disponibles")
        self.minitel.normal_size()
        self.minitel.move_cursor(1, 3)
        self.minitel.text_colour(Terminal.BLUE)
        self.minitel.print_repeat('`', 40)
        self.minitel.move_cursor(1, 23)
        self.minitel.text_colour(Terminal.BLUE)
        self.minitel.print_repeat('`', 40)
        self.minitel.move_cursor(1, 24)
        self.minitel.text_colour(Terminal.WHITE)
        self.minitel.print_text("          Numéro du service: ..  + ")
        self.minitel.reverse_video()
        self.minitel.print_text("ENVOI")
        self.minitel.normal_video()      
        i = 0
        x = 1
        pagesnum = []
        for dirName in next(os.walk(self.context.current_page.pagefolder))[1]:
            if not dirName.startswith('_'):
                self.minitel.move_cursor(x, 4+i)
                pagesnum.append(dirName)
                self.minitel.print_text("{:02d} {}".format(len(pagesnum), 
                                                       dirName[0:16]))
                i = i + 1
                if i > 18:
                    x = 21
                    i = 0
        ''' Make zone '''
        self.minitel.clear_form_inputs()
        self.minitel.add_form_input(FormInput(30, 24, 2, '', True))
        while True:
            key = self.minitel.wait_form_inputs()
            if key == Terminal.ENVOI:
                try:
                    pageindex = int(self.minitel.forms[0].text)
                    logger.debug('Selected page {:d}/{}'.format(pageindex,pagesnum[pageindex-1]))
                    nextpage = Page.get_page(self.context.current_page.service, pagesnum[pageindex-1])
                    return PageContext(self.context, self.minitel.forms, nextpage)
                except:
                    self.minitel.show_message('Mauvais numéro', 10)
            if key == Terminal.ANNULATION:
                break
            if key == Terminal.SOMMAIRE:
                break
            if key == Terminal.GUIDE:
                break
        return None
    
    def showprice(self):
        self.minitel.clear_screen()
        self.minitel.move_cursor(1, 2)
        self.minitel.double_height_size()
        self.minitel.print_text("Prix des services")
        self.minitel.normal_size()
        self.minitel.move_cursor(1, 3)
        self.minitel.text_colour(Terminal.BLUE)
        self.minitel.print_repeat('`', 40)
        self.minitel.move_cursor(1, 5)
        self.minitel.double_height_size()
        self.minitel.print_text("A l'époque ces services")
        self.minitel.move_cursor(1, 7)
        self.minitel.double_height_size()
        self.minitel.print_text("Minitels coutaient tellement cher!")
        time.sleep(2.0)
        self.minitel.move_cursor(1, 10)
        self.minitel.double_height_size()
        self.minitel.print_text("Cela a fait la fortune de certains...")
        self.minitel.move_cursor(1, 12)
        self.minitel.normal_size()
        self.minitel.print_text("Coucou Xavier :-)")
        time.sleep(2.0)
        return None