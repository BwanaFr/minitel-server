"""
Created on 09 Jan 2020

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext, \
    Page
import logging
from minitel_server.terminal import Terminal
from minitel_server.exceptions import UserTerminateSessionError, MinitelTimeoutError
import datetime

logger = logging.getLogger('Clockpage')


class HandlerClock(DefaultPageHandler):
    """
    classdocs
    """

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)
        logger.info('in our custom handler')

    def after_rendering(self):
        logger.debug('In after_rendering callback')
        while True:
            try:
                # print time
                today = datetime.datetime.now()
                self.minitel.move_cursor(12, 9)
                self.minitel.double_size()
                self.minitel.print_text(today.strftime('%H:%M:%S'))
                self.minitel.normal_size()

                # Waits for a key press (the form is empty)
                key = self.minitel.wait_form_inputs(1)
                if key == Terminal.RETOUR:
                    next_page = Page.get_page(self.context.current_page.service, None)
                    return PageContext(self.context, self.minitel.forms, next_page)
                if key == Terminal.CONNEXION_FIN:
                    logger.debug("Connection/fin from {}".format(self.context.current_page.fullname))
                    raise UserTerminateSessionError
            except MinitelTimeoutError:
                pass
        return None
