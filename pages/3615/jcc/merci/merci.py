"""
Created on 04 Oct 2022

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext, Page
import logging
import time

logger = logging.getLogger('Merci')


class Merci(DefaultPageHandler):
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
        time.sleep(1)
        next_page = Page.get_page(self.context.current_page.service, "jcc.menu")
        return PageContext(self, next_page)
