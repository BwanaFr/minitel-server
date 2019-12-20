'''
Created on 24 Oct 2019

@author: mdonze
'''
from builtins import Exception

class DisconnectedError(Exception):
    '''
    Minitel is disconnected
    '''
    pass

class MinitelTimeoutError(Exception):
    '''
    Communication timeout
    '''
    pass

class UserTerminateSessionError(Exception):
    '''
    User wants to terminate the session
    '''
    pass