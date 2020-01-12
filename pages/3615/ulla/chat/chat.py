"""
Created on 26 Dec 2019

@author: mdonze
"""
import collections
import queue

from minitel_server.page import DefaultPageHandler, PageContext, \
    Page
import logging
from minitel_server.terminal import Terminal
from minitel_server.exceptions import UserTerminateSessionError, MinitelTimeoutError, DisconnectedError
import threading

logger = logging.getLogger('Ullapage')


class HandlerUllaChat(DefaultPageHandler):
    """
    A basic chat for Ulla
    """

    class __UllaChatRoom(threading.Thread):
        """
        Chat room
        """

        def __init__(self):
            threading.Thread.__init__(self)
            self._clients = []
            self._lock = threading.RLock()
            self._message_queue = queue.Queue()

        def add_client(self, client):
            self._lock.acquire()
            self._clients.append(client)
            self._lock.release()
            self._message_queue.put({"type": "add"})

        def remove_client(self, client):
            self._lock.acquire()
            self._clients.remove(client)
            self._lock.release()
            self._message_queue.put({"type": "remove"})

        def get_user_count(self):
            self._lock.acquire()
            users = len(self._clients)
            self._lock.release()
            return users

        def run(self):
            while True:
                message = self._message_queue.get()
                if message is not None:
                    self._lock.acquire()
                    for c in self._clients:
                        c.new_message(message)
                    self._lock.release()

        def send_message(self, message):
            message["type"] = "message"
            self._message_queue.put(message)

    # Singleton for chat
    chat_room = None

    def __init__(self, minitel, context):
        """
        Constructor
        """
        super().__init__(minitel, context)
        logger.info('HandlerUllaChat: in our custom handler')
        if not HandlerUllaChat.chat_room:
            HandlerUllaChat.chat_room = HandlerUllaChat.__UllaChatRoom()
            HandlerUllaChat.chat_room.start()
        HandlerUllaChat.chat_room.add_client(self)
        self._messages = collections.deque(maxlen=17)
        self.user_name = self.context.data["username"]
        self._new_message_queue = queue.Queue()

    def after_rendering(self):
        logger.debug('HandlerUllaChat: In after_rendering callback')
        try:
            while True:
                if not self._new_message_queue.empty():
                    self.minitel.visible_cursor(False)
                    update_user_count = False
                    while True:
                        try:
                            item = self._new_message_queue.get_nowait()
                            if item['type'] != 'message':
                                update_user_count = True
                            self._messages.append(item)
                        except queue.Empty:
                            break
                    if update_user_count:
                        self.minitel.move_cursor(1, 3)
                        count = HandlerUllaChat.chat_room.get_user_count()
                        if count == 1:
                            self.minitel.print_text("1 utilisateur en ligne")
                        else:
                            self.minitel.print_text(
                                "{} utilisateurs en ligne".format(count))
                        self.minitel.clear_eol();

                    i = 5
                    for m in self._messages:
                        if m['type'] == 'message':
                            self.minitel.move_cursor(1, i)
                            self.minitel.text_colour(Terminal.BLUE)
                            self.minitel.print_text(m['user'])
                            self.minitel.text_colour(Terminal.CYAN)
                            self.minitel.print_text('→')
                            self.minitel.text_colour(Terminal.WHITE)
                            self.minitel.print_text(m['message'])
                            self.minitel.clear_eol()
                            i = i + 1
                    logger.debug("Messages printed")
                try:
                    key = self.minitel.wait_form_inputs(0.2)
                    if key == Terminal.ENVOI:
                        HandlerUllaChat.chat_room.send_message({"user": self.user_name,
                                                                "message": self.minitel.forms[0].text})
                        self.minitel.forms[0].text = ""
                        self.minitel.forms[0].initial_draw = True
                    elif key == Terminal.RETOUR:
                        next_page = Page.get_page(self.context.current_page.service, "ulla.home")
                        HandlerUllaChat.chat_room.remove_client(self)
                        return PageContext(self.context, self.context.previous.data, next_page)
                    elif key == Terminal.CONNEXION_FIN:
                        logger.debug("Connection/fin from {}".format(self.context.current_page.fullname))
                        HandlerUllaChat.chat_room.remove_client(self)
                        raise UserTerminateSessionError
                except MinitelTimeoutError:
                    pass
        except DisconnectedError as e:
            logger.debug("User {} disconnected".format(self.user_name))
            HandlerUllaChat.chat_room.remove_client(self)
            raise e

        return None

    def new_message(self, message):
        if message is not None:
            logger.debug("New message : {}".format(message))
            self._new_message_queue.put(message)
