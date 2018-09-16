# -*- coding: utf-8 -*-
"""
Give names to the Davis Instruments commands and constants.

A considerable adaptation has been made from the `weatherlink-python`
project on GitHub, by Nick Williams of Cane Ridge TN. His code is
licensed under Apache 2.0.

This library is specifically [re]written for Python 3.7 and later,
and makes use of numpy and a few other well known Python libraries.
This code exploits the availability of SQLite and its absence of 
state, rather than using MySQL. Just a personal choice, as well as
giving the code the ability to run just about anywhere (Raspberry Pi?)
without installing a database. 
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


class DavisResponses(enum.Enum):
    ACK = prepx('06')
    OK = prep('\n\rOK\n\r')
    DONE = prep('DONE\n\r')
    AWAKE = prepx('0A0D')


class DavisConversions:
    """
    This `class` is more like an enum of functions to do some of
    the work in unit conversion, and calculations of values that
    are not directly observed. 
    """

    _TENTHS = 0.1
    TENTHS = lambda x: x * _TENTHS

    _HUNDREDTHS = 0.01
    HUNDREDTHS = lambda x: x * _HUNDREDTHS

    _THOUSANDTHS = 0.001
    THOUSANDTHS = lambda x: x * _THOUSANDTHS

    _INCHES_PER_CENTIMETER = 0.393701


dc = DavisConversions

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

 
class LoopRecord:
    """
    This class has been taken directly from Nick Williams weatherlink-python
    project. I am really glad that I did not have to type in this entire
    definition.
    """
    RECORD_LENGTH = 99

    LOOP1_RECORD_TYPE = 0
    LOOP2_RECORD_TYPE = 1

    LOOP2_RECORD_FORMAT = (
        '<3s'  # String 'LOO'
        'b'  # barometer trend
        'B'  # Should be 1 for "LOOP 2" (0 would indicate "LOOP 1")
        'H'  # Unused, should be 0x7FFF
        'H'  # Barometer in thousandths of inches of mercury
        'h'  # Inside temperature in tenths of degrees Fahrenheit
        'B'  # Inside humidity in whole percents
        'h'  # Outside temperature in tenths of degrees Fahrenheit
        'B'  # Wind speed in MPH
        'B'  # Unused, should be 0xFF
        'H'  # Wind direction in degrees, 0 = no wind, 1 = nearly N, 90 = E, 180 = S, 270 = W, 360 = N
        'H'  # 10-minute wind average speed in tenths of MPH
        'H'  # 2-minute wind average speed in tenths of MPH
        'H'  # 10-minute wind gust speed in tenths of MPH
        'H'  # 10-minute wind gust direction in degrees
        'H'  # Unused, should be 0x7FFF
        'H'  # Unused, should be 0x7FFF
        'h'  # Dew point in whole degrees Fahrenheit
        'B'  # Unused, should be 0xFF
        'B'  # Outside humidity in whole percents
        'B'  # Unused, should be 0xFF
        'h'  # Heat index in whole degrees Fahrenheit
        'h'  # Wind chill in whole degrees Fahrenheit
        'h'  # THSW index in whole degrees Fahrenheit
        'H'  # Rain rate in clicks/hour
        'B'  # UV Index
        'H'  # Solar radiation in watts per square meter
        'H'  # Number of rain clicks this storm
        '2x'  # Useless start date of this storm, which we don't care about
        'H'  # Number of rain clicks today
        'H'  # Number of rain clicks last 15 minutes
        'H'  # Number of rain clicks last 1 hour
        'H'  # Daily total evapotranspiration in thousandths of inches
        'H'  # Number of rain clicks last 24 hours
        '11x'  # Barometer calibration-related settings and readings
        'B'  # Unused, should be 0xFF
        'x'  # Unused field filled with undefined data
        '6x'  # Information about what's displayed on the console graph, which we don't care about
        'B'  # The minute within the hour, 0-59
        '3x'  # Information about what's displayed on the console graph, which we don't care about
        'H'  # Unused, should be 0x7FFF
        'H'  # Unused, should be 0x7FFF
        'H'  # Unused, should be 0x7FFF
        'H'  # Unused, should be 0x7FFF
        'H'  # Unused, should be 0x7FFF
        'H'  # Unused, should be 0x7FFF
        'c'  # Should be '\n'
        'c'  # Should be '\r'
        'H'  # Cyclic redundancy check (CRC)
    )

    LOOP2_RECORD_VERIFICATION_MAP_WLK = {
        0: 'LOO',
        2: 1,
        3: 0x7FFF,
        9: 0xFF,
        15: 0x7FFF,
        16: 0x7FFF,
        18: 0xFF,
        20: 0xFF,
        33: 0xFF,
        35: 0x7FFF,
        36: 0x7FFF,
        37: 0x7FFF,
        38: 0x7FFF,
        39: 0x7FFF,
        40: 0x7FFF,
        41: '\n',
        42: '\r',
    }

    LOOP2_RECORD_SPECIAL_HANDLING = frozenset(LOOP2_RECORD_VERIFICATION_MAP_WLK.keys())

    LOOP2_RECORD_ATTRIBUTE_MAP = (
        ('_special', int, None, ),
        ('barometric_trend', int, 80, ),
        ('_special', int, None, ),
        ('_special', int, None, ),
        ('barometric_pressure', dc.THOUSANDTHS, 0, ),
        ('temperature_inside', dc.TENTHS, 32767, ),
        ('humidity_inside', int, 255, ),
        ('temperature_outside', dc.TENTHS, 32767, ),
        ('wind_speed', float, 255, ),
        ('_special', int, None, ),
        ('wind_direction_degrees', int, 0, ),
        ('wind_speed_10_minute_average', dc.TENTHS, 0, ),
        ('wind_speed_2_minute_average', dc.TENTHS, 0, ),
        ('wind_speed_10_minute_gust', dc.TENTHS, 0, ),
        ('wind_speed_10_minute_gust_direction_degrees', int, 0, ),
        ('_special', int, None, ),
        ('_special', int, None, ),
        ('dew_point', float, 255, ),
        ('_special', int, None, ),
        ('humidity_outside', int, 255, ),
        ('_special', int, None, ),
        ('heat_index', int, 255, ),
        ('wind_chill', int, 255, ),
        ('thsw_index', int, 255, ),
        ('rain_rate_clicks', int, None, ),
        ('uv_index', dc.TENTHS, 255, ),
        ('solar_radiation', int, 32767, ),
        ('rain_clicks_this_storm', int, None, ),
        ('rain_clicks_today', int, None, ),
        ('rain_clicks_15_minutes', int, None, ),
        ('rain_clicks_1_hour', int, None, ),
        ('evapotranspiration', dc.THOUSANDTHS, 0, ),
        ('rain_clicks_24_hours', int, None, ),
        ('_special', int, None),
        ('minute_in_hour', int, 60, ),
    )

    LOOP_WIND_DIRECTION_SPECIAL = (
        ('wind_direction_degrees', 'wind_direction', ),
        ('wind_speed_10_minute_gust_direction_degrees', 'wind_speed_10_minute_gust_direction', ),
    )

    LOOP_RAIN_AMOUNT_SPECIAL = (
        ('rain_rate_clicks', 'rain_rate', ),
        ('rain_clicks_this_storm', 'rain_amount_this_storm', ),
        ('rain_clicks_today', 'rain_amount_today', ),
        ('rain_clicks_15_minutes', 'rain_amount_15_minutes', ),
        ('rain_clicks_1_hour', 'rain_amount_1_hour', ),
        ('rain_clicks_24_hours', 'rain_amount_24_hours', ),
    )

    @classmethod
    def load_loop_1_2_from_connection(cls, socket_file):
        arguments = cls._get_loop_1_arguments(socket_file, True)
        arguments.update(cls._get_loop_2_arguments(socket_file))
        return cls(**arguments)

    @classmethod
    def load_loop_1_from_connection(cls, socket_file):
        return cls(**cls._get_loop_1_arguments(socket_file))

    @classmethod
    def load_loop_2_from_connection(cls, socket_file):
        return cls(**cls._get_loop_2_arguments(socket_file))

    @classmethod
    def _get_loop_1_arguments(cls, socket_file, unique_only=False):
        raise NotImplementedError()

    @classmethod
    def _get_loop_2_arguments(cls, socket_file):
        data = socket_file.read(cls.RECORD_LENGTH)

        unpacked = struct.unpack_from(cls.LOOP2_RECORD_FORMAT, data)

        for k, v in six.iteritems(cls.LOOP2_RECORD_VERIFICATION_MAP_WLK):
            assert unpacked[k] == v

        arguments = {'crc_match': calculate_weatherlink_crc(data) == 0, 'record_type': 2}

        last = len(cls.LOOP2_RECORD_ATTRIBUTE_MAP)
        for i, v in enumerate(unpacked):
            if (i < last and i not in cls.LOOP2_RECORD_VERIFICATION_MAP_WLK and
                        i not in cls.LOOP2_RECORD_SPECIAL_HANDLING):
                k = cls.LOOP2_RECORD_ATTRIBUTE_MAP[i][0]
                if v == cls.LOOP2_RECORD_ATTRIBUTE_MAP[i][2]:
                    arguments[k] = None
                else:
                    arguments[k] = cls.LOOP2_RECORD_ATTRIBUTE_MAP[i][1](v)

        cls._post_process_arguments(arguments)

        return arguments

    @classmethod
    def _post_process_arguments(cls, arguments):
        # The online download does not contain this information, unfortunately
        rain_collector_type = RainCollectorTypeSerial.inches_0_01

        try:
            arguments['barometric_trend'] = BarometricTrend(arguments['barometric_trend'])
        except ValueError:
            arguments['barometric_trend'] = None

        for k1, k2 in cls.LOOP_WIND_DIRECTION_SPECIAL:
            if arguments[k1]:
                arguments[k2] = WindDirection.from_degrees(arguments[k1])
            else:
                arguments[k2] = None

        for k1, k2 in cls.LOOP_RAIN_AMOUNT_SPECIAL:
            if arguments[k1]:
                arguments[k2] = rain_collector_type.clicks_to_inches(arguments[k1])
            else:
                arguments[k2] = None


