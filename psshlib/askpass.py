#!/usr/bin/env python
# -*- Mode: python -*-

# Copyright (c) 2009, Andrew McNabb

"""Implementation of SSH_ASKPASS to get a password to ssh from pssh.

The password is read from the socket specified by the environment variable
PSSH_ASKPASS_SOCKET.  The other end of this socket is pssh.

The ssh man page discusses SSH_ASKPASS as follows:
    If ssh needs a passphrase, it will read the passphrase from the current
    terminal if it was run from a terminal.  If ssh does not have a terminal
    associated with it but DISPLAY and SSH_ASKPASS are set, it will execute
    the program specified by SSH_ASKPASS and open an X11 window to read the
    passphrase.  This is particularly useful when calling ssh from a .xsession
    or related script.  (Note that on some machines it may be necessary to
    redirect the input from /dev/null to make this work.)
"""

import os
import socket
import sys
import textwrap

askpass_path = os.path.splitext(os.path.abspath(__file__))[0] + '.py'
ASKPASS_PATHS = (askpass_path,
        '/usr/libexec/pssh/pssh_askpass',
        '/usr/local/libexec/pssh/pssh_askpass')

_executable_path = None

def executable_path():
    """Determines the value to use for SSH_ASKPASS.

    The value is cached since this may be called many times.
    """
    global _executable_path
    if _executable_path is None:
        for path in ASKPASS_PATHS:
            if os.access(path, os.X_OK):
                _executable_path = path
                break
        else:
            _executable_path = ''
            sys.stderr.write(textwrap.fill("Warning: could not find an"
                    " executable path for askpass because PSSH was not"
                    " installed correctly.  Password prompts will not work."))
            sys.stderr.write('\n')
    return _executable_path

def password_client():
    """Connects to pssh over the socket specified at PSSH_ASKPASS_SOCKET."""
    address = os.getenv('PSSH_ASKPASS_SOCKET')
    if not address:
        sys.stderr.write(textwrap.fill("Permission denied.  Please create"
                " SSH keys or use the -A option to provide a password."))
        sys.stderr.write('\n')
        sys.exit(1)

    sock = socket.socket(socket.AF_UNIX)
    try:
        sock.connect(address)
    except socket.error:
        _, e, _ = sys.exc_info()
        number, message = e.args
        sys.stderr.write("Couldn't bind to %s: %s.\n" % (address, message))
        sys.exit(2)

    try:
        password = sock.makefile().read()
    except socket.error:
        sys.stderr.write("Socket error.\n")
        sys.exit(3)

    print(password)


if __name__ == '__main__':
    password_client()
