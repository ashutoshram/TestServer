import os
import sys

if os.name == "nt":
    from colorama import init
    init()

def stty_size ():
    size = list (map (int, os.popen('stty size', 'r').read().split()))
    size.reverse ()
    return size

class tc:
    WHITE = '\033[97m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    OKBLUE = '\033[94m'
    WARNING = '\033[93m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    GREY = '\033[90m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'
    ISATTY = sys.stdout.isatty()

    @classmethod
    def _wrap (cls, s, c):
        return cls.ISATTY and "{}{}{}".format (c, s, cls.ENDC) or s

    @classmethod
    def default (cls, s):
        return s

    @classmethod
    def bold (cls, s):
        return cls._wrap (s, cls.BOLD)

    @classmethod
    def underline (cls, s):
        return cls._wrap (s, cls.UNDERLINE)
    u = underline

    @classmethod
    def grey (cls, s):
        return cls._wrap (s, cls.GREY)
    critical = fatal = grey

    @classmethod
    def greeen (cls, s):
        return cls._wrap (s, cls.OKGREEN)
    ok = info = greeen

    @classmethod
    def yellow (cls, s):
        return cls._wrap (s, cls.WARNING)
    warning = warn = yellow

    @classmethod
    def magenta (cls, s):
        return cls._wrap (s, cls.MAGENTA)
    expt = magenta

    @classmethod
    def cyan (cls, s):
        return cls._wrap (s, cls.CYAN)
    debug = secondary = fail = cyan

    @classmethod
    def red (cls, s):
        return cls._wrap (s, cls.FAIL)
    error = red

    @classmethod
    def white (cls, s):
        return cls._wrap (s, cls.WHITE)
    blah = echo = white

    @classmethod
    def blue (cls, s):
        return cls._wrap (s, cls.OKBLUE)
    primary = blue
