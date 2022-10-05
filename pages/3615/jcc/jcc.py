"""
Created on 04 Oct 2022

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext, Page
import logging
import time

logger = logging.getLogger('Jcc')


class Jcc(DefaultPageHandler):
    """
    JCC  page
    """

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)

    def after_rendering(self):        
        next_page = Page.get_page(self.context.current_page.service, "jcc.menu")
        time.sleep(1)
        return PageContext(self, next_page)
