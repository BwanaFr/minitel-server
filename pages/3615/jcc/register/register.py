"""
Created on 04 Oct 2022

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext, Page
import logging
from minitel_server.terminal import Terminal, FormInput
from minitel_server.exceptions import UserTerminateSessionError, MinitelTimeoutError, DisconnectedError
import sqlite3
import re

logger = logging.getLogger('Register')


class Register(DefaultPageHandler):
    """
    JCC inscription page
    """

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)
        self.conn = None
        logger.debug(context.data)

    def after_rendering(self):
        current_form = 0
        while True:
            key = self.minitel.wait_form_inputs(current_form=current_form)
            if key == Terminal.ENVOI:
                err_msg = None
                if not re.match('[a-zA-Z\-À-ÿ]{2,}', self.minitel.forms[0].text, re.RegexFlag.IGNORECASE):
                    err_msg = 'Prénom invalide'
                    current_form = 0
                elif not re.match('[a-zA-Z\-À-ÿ]{2,}', self.minitel.forms[1].text, re.RegexFlag.IGNORECASE):
                    err_msg = 'Nom invalide'
                    current_form = 1
                elif not re.match('^((\w[^\W]+)[\.\-]?){1,}\@(([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$', self.minitel.forms[2].text, re.RegexFlag.IGNORECASE):
                    err_msg = 'E-mail invalide'
                    current_form = 2

                if err_msg is not None:
                    self.minitel.bell()
                    self.minitel.show_message(err_msg, 5, 13, 16, True)
                else:
                    conn = sqlite3.connect('jcc.db')
                    c = conn.cursor()
                    #create table
                    c.execute('''CREATE TABLE IF NOT EXISTS news_letter
                                (prenom text, nom text, mail text)''')
                    req = f'INSERT INTO news_letter VALUES(\'{self.minitel.forms[0].text}\', \'{self.minitel.forms[1].text}\', \'{self.minitel.forms[2].text}\')'
                    c.execute(req)
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

