"""
Created on 15 Jan 2020

@author: mdonze
"""
from minitel_server.page import DefaultPageHandler, PageContext
import logging
from minitel_server.terminal import Terminal, FormInput

logger = logging.getLogger('Wikipedia')

wikipedia_available = True

# Try to import the wikipedia module
try:
    import wikipedia
except ImportError:
    wikipedia = None
    logger.warning("wikipedia module not installed.")
    wikipedia_available = False


class Search(DefaultPageHandler):
    """
    Search page
    """
    MAX_TEXT_LEN = 40
    NB_LINES = 20

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)
        logger.debug(context.data)
        # Gets the previous form from context
        self._search_term = context.data['wikipedia']['text_0']
        logger.info("Searching for {}".format(self._search_term))

    def after_rendering(self):
        # Display error if wikipedia module is not installed
        if not wikipedia_available:
            return self.show_no_wikipedia("Module Python introuvable")

        # Perform the search
        try:
            wikipedia.set_lang('fr')
            res = wikipedia.search(self._search_term, results=Search.NB_LINES)
            if len(res) == 0:
                return self.show_no_results()
            elif len(res) == 1:
                # Only one result.
                res_text = wikipedia.summary(res[0])
                return self.show_result(res_text)

            # Multiple results
            while True:
                selected = self.select_page(res)
                if selected is not None:
                    res_text = wikipedia.summary(res[selected])
                    self.show_result(res_text)
                else:
                    return PageContext(self, self.context.previous.current_page)
        except IOError:
            return self.show_no_wikipedia("Erreur connexion")

    def clear_progress(self):
        """
            Clear the search page
        """
        self.minitel.move_cursor(1, 11)
        self.minitel.clear_eol()
        self.minitel.move_cursor_down()
        self.minitel.clear_eol()

    def show_no_wikipedia(self, text):
        """
            Shows service unavailable
            :param text Error test to be displayed
        """
        self.clear_progress()
        self.minitel.move_cursor(11, 11)
        self.minitel.double_size()
        self.minitel.text_colour(self.minitel.RED)
        self.minitel.print_text("Wikipedia")
        self.minitel.move_cursor(8, 14)
        self.minitel.double_size()
        self.minitel.text_colour(self.minitel.RED)
        self.minitel.print_text("indisponible")
        self.minitel.move_cursor(1, 20)
        self.minitel.print_text(text)
        self.minitel.move_cursor_down()
        self.minitel.move_cursor_start_line()
        self.minitel.print_text("Appuyez sur retour")
        self.minitel.add_form_input(FormInput(35, 24, 1, initial_draw=False))
        while True:
            self.minitel.visible_cursor(False)
            key = self.minitel.wait_form_inputs()
            if key == Terminal.RETOUR:
                logger.debug("Retour")
                return PageContext(self, self.context.previous.current_page)

    def show_no_results(self):
        """
            Show the no result page
        """
        self.clear_progress()
        self.minitel.move_cursor(4, 11)
        self.minitel.double_size()
        self.minitel.text_colour(self.minitel.RED)
        self.minitel.print_text("Aucun résultat")
        self.minitel.move_cursor(1, 22)
        self.minitel.print_text("Appuyez sur retour")
        self.minitel.add_form_input(FormInput(35, 24, 1, initial_draw=False))
        while True:
            self.minitel.visible_cursor(False)
            key = self.minitel.wait_form_inputs()
            if key == Terminal.RETOUR:
                logger.debug("Retour")
                return PageContext(self, self.context.previous.current_page)

    def show_result(self, text):
        """
            Shows result
            :param text Wikipedia text
        """
        # Cut the text to be displayed
        # Do line wrap
        chunks = []
        start = 0
        logger.debug("Displaying {}".format(text))
        while True:
            if start >= len(text):
                break
            actual = text[start:(start + self.MAX_TEXT_LEN)]
            new_lines = actual.split('\n')
            if len(new_lines) > 1:
                # Got a \n in string
                for j in range(0, len(new_lines) - 1):
                    chunks.append(new_lines[j])
                    start = start + len(new_lines[j])
                start = start + 1
                continue

            if len(actual) == self.MAX_TEXT_LEN:
                # Takes all length, needs to end at a space
                last_space_pos = actual.rfind(' ')
                if last_space_pos > 0:
                    i = last_space_pos
                else:
                    i = len(actual)
                chunks.append(text[start:i + start])
                start = start + i + 1
            else:
                chunks.append(actual)
                start = start + len(actual)
        # Compute the number of pages to be shown
        nb_pages = len(chunks) // Search.NB_LINES
        if len(chunks) % Search.NB_LINES != 0:
            nb_pages = nb_pages + 1
        logger.debug("Page count : {}".format(nb_pages))
        page_number = 0
        self.minitel.clear_form_inputs()
        self.minitel.add_form_input(FormInput(35, 24, 3, initial_draw=True))
        self.minitel.move_cursor(1, 24)
        self.minitel.clear_eol()
        self.minitel.move_cursor(30, 24)
        self.minitel.print_text("Page ")
        self.minitel.move_cursor(38, 24)
        self.minitel.print_text("/{}".format(nb_pages))
        while True:
            self.minitel.move_cursor(1, 3)
            self.minitel.forms[0].text = "{:<3}".format(page_number + 1)
            for i in range(0, Search.NB_LINES):
                line_number = page_number * Search.NB_LINES + i
                if line_number < len(chunks):
                    self.minitel.print_text(chunks[line_number])
                self.minitel.clear_eol()
                self.minitel.move_cursor(1, 4 + i)
            while True:
                self.minitel.forms[0].initial_draw = True
                key = self.minitel.wait_form_inputs(force_form=0)
                if key == Terminal.RETOUR:
                    page_number = page_number - 1
                    if page_number < 0:
                        page_number = 0
                        self.minitel.bell()
                    break
                elif key == Terminal.SUITE:
                    page_number = page_number + 1
                    if page_number >= nb_pages:
                        page_number = 0
                    break
                elif key == Terminal.ENVOI:
                    try:
                        new_page_number = int(self.minitel.forms[0].text) - 1
                        if 0 <= new_page_number < nb_pages:
                            page_number = new_page_number
                            break
                        else:
                            self.minitel.bell()
                    except ValueError:
                        self.minitel.bell()
                elif key == Terminal.SOMMAIRE:
                    return

    def select_page(self, articles):
        """
            Ask user for a page
        """
        self.minitel.move_cursor(1, 3)
        for i in range(0, Search.NB_LINES):
            if i < len(articles):
                self.minitel.reverse_video()
                self.minitel.print_text("{:2}".format(i + 1))
                self.minitel.normal_video()
                self.minitel.print_text(" {}".format(articles[i][:36]))
            self.minitel.clear_eol()
            self.minitel.move_cursor(1, i + 4)
        self.minitel.clear_form_inputs()
        self.minitel.add_form_input(FormInput(35, 24, 2, initial_draw=True))
        self.minitel.forms[0].text = "1"
        self.minitel.move_cursor(25, 24)
        self.minitel.print_text("Selection : ")
        while True:
            key = self.minitel.wait_form_inputs(force_form=0)
            if key == Terminal.ENVOI:
                try:
                    new_page_number = int(self.minitel.forms[0].text) - 1
                    if 0 <= new_page_number < len(articles):
                        return new_page_number
                    else:
                        self.minitel.bell()
                except ValueError:
                    self.minitel.bell()
            elif key == Terminal.RETOUR or key == Terminal.SOMMAIRE:
                return None
