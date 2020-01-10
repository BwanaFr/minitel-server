"""
Created on 18 Oct 2019

@author: mdonze
"""

import logging
import os
import yaml
import re
from . import constant
from minitel_server.terminal import Terminal, FormInput
from minitel_server.exceptions import UserTerminateSessionError

logger = logging.getLogger('page')


class Page(object):
    """
    Represents a minitel page template
    """

    @staticmethod
    def get_page(service, name):
        return Page(service, name)  # Page.pages[name];

    def __init__(self, service, name):
        """
        Constructor
        """
        self.service = service
        self.forms = None
        self.handler = None
        if name is None:
            self.name = str(service)
            self.fullname = ''
            self.page_folder = os.path.join(constant.PAGES_LOCATION, str(self.service))
        else:
            tokens = name.split('.')
            self.fullname = name
            self.name = tokens[len(tokens) - 1]
            self.page_folder = os.path.join(constant.PAGES_LOCATION, str(self.service))
            for x in range(len(tokens)):
                self.page_folder = os.path.join(self.page_folder, tokens[x])
        logger.debug("Minitel page folder is {}".format(self.page_folder))
        # Load page configuration from its yaml
        page_file = os.path.join(self.page_folder, self.name + '.yaml')
        try:
            with open(page_file) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if data is None:
                    return
                # get list of forms
                self.forms = data.get('forms', None)
                self.handler = data.get('handler', None)
        except FileNotFoundError:
            pass

    def get_page_data(self):
        """ Get page VTX data file """
        file_path = os.path.join(self.page_folder, self.name + '.vdt')
        if os.path.exists(file_path):
            return file_path

        file_path = os.path.join(self.page_folder, self.name + '.vtx')
        if os.path.exists(file_path):
            return file_path

        return None

    def get_handler(self):
        """" Gets custom handler """
        return self.handler

    def get_module_name(self):
        """ Gets module name for resolving custom handler """
        if self.handler is None:
            return None
        else:
            if len(self.fullname) == 0:
                return constant.PAGES_LOCATION + '.' + str(self.service) + '.' + self.name
            else:
                return constant.PAGES_LOCATION + '.' + str(self.service) + '.' + self.fullname + '.' + self.name


class PageContext(object):
    """
    Navigation context
    """

    def __init__(self, previous, data, current_page):
        """Previous page before this one"""
        self.previous = previous
        self.data = data
        self.current_page = current_page


class PageHandler(object):
    """
    Abstract page handler for custom handlers
    """

    def __init__(self, minitel, context):
        self.minitel = minitel
        self.context = context

    def before_rendering(self):
        """
        Called before rendering the page
        Useful for setting forms
        """
        pass

    def render(self):
        """
        Send the page content to the Minitel
        """
        pass

    def after_rendering(self):
        """
        Called after render() to handle keyboard inputs (or redirects)
        """
        return None


class DefaultPageHandler(PageHandler):
    """
    Default page handler for simple pages described in YAML
    """

    def __init__(self, minitel, context):
        super().__init__(minitel, context)
        self.page = self.context.current_page
        self.forms = self.page.forms

    def before_rendering(self):
        self.minitel.clear_form_inputs()
        # add all zones in the document (if any)
        if self.forms is not None:
            for value in self.forms:
                row = value['location'][0]
                col = value['location'][1]
                length = value.get('length', 0)
                colour = value.get('color', Terminal.WHITE)
                text = str(value.get('text', ''))
                form_input = FormInput(col, row, length, text, colour, True)
                self.minitel.add_form_input(form_input)

    def render(self):
        # Send the page content
        self.minitel.draw_file(self.page.get_page_data())

    def after_rendering(self):
        new_context = None
        if self.forms is not None:
            # Wait for zones
            key = self.minitel.wait_form_inputs()
            logger.debug('Got zone SEP key : {}'.format(key))
            i = 0
            data = {}
            next_page = None
            for value in self.forms:
                # Save forms values in a array
                zone_text = self.minitel.forms[i].text
                data["text_{}".format(i)] = zone_text
                # test if zone match
                # Check if forms matches regular expression
                if 'actions' in value:
                    for action in value['actions']:
                        if 'value' in action:
                            value_pattern = str(action['value'])
                            if re.match(value_pattern, zone_text, re.RegexFlag.IGNORECASE):
                                # value match. what to do now?
                                if 'page' in action:
                                    next_page = Page.get_page(self.context.current_page.service, str(action['page']))
                                    break
                i = i + 1
                if next_page is not None:
                    new_data = self.context.data
                    new_data[self.context.current_page.name] = data
                    new_context = PageContext(self.context, new_data, next_page)
                    break
        else:
            sep, key = self.minitel.wait_input()
            if sep and key == Terminal.RETOUR:
                new_context = self.context.previous
            elif sep and key == Terminal.CONNEXION_FIN:
                raise UserTerminateSessionError
        return new_context
