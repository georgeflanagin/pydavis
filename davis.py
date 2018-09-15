#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Talk to a Davis Instruments weather station.
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
import argparse
import cmd
import enum
import logging
import os
import pdb
import socket
import subprocess
import sys
import time
import typing
from   typing import *

if sys.version_info < __required_version__:
    print('This program is compatible with Python {}.{} and later.'.format(
        sys.version_info.major, sys.version_info.minor)
        )
    sys.exit(os.EX_SOFTWARE)

# Paramiko
import logging

# From gkflib

import fname
import setproctitle
import gkflib as gkf
import beachhead

# From this project

import daviscommands as dc

class Davis(cmd.Cmd):

    use_rawinput = True
    doc_header = 'To get a little overall guidance, type `help general`'
    # intro = "\n".join(banner)

    def __init__(self):
        
        cmd.Cmd.__init__(self)
        Davis.prompt = "\n[Davis]: "
        self.connection = None


    
    def __bool__(self) -> bool: 
        return self.sock is not None


    def preloop(self) -> None:
        setproctitle.setproctitle('Davis')


    def default(self, data:str="") -> None:
        gkf.tombstone(beachhead.red('unknown command {}'.format(data)))
        self.do_help(data)


    def do_connect(self, info:str="") -> None:
        """
        Usage: connect {IP|name} {port}
        """
        info = info.strip().split()
        self.connection = beachhead.SocketConnection()
        try:
            self.connection.open_socket(info[0], int(info[1]))
        except Exception as e:
            gkf.tombstone(gkf.type_and_text(e))
            return

        print('Connected to /something/ at {}:{}'.format(info[0],info[1]))
        print('Ready to talk. Sending TEST')
        self.connection.send('TEST')
        reply = self.read()
        print('Received {} as reply'.format(reply))


    def do_exit(self, info:str="") -> None:
        """
        Usage: exit
        """
        self.connection.close()
        sys.exit(os.EX_OK)


if __name__ == "__main__":

    # subprocess.call('clear',shell=True)
    while True:
        try:
            Davis().cmdloop()

        except KeyboardInterrupt:
            gkf.tombstone("Exiting via control-C.")
            sys.exit(os.EX_OK)

        except Exception as e:
            gkf.tombstone(gkf.type_and_text(e))
            gkf.tombstone(gkf.formatted_stack_trace(True))
            sys.exit(1) 
