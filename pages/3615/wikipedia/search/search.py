"""
Created on 15 Jan 2020

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext, \
    Page
import logging
from minitel_server.terminal import Terminal, FormInput
from minitel_server.exceptions import UserTerminateSessionError
import time

logger = logging.getLogger('Wikipedia')


class Search(DefaultPageHandler):
    """
    Search page
    """

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)
        logger.debug(context.data)

    def after_rendering(self):
        time.sleep(5)
        self.minitel.move_cursor(1, 11)
        self.minitel.clear_eol()
        self.minitel.move_cursor_down()
        self.minitel.clear_eol()
        self.minitel.move_cursor(1, 1)
        self.minitel.print_text("My multiple line\ntext\nline 3")
        self.minitel.move_cursor(1, 22)
        self.minitel.print_repeat('`', 40)
        self.minitel.move_cursor(1, 23)
        self.minitel.print_text("Selection")
        self.minitel.clear_form_inputs()
        self.minitel.add_form_input(FormInput(35, 24, 2, initial_draw=True))
        key = self.minitel.wait_form_inputs()
        if key == Terminal.RETOUR:
            logger.debug("Retour")
            return PageContext(self, self.context.previous)
        return None
