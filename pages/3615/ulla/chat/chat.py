"""
Created on 26 Dec 2019

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext, \
    Page
import logging
from minitel_server.terminal import Terminal
from minitel_server.exceptions import UserTerminateSessionError
import threading

logger = logging.getLogger('Ullapage')


class HandlerUllaChat(DefaultPageHandler):
    """
    A basic chat for Ulla
    """
    num = 0
    lock = threading.RLock()

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)
        logger.info('HandlerUllaChat: in our custom handler')

    def before_rendering(self):
        logger.debug('HandlerUllaChat: In before_rendering callback')
        super().before_rendering()
        HandlerUllaChat.lock.acquire()
        HandlerUllaChat.num += 1
        HandlerUllaChat.lock.release()

    def render(self):
        super().render()
        self.minitel.move_cursor(1, 3)
        self.minitel.print_text("{} utilisateurs en ligne".format(HandlerUllaChat.num))

    def after_rendering(self):
        logger.debug('HandlerUllaChat: In after_rendering callback')
        key = self.minitel.wait_form_inputs()
        if key == Terminal.ENVOI:
            logger.debug("Envoi from {}".format(self.context.current_page.fullname))
            logger.debug('Username is {}'.format(self.minitel.forms[0].text))
            nextpage = Page.get_page(self.context.current_page.service, "ulla.home")
            return PageContext(self.context, self.minitel.forms, nextpage)
        if key == Terminal.GUIDE:
            logger.debug("Guide from {}".format(self.context.current_page.fullname))
        if key == Terminal.SOMMAIRE:
            logger.debug("Sommaire from {}".format(self.context.current_page.fullname))
        if key == Terminal.CONNEXION_FIN:
            logger.debug("Connection/fin from {}".format(self.context.current_page.fullname))
            raise UserTerminateSessionError
        return None
