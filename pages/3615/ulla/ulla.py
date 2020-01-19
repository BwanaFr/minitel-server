"""
Created on 7 Nov 2019

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext, \
    Page
import logging
from minitel_server.terminal import Terminal
from minitel_server.exceptions import UserTerminateSessionError

logger = logging.getLogger('Ullapage')


class HandlerUlla(DefaultPageHandler):
    """
    classdocs
    """

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)

    def after_rendering(self):
        logger.debug('In after_rendering callback')
        key = self.minitel.wait_form_inputs()
        if key == Terminal.ENVOI:
            logger.debug("Envoi from {}".format(self.context.current_page.fullname))
            logger.debug('Username is {}'.format(self.minitel.forms[0].text))
            data = {"username": self.minitel.forms[0].text}
            next_page = Page.get_page(self.context.current_page.service, "ulla.home")
            return PageContext(self, next_page, data)
        if key == Terminal.GUIDE:
            logger.debug("Guide from {}".format(self.context.current_page.fullname))
        if key == Terminal.SOMMAIRE:
            logger.debug("Sommaire from {}".format(self.context.current_page.fullname))
        if key == Terminal.CONNEXION_FIN:
            logger.debug("Connection/fin from {}".format(self.context.current_page.fullname))
            raise UserTerminateSessionError
        return None
