"""
Created on 04 Oct 2022

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext, Page
import logging
from minitel_server.terminal import Terminal, FormInput
from minitel_server.exceptions import UserTerminateSessionError, MinitelTimeoutError, DisconnectedError
import sqlite3
import time

logger = logging.getLogger('LivreOrConsult')


class LivreOrConsult(DefaultPageHandler):
    """
    JCC livre d'or page
    """

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)
        logger.debug(context.data)

    def after_rendering(self):
        current_page = 0
        conn = sqlite3.connect('jcc.db')
        c = conn.cursor()
        #create table
        c.execute('''CREATE TABLE IF NOT EXISTS livre_or
                    (pseudo text, message text, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        # Gets records
        c.execute('''SELECT * FROM livre_or ORDER BY created_at DESC;''')
        records = c.fetchall()
        conn.close()
        if len(records) == 0:
            self.minitel.move_cursor(7, 15)
            self.minitel.double_size()
            self.minitel.blink_cursor()
            self.minitel.visible_cursor(False)
            self.minitel.print_text('AUCUN MESSAGE')
            self.minitel.bell()
            self.minitel.blink_cursor(False)
            self.minitel.move_cursor(2, 19)
            self.minitel.print_text('Appuyer sur une touche pour continuer')
            self.minitel.wait_input()
            next_page = Page.get_page(self.context.current_page.service, "jcc.menu")
            return PageContext(self, next_page)
        self.minitel.move_cursor(1, 8)
        self.minitel.print_text('Message de ')
        while True:
            pseudo, message, _ = records[current_page]
            self.minitel.move_cursor(12, 8)
            self.minitel.clear_eol()
            self.minitel.double_width_size()
            self.minitel.print_text(pseudo)
            self.minitel.normal_size()            
            for i in range(11, 24):
                self.minitel.move_cursor(1, i)
                self.minitel.clear_eol()
            self.minitel.move_cursor(1, 10)
            self.minitel.clear_eol()
            self.minitel.print_text(message)
            self.minitel.move_cursor(1, 23)
            self.minitel.visible_cursor(False)
            self.minitel.print_text('Menu : ')
            self.minitel.reverse_video()
            self.minitel.print_text('SOMMAIRE')
            self.minitel.normal_video()
            self.minitel.move_cursor(1, 24)
            self.minitel.visible_cursor(False)
            self.minitel.clear_eol()
            suite_enabled = False
            retour_enabled = False
            if (current_page + 1) < len(records):
                suite_enabled = True
                self.minitel.print_text('Suivant : ')
                self.minitel.reverse_video()
                self.minitel.print_text('SUITE')
                self.minitel.normal_video()
            if current_page > 0:
                retour_enabled = True
                if suite_enabled:
                    self.minitel.print_text(' ')
                self.minitel.print_text('Precedent : ')
                self.minitel.reverse_video()
                self.minitel.print_text('RETOUR')
                self.minitel.normal_video()

            while True:
                sep, key = self.minitel.wait_input()
                if sep:
                    if key == Terminal.SOMMAIRE:
                        next_page = Page.get_page(self.context.current_page.service, "jcc.menu")
                        return PageContext(self, next_page)
                    elif (key == Terminal.SUITE) and suite_enabled:
                        current_page += 1
                        break
                    elif (key == Terminal.RETOUR) and retour_enabled:
                        current_page -= 1
                        break
                    elif key == Terminal.CONNEXION_FIN:
                        logger.debug("Connection/fin from {}".format(self.context.current_page.fullname))                
                        raise UserTerminateSessionError
                    else:
                        self.minitel.bell()
                else:
                    self.minitel.bell()