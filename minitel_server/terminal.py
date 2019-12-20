'''
Created on 18 Dec 2019

@author: mdonze
'''

import logging
from select import select
from minitel_server.exceptions import DisconnectedError, MinitelTimeoutError
import time

logger = logging.getLogger('Terminal')

class Terminal(object):
    '''
    Minitel terminal control
    '''
    #Some built-in constants
    CONN_TIMEOUT = 200          #Milliseconds to wait for connection data
    
    # Colour constants
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

    # Characters attributes
    CHAR_COLOR = 0x40           #Character colour
    BACK_COLOR = 0x50           #Background colour
    CURSOR_BLINK = 0x48         #Cursor blink
    CURSOR_FIXED = 0x49         #Cursor 
    START_INCRUSTATION = 0x4B   #Start incrustation
    END_INCRUSTATION = 0x4A     #End incrustation
    NORMAL_SIZE = 0x4C          #Characters normal size
    DOUBLE_HEIGHT = 0x4D        #Characters double height
    DOUBLE_WIDTH = 0x4E         #Characters double width
    DOUBLE_SIZE = 0x4F          #Characters double size
    START_LINE_MASK = 0x58
    END_LINE_MASK = 0x5F
    START_UNDERLINE = 0x5A      #Underline on
    END_UNDERLINE = 0x59        #Underline off
    REVERSE_VIDEO = 0x5D        #Video reversed
    NORMAL_VIDEO = 0x5C         #Video not-reversed
    TRANSPARENCY_VIDEO = 0x5E   #Transparency
    
    #Other constants
    BELL = 0x7
    CURSOR_LEFT = 0x8           #Move cursor left
    CURSOR_RIGHT = 0x9          #Move cursor right
    CURSOR_DOWN = 0xA           #Move cursor down
    CURSOR_UP = 0xB             #Move cursor up
    CLEAR_SCREEN = 0xC          #Clear screen
    SEMIGRAPHICS_MODE = 0xE     #Semi-graphics mode
    TEXT_MODE = 0xF             #Test mode
    CURSOR_VISIBLE = 0x11       #Visible cursor
    CURSOR_INVISIBLE = 0x14     #Invisible cursor
    CHAR_REPEAT = 0x12          #Character repeat
    ACCENT = 0x19               #Accent mode
    CURSOR_HOME = 0x1E          #Home cursor (line 1, col 1)
    CURSOR_MOVE = 0x1F          #Move cursor to coordinate

    # Keys constants
    ENVOI = 1
    RETOUR = 2
    REPETITION = 3
    GUIDE = 4
    ANNULATION = 5
    SOMMAIRE = 6
    CORRECTION = 7
    SUITE = 8
    CONNEXION_FIN = 9
    
    # Protocol constants
    ATTRIBUTE = 0x1B    #ESC
    SEP = 0x13          #SEP function
    ACK_PROTO = 0x1B    #Protocol acknowledge
    PRO1 = 0x39         #PRO 1 protocol (1 byte following)
    PRO2 = 0x3A         #PRO 2 protocol (2 bytes following)
    PRO3 = 0x3B         #PRO 3 protocol (3 bytes following)
       

    def __init__(self, con):
        '''
        Terminal constructor con is the TCP socket
        '''
        self.con = con
        self.forms = []
    
    def add_even_parity(self, data):
        '''
        Add even parity to bytes
        '''
        ret = bytearray()
        for b in data:
            if bin(b).count('1') % 2:
                b |= 0x80
            ret.append(b)
        return ret
    
    def remove_parity(self, data):
        '''
        Removes parity bit
        '''
        if not data:
            return data
        ret = []
        for c in data:
            c &= 0x7f
            ret.append(c)
        return ret
            
    def write(self, *data):
        '''
        Write to the socket
        '''
        bytes_data = bytearray()
        for d in data:
            if isinstance(d, str):
                bytes_data += bytearray(d, 'utf-8')
            elif isinstance(d, int):
                bytes_data += bytearray(d.to_bytes(1, 'big'))
            else:
                bytes_data += bytearray(d)
        logger.debug("Writing {} to Minitel".format(bytes_data))
        try:
            bytes_data = self.add_even_parity(bytes_data)
            self.con.sendall(bytes_data)
        except:
            raise DisconnectedError()
    
    def read(self, timeout=None):
        '''
        Reads a single byte from socket
        '''
        ready_to_read, _ready_to_write, _in_error = \
               select(
                  [self.con],
                  [],
                  [],
                  timeout)
        data = None
        if len(ready_to_read) != 0:
            data = self.remove_parity(self.con.recv(1))
            if not data:
                raise DisconnectedError
            return data[0]
        raise MinitelTimeoutError()
    
    def read_n(self, expected=1, timeout=None):
        '''
        Reads a given amount of data
        '''
        data = []
        while len(data) < expected:
            data += [self.read(timeout)]
        return data    
    
    def read_all(self):
        '''
        Reads all bytes in the receipt buffer
        Mainly use to flush
        '''
        data = []
        while True:
            d = self.remove_parity(self.con.recv(2048))
            if not d:
                return data
            data += [d]
    
    def wait_connection(self):
        '''
        Waits for connection garbage CHARACTERS
        '''
        logger.debug("Waiting for connection data...")
        try:
            self.read(self.CONN_TIMEOUT/1000)
        except MinitelTimeoutError:
            pass
    
    def home_cursor(self):
        '''
        Moves cursor to home (1,1) Position
        '''
        logger.debug("Move cursor to home")
        self.write(self.CURSOR_HOME)
    
    def clear_screen(self):
        '''
        Clears the Minitel screen
        '''
        logger.debug("Clear screen")
        self.write(self.CLEAR_SCREEN)
    
    def move_cursor(self, x, y):
        '''
        Moves cursor to absolute location
        '''
        logger.debug("Move cursor to {}/{}".format(x,y))
        data = [self.CURSOR_MOVE, 0x40, 0x40]
        data[1] |= y
        data[2] |= x
        self.write(data)
        
    def print_text(self, text):
        '''
        Print a text to the Minitel and replace accents
        '''
        text = text.replace('à', '\x19\x41a')
        text = text.replace('â', '\x19\x43a')
        text = text.replace('ä', '\x19\x48a')
        text = text.replace('è', '\x19\x41e')
        text = text.replace('é', '\x19\x42e')
        text = text.replace('ê', '\x19\x43e')
        text = text.replace('ë', '\x19\x48e')
        text = text.replace('î', '\x19\x43i')
        text = text.replace('ï', '\x19\x48i')
        text = text.replace('ô', '\x19\x43o')
        text = text.replace('ö', '\x19\x48o')
        text = text.replace('ù', '\x19\x43u')
        text = text.replace('û', '\x19\x43u')
        text = text.replace('ü', '\x19\x48u')
        text = text.replace('ç', '\x19\x4Bc')
        text = text.replace('°', '\x19\x30')
        text = text.replace('£', '\x19\x23')
        text = text.replace('Œ', '\x19\x6A').replace('œ', '\x19\x7A')
        text = text.replace('ß', '\x19\x7B')

        # Caractères spéciaux
        text = text.replace('¼', '\x19\x3C')
        text = text.replace('½', '\x19\x3D')
        text = text.replace('¾', '\x19\x3E')
        text = text.replace('←', '\x19\x2C')
        text = text.replace('↑', '\x19\x2D')
        text = text.replace('→', '\x19\x2E')
        text = text.replace('↓', '\x19\x2F')
        text = text.replace('̶', '\x60')
        text = text.replace('|', '\x7C')

        # Caractères accentués inexistants sur Minitel
        text = text.replace('À', 'A').replace('Â', 'A').replace('Ä', 'A')
        text = text.replace('È', 'E').replace('É', 'E')
        text = text.replace('Ê', 'E').replace('Ë', 'E')
        text = text.replace('Ï', 'I').replace('Î', 'I')
        text = text.replace('Ô', 'O').replace('Ö', 'O')
        text = text.replace('Ù', 'U').replace('Û', 'U').replace('Ü', 'U')
        text = text.replace('Ç', 'C')
        self.write(text)
        
    def wait_input(self, timeout=None):
        '''
        Waits for user input
        '''
        while True:
            data = self.read(timeout)
            if data == self.SEP:
                sep_key = self.read(timeout) 
                logger.debug("Got SEP key : 0x{0:x}".format(sep_key))
                return (True, sep_key - 0x40)
            elif data == self.ACK_PROTO:
                proto = self.read(timeout)
                logger.debug("Got protocol acknowledge 0x{0:x}".format(proto))
                if proto == self.PRO1:
                    data = self.read_n(1, timeout)
                elif proto == self.PRO2:
                    data = self.read_n(2, timeout)
                elif proto == self.PRO3:
                    data = self.read_n(3, timeout)
                else:
                    logger.warn("unsupported protocol ack.")
                    self.read_all()
            elif (data >= 0x20) and (data <= 0x7f):
                return (False, data)
            elif data == Terminal.ACCENT:
                ''' Accent '''
                acc_code = self.read(timeout)
                if acc_code == 0x23:
                    return (False, '£')
                elif acc_code == 0x27:
                    return (False, '§')
                elif acc_code == 0x2C:
                    return (False, '←')
                elif acc_code == 0x2D:
                    return (False, '↑')
                elif acc_code == 0x2E:
                    return (False, '→')
                elif acc_code == 0x2F:
                    return (False, '↓')
                elif acc_code == 0x30:
                    return (False, '°')
                elif acc_code == 0x31:
                    return (False, '±')
                elif acc_code == 0x3C:
                    return (False, '¼')
                elif acc_code == 0x3D:
                    return (False, '½')
                elif acc_code == 0x3E:
                    return (False, '¾')
                elif acc_code == 0x41:
                    acc_char = self.read(timeout)
                    if acc_char == 'a':
                        return (False, 'à')
                    elif acc_char == 'e':
                        return (False, 'è')
                    elif acc_char == 'i':
                        return (False, 'ì')
                    elif acc_char == 'o':
                        return (False, 'ò')
                    elif acc_char == 'u':
                        return (False, 'ù')
                    else:
                        return (False, acc_char)
                elif acc_code == 0x42:
                    acc_char = self.read(timeout)
                    if acc_char == 'a':
                        return (False, 'á')
                    elif acc_char == 'e':
                        return (False, 'é')
                    elif acc_char == 'i':
                        return (False, 'í')
                    elif acc_char == 'o':
                        return (False, 'ó')
                    elif acc_char == 'u':
                        return (False, 'ú')
                    else:
                        return (False, acc_char)
                elif acc_code == 0x43:
                    acc_char = self.read(timeout)
                    if acc_char == 'a':
                        return (False, 'â')
                    elif acc_char == 'e':
                        return (False, 'ê')
                    elif acc_char == 'i':
                        return (False, 'î')
                    elif acc_char == 'o':
                        return (False, 'ô')
                    elif acc_char == 'u':
                        return (False, 'û')
                    else:
                        return (False, acc_char)
                elif acc_code == 0x48:
                    acc_char = self.read(timeout)
                    if acc_char == 'a':
                        return (False, 'ä')
                    elif acc_char == 'e':
                        return (False, 'ë')
                    elif acc_char == 'i':
                        return (False, 'ï')
                    elif acc_char == 'o':
                        return (False, 'ö')
                    elif acc_char == 'u':
                        return (False, 'ü')
                    else:
                        return (False, acc_char)
                elif acc_code == 0x6A:
                    return (False, 'Œ')
                elif acc_code == 0x7A:
                    return (False, 'œ')
                elif acc_code == 0x7B:
                    return (False, 'ß')
            else:
                logger.error("Got out of range character :0x{0:x}".format(data))
    
    def text_colour(self, colour):
        '''
        Set the text colour
        '''
        logger.debug("Setting char colour to {}".format(colour))
        self.write(self.ATTRIBUTE, ((colour & 0xF) | self.CHAR_COLOR))
        
    def background_colour(self, colour):
        '''
        Set the text background colour
        '''
        logger.debug("Setting background colour to {}".format(colour))
        self.write(self.ATTRIBUTE, ((colour & 0xF) | self.BACK_COLOR))
    
    def reverse_video(self):
        '''
        Sets the video in reverse mode
        '''
        self.write(self.ATTRIBUTE, self.REVERSE_VIDEO);
        
    def normal_video(self):
        '''
        Sets the video in normal mode
        '''
        self.write(self.ATTRIBUTE, self.NORMAL_VIDEO);
    
    def transparent_video(self):
        '''
        Sets the video in transparent mode
        '''
        self.write(self.ATTRIBUTE, self.TRANSPARENCY_VIDEO);
        
    def blink_cursor(self, blink=True):
        '''
        Sets if the cursor is blinking
        '''
        if blink is True:
            self.write(self.ATTRIBUTE, self.CURSOR_BLINK)
        else:
            self.write(self.ATTRIBUTE, self.CURSOR_FIXED)
    
    def normal_size(self):
        '''
        Sets the text in normal size
        '''
        self.write(self.ATTRIBUTE, self.NORMAL_SIZE)
    
    def double_height_size(self):
        '''
        Sets the text in double height size
        '''
        self.write(self.ATTRIBUTE, self.DOUBLE_HEIGHT)

    def double_width_size(self):
        '''
        Sets the text in double width size
        '''
        self.write(self.ATTRIBUTE, self.DOUBLE_WIDTH)

    def double_size(self):
        '''
        Sets the text in double size
        '''
        self.write(self.ATTRIBUTE, self.DOUBLE_SIZE)

    def underline(self, on=True):
        '''
        Sets underline on/off
        '''
        if on is True:
            self.write(self.ATTRIBUTE, self.START_UNDERLINE)
        else:
            self.write(self.ATTRIBUTE, self.END_UNDERLINE)
    
    def bell(self):
        '''
        Sends a bell to Minitel
        '''
        self.write(self.BELL)
    
    def move_cursor_left(self):
        '''
        Moves cursor to left by one column
        '''
        self.write(self.CURSOR_LEFT)

    def move_cursor_right(self):
        '''
        Moves cursor to right by one column
        '''
        self.write(self.RIGHT)
        
    def move_cursor_up(self):
        '''
        Moves cursor up by one line
        '''
        self.write(self.UP)

    def move_cursor_down(self):
        '''
        Moves cursor down by one line
        '''
        self.write(self.DOWN)

    def semigraphics_mode(self):
        '''
        Switch to semi-graphics mode
        '''
        self.write(self.SEMIGRAPHICS_MODE)
    
    def text_mode(self):
        '''
        Switch to text mode
        '''
        self.write(self.TEXT_MODE)
    
    def visible_cursor(self, visible=True):
        '''
        Sets if the cursor will be visible or invisible
        '''
        if visible is True:
            self.write(self.CURSOR_VISIBLE)
        else:
            self.write(self.CURSOR_INVISIBLE)
    
    def draw_file(self, filename):
        '''
        Send a raw file to Minitel (VTX. VTD files)
        '''
        logger.debug("Rendering file {}".format(filename))
        try:
            with open(filename, 'rb') as f:
                self.con.sendall(f.read())
        except:
            raise DisconnectedError()
    
    def add_form_input(self, form_input):
        '''
        Adds a form input
        '''
        self.forms.append(form_input)
    
    def clear_form_inputs(self):
        '''
        Removes all forms
        '''
        self.forms.clear()
    
    def wait_form_inputs(self):
        '''
        Waits for user inputs to be filled
        '''
        for f in self.forms:
            f.prepare(self)
            
        current_input = 0;
        while True:
            key = self.forms[current_input].grab_focus(self)
            if key == self.SUITE:
                current_input += 1
                if current_input>= len(self.forms):
                        current_input = 0
                logger.debug("Moving to next form input : {}".format(current_input))
            else:
                return key
    
    def print_repeat(self, c, count):
        '''
        Print character c count times
        '''
        self.write(c)
        if count > 2:
            self.write(self.CHAR_REPEAT, (0x40 | count-1))
        else:
            for _i in range(1, count):
                self.write(c)

    def show_message(self, text, duration=2):
        '''
        Displays a notification message on top left of screen
        User must move back the cursor to continue (and put it visible)
        '''
        self.visible_cursor(False)
        self.move_cursor(1, 0)
        self.print_text(text)
        time.sleep(duration)
        self.move_cursor(1, 0)
        self.print_repeat(' ', len(text))


