"""
Created on 3 Dec 2020

@author: mdonze
"""
import logging
import yaml
import sys
import os

from . import constant

logger = logging.getLogger('page')


class Configuration(object):
    PAGE_LOCATION = 'pages'
    page_folder = '.'

    @staticmethod
    def load_configuration():
        try:
            with open(constant.CFG_FILE) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if data is None:
                    return
                # Gets page location
                page_folder = data.get('pages_folder', None)
                if page_folder is not None:
                    Configuration.page_folder = page_folder
                    sys.path.append(page_folder)
        except FileNotFoundError:
            logger.warning("Configuration file not found.")

        Configuration.page_folder = os.path.join(Configuration.page_folder, Configuration.PAGE_LOCATION)
        logger.info("Pages stored in {} : ".format(Configuration.page_folder))
