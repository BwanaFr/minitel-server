"""
Created on 04 Oct 2022

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext, Page
import logging
from minitel_server.terminal import Terminal, FormInput
from minitel_server.exceptions import UserTerminateSessionError, MinitelTimeoutError, DisconnectedError
import sqlite3

logger = logging.getLogger('LivreOrAdd')


class LivreOrAdd(DefaultPageHandler):
    """
    JCC livre d'or page
    """

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)
        self.conn = None
        logger.debug(context.data)

    def after_rendering(self):
        self.minitel.clear_form_inputs()
        self.minitel.add_form_input(FormInput(11, 9, 20, 'Anonyme', Terminal.WHITE, True))
        self.minitel.add_form_input(FormInput(15, 10, 466, '', Terminal.WHITE, False))
        key = self.minitel.wait_form_inputs()
        if key == Terminal.ENVOI:
            if len(self.minitel.forms[1].text) == 0:
                next_page = Page.get_page(self.context.current_page.service, "jcc.menu")
                return PageContext(self, next_page)
            conn = sqlite3.connect('jcc.db')
            c = conn.cursor()
            #create table
            c.execute('''CREATE TABLE IF NOT EXISTS livre_or
                        (pseudo text, message text, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            req = f'INSERT INTO livre_or(pseudo, message) VALUES(?,?)'            
            c.execute(req, (self.minitel.forms[0].text, self.minitel.forms[1].text))
            #commit the changes to db			
            conn.commit()
            #close the connection
            conn.close()
            next_page = Page.get_page(self.context.current_page.service, "jcc.merci")
            return PageContext(self, next_page)
        elif key == Terminal.RETOUR:
            next_page = Page.get_page(self.context.current_page.service, "jcc.menu")
            return PageContext(self, next_page)
        elif key == Terminal.CONNEXION_FIN:
            logger.debug("Connection/fin from {}".format(self.context.current_page.fullname))                
            raise UserTerminateSessionError