class FormInput(object):
    '''
    Represents an input form
    '''
    
    def __init__(self, locx, locy, lenght,
                 text = "",
                 colour=Terminal.WHITE,
                 initial_draw = False,
                 placeholder = '.'):
        '''
        locx : Start X location of the input
        locy : Start Y location of the input
        lenght : Maximum lenght of the input
        text : Initial text
        initial_draw : True if the input needs to be drawn
        placeholder : Character to put as placeholder
        colour : Text colour
        '''
        self._locx = locx
        self._locy = locy
        self._lenght = lenght
        self.text = text[0:self._lenght]
        self._initial_draw = initial_draw
        self._placeholder = placeholder
        self._colour = colour
    
    def prepare(self, terminal):
        '''
        Prepare form input by drawing placeholder, if enabled
        '''
        if self._initial_draw :
            #Print the initial form text
            terminal.move_cursor(self._locx, self._locy)            
            terminal.text_colour(self._colour)
            terminal.print_text(self.text)
            rem = self._lenght - len(self.text)
            if rem > 0:
                terminal.print_repeat(self._placeholder, rem)
    
    def grab_focus(self, terminal):
        '''
        Manage this input
        '''
        #Print the initial form text

        
        offset = len(self.text)
        if offset >= self._lenght:
            offset = self._lenght - 1
        terminal.move_cursor(self._locx + offset, self._locy)
        terminal.text_colour(self._colour)
        terminal.visible_cursor(True)
        while True:
            sep, key = terminal.wait_input()
            if sep is True:
                #Minitel key
                if key == Terminal.CORRECTION:
                    if len(self.text)<1:
                        terminal.bell()
                    else:
                        #Don't move back if we are at the end of the field
                        if (len(self.text)< self._lenght):
                            terminal.move_cursor_left()
                        terminal.print_text(self._placeholder)
                        terminal.move_cursor_left()
                        self.text = (self.text[0:-1])                        
                else:
                    return key
            else:
                if len(self.text) >= self._lenght:
                    terminal.bell()
                else:
                    c = chr(key)
                    self.text += c
                    terminal.print_text(c)
                    #Move back if we are at the end of the field
                    if len(self.text) >= self._lenght:
                        terminal.move_cursor_left()
            logger.debug("New text is {}".format(self.text))