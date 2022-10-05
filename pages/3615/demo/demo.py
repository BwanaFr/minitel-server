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
import glob
import os

logger = logging.getLogger('Demopage')


class HandlerDemo(DefaultPageHandler):
    """
    classdocs
    """

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)

    def after_rendering(self):
        vdt_folder = os.path.join(self.context.current_page.page_folder, 'vdts', '*.vdt')
        vdt_files = glob.glob(vdt_folder)
        logger.info(f'Found {len(vdt_files)} files')
        while True:
            for vdt_file in vdt_files:
                try:
                    # clear screen
                    logger.info(f'VDT file is {str(vdt_file)}')
                    self.minitel.clear_screen()
                    self.minitel.draw_file(vdt_file)
                    # Waits for a key press (the form is empty)
                    sep, key = self.minitel.wait_input(2)
                    if sep is True:
                        if key == Terminal.RETOUR:
                            next_page = Page.get_page(self.context.current_page.service, None)
                            return PageContext(self, next_page)
                        if key == Terminal.CONNEXION_FIN:
                            logger.debug("Connection/fin from {}".format(self.context.current_page.fullname))
                            raise UserTerminateSessionError
                except MinitelTimeoutError:
                    pass        
