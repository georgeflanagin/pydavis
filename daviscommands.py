#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Give names to the Davis Instruments commands.
"""

__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2018'
__credits__ = None
__version__ = '0.1'
__maintainer__ = 'George Flanagin'
__email__ = 'me+davis@georgeflanagin.com'
__status__ = 'Prototype'
__required_version__ = (3,7)

# Builtins
import enum
import os
import sys
import typing
from   typing import *

if sys.version_info < __required_version__:
    print('This program is compatible with Python {}.{} and later.'.format(
        sys.version_info.major, sys.version_info.minor)
        )
    sys.exit(os.EX_SOFTWARE)

utf8 = 'utf-8'

def prep(s:str) -> bytearray:
    """
    Convert a string to a bytearray suitable for sending through
    a socket connection.
    """
    return bytearray(s, 'utf-8')


def prepx(s:str) -> bytearray:
    """
    As above, but the string is assumed to be a collection of hex
    digits (0-9A-F). 
    """
    try:
        return bytearray.fromhex(s)
    except ValueError as e:
        gkf.tombstone('{} cannot be converted to hex'.format(s))
        raise e from None


class DavisCommand(enum.Enum):
    """
    These commands are sent to the Vantage[x] console. They
    have been taken from pages 6-21 of Rev 2.6.1 of the 
    Vantage Serial Protocol document, March 29, 2013.

    Commands with a NL ('\n') appended, are complete, whereas 
    ones that do not include the new line must be supplied
    parameters. The line breaks below represent the inclusion
    of the commands in sections of the document.
    """
    WAKEUP = prepx('0A')

    TEST = prep('TEST\n')    
    WRD = prep('WRD').extend(prepx('124D0A'))
    RXCHECK = prep('RXCHECK\n')
    VER = prep('RXTEST\n')
    RECEIVERS = prep('RECEIVERS\n')
    NVER = prep('NVER\n')
    
    LOOP = prep('LOOP')
    LPS = prep('LPS')
    HILOWS = prep('HILOWS')
    PUTRAIN = prep('PUTRAIN')
    PUTEST = prep('PUTET')

    DMP = prep('DMP\n')
    DMPAFT = prep('DMPAFT')
    
    GETEE = prep('GETEE\n')
    EEWR = prep('EEWR')
    EERD = prep('EERD')
    EEBWR = prep('EEBWR')
    EEBRD = prep('EEBRD')
    CALED = prep('CALED\n')
    CALFIX = prep('CALFIX\n')
    BAR = prep('BAR')
    BARDATA = prep('BARDATA\n')
    CLRLOG = prep('CLRLOG\n') # TODO: this is a dangerous command.
    CLRALM = prep('CLRALM\n')
    CLRCAL = prep('CLRCAL\n')
    CLRGRA = prep('CLRGRA\n')
    CLRVAR = prep('CLRVAR')
    CLRHIGHS = prep('CLRHIGHS')
    CLRLOWS = prep('CLRLOWS')
    CLRBITS = prep('CLRBITS\n')
    SETTIME = prep('SETTIME')
    GETTIME = prep('GETTIME\n')
    GAIN_ON = prep('GAIN 1\n')
    GAIN_OFF = prep('GAIN 0\n')
    SETPER = prep('SETPER')
    STOP = prep('STOP\n')
    START = prep('START\n')
    NEWSETUP = prep('NEWSETUP\n') # TODO: this is a dangerous command.
    LAMP_ON = prep('LAMPS 1\n')
    LAMP_OFF = prep('LAMPS 0\n')
    

class DavisResponse(enum.Enum):
    ACK = prepx('06')
    OK = prep('\n\rOK\n\r')
    DONE = prep('DONE\n\r')
    AWAKE = prepx('0A0D')

