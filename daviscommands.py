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
import datetime
import enum
import os
import struct
import sys
import time
import typing
from   typing import *

# Installed

import numpy as np

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

class CRC:
    """
    CRC values are sent big endian, unlike everything else that
    is sent little endian. This information appears of page 38
    of 60 in the spec.
    """

    crc_table = np.array([ 
           0x0,  0x1021,  0x2042,  0x3063,  0x4084,  0x50a5,  0x60c6,  0x70e7,
        0x8108,  0x9129,  0xa14a,  0xb16b,  0xc18c,  0xd1ad,  0xe1ce,  0xf1ef,
        0x1231,   0x210,  0x3273,  0x2252,  0x52b5,  0x4294,  0x72f7,  0x62d6,
        0x9339,  0x8318,  0xb37b,  0xa35a,  0xd3bd,  0xc39c,  0xf3ff,  0xe3de,
        0x2462,  0x3443,   0x420,  0x1401,  0x64e6,  0x74c7,  0x44a4,  0x5485,
        0xa56a,  0xb54b,  0x8528,  0x9509,  0xe5ee,  0xf5cf,  0xc5ac,  0xd58d,
        0x3653,  0x2672,  0x1611,   0x630,  0x76d7,  0x66f6,  0x5695,  0x46b4,
        0xb75b,  0xa77a,  0x9719,  0x8738,  0xf7df,  0xe7fe,  0xd79d,  0xc7bc,
        0x48c4,  0x58e5,  0x6886,  0x78a7,   0x840,  0x1861,  0x2802,  0x3823,
        0xc9cc,  0xd9ed,  0xe98e,  0xf9af,  0x8948,  0x9969,  0xa90a,  0xb92b,
        0x5af5,  0x4ad4,  0x7ab7,  0x6a96,  0x1a71,   0xa50,  0x3a33,  0x2a12,
        0xdbfd,  0xcbdc,  0xfbbf,  0xeb9e,  0x9b79,  0x8b58,  0xbb3b,  0xab1a,
        0x6ca6,  0x7c87,  0x4ce4,  0x5cc5,  0x2c22,  0x3c03,   0xc60,  0x1c41,
        0xedae,  0xfd8f,  0xcdec,  0xddcd,  0xad2a,  0xbd0b,  0x8d68,  0x9d49,
        0x7e97,  0x6eb6,  0x5ed5,  0x4ef4,  0x3e13,  0x2e32,  0x1e51,   0xe70,
        0xff9f,  0xefbe,  0xdfdd,  0xcffc,  0xbf1b,  0xaf3a,  0x9f59,  0x8f78,
        0x9188,  0x81a9,  0xb1ca,  0xa1eb,  0xd10c,  0xc12d,  0xf14e,  0xe16f,
        0x1080,    0xa1,  0x30c2,  0x20e3,  0x5004,  0x4025,  0x7046,  0x6067,
        0x83b9,  0x9398,  0xa3fb,  0xb3da,  0xc33d,  0xd31c,  0xe37f,  0xf35e,
         0x2b1,  0x1290,  0x22f3,  0x32d2,  0x4235,  0x5214,  0x6277,  0x7256,
        0xb5ea,  0xa5cb,  0x95a8,  0x8589,  0xf56e,  0xe54f,  0xd52c,  0xc50d,
        0x34e2,  0x24c3,  0x14a0,   0x481,  0x7466,  0x6447,  0x5424,  0x4405,
        0xa7db,  0xb7fa,  0x8799,  0x97b8,  0xe75f,  0xf77e,  0xc71d,  0xd73c,
        0x26d3,  0x36f2,   0x691,  0x16b0,  0x6657,  0x7676,  0x4615,  0x5634,
        0xd94c,  0xc96d,  0xf90e,  0xe92f,  0x99c8,  0x89e9,  0xb98a,  0xa9ab,
        0x5844,  0x4865,  0x7806,  0x6827,  0x18c0,   0x8e1,  0x3882,  0x28a3,
        0xcb7d,  0xdb5c,  0xeb3f,  0xfb1e,  0x8bf9,  0x9bd8,  0xabbb,  0xbb9a,
        0x4a75,  0x5a54,  0x6a37,  0x7a16,   0xaf1,  0x1ad0,  0x2ab3,  0x3a92,
        0xfd2e,  0xed0f,  0xdd6c,  0xcd4d,  0xbdaa,  0xad8b,  0x9de8,  0x8dc9,
        0x7c26,  0x6c07,  0x5c64,  0x4c45,  0x3ca2,  0x2c83,  0x1ce0,   0xcc1,
        0xef1f,  0xff3e,  0xcf5d,  0xdf7c,  0xaf9b,  0xbfba,  0x8fd9,  0x9ff8,
        0x6e17,  0x7e36,  0x4e55,  0x5e74,  0x2e93,  0x3eb2,   0xed1,  0x1ef0
        ], dtype = np.uint16)

    crc_init = 0x0000

    def __call__(data:Any) -> np.uint16:
        if isinstance(data, str): 
            data = prep(data)

        elif not isinstance(data, bytearray):
            return NotImplemented

        else:
            pass

        AX = CRC.crc_init
        for b in data:
            AX = CRC.crc_table[(AX >> 8) ^ b] ^ (AX << 8)
        return crc


    def __bool__(checksum:np.uint16) -> bool:
        """
        Check the checksum.
        """
        return crc_table[(checksum >> 8) ^ b] ^ (checksum << 8) == 0
            

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


class DavisDate:
    """
    Convert Davis date stamps written as:
        7 bit year | 4 bit month | 5 bit day
    with the year having an offset of 2000 to a Python date.
    """
    
    def from_davis(value:np.uint16) -> datetime.date:
        year = value >> 9
        month = value & 0b0000000111100000 >> 5
        day = value & 31
        return datetime.date(year+2000, month, day)

    def to_davis(d:datetime.date) -> np.uint16:
        return np.uint16((d.year-2000) << 9 + d.month << 5 + d.day)
    

class DavisTime:
    """
    Convert Davis times of h*100 + minute to a Python time.
    """
    
    def from_davis(value:np.uint16) -> datetime.time:
        m = value % 100
        h = value // 100
        return datetime.time(h, m)

    def to_davis(value:datetime.time) -> np.uint16:
        return value.hour * 100 + value.minute

 
