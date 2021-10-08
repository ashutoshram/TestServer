import getopt as optparse
import sys
from .termcolor import tc
import math

helps = []
long_opts = ['help']
short_opts = []
aliases = {}
defaults = {}

def usage (exit = False):
    maxlen = max ([len (opt) + 2 for opt, desc in helps]) + 1
    print ("\nMandatory arguments to long options are mandatory for short options too.")
    for opt, desc in helps:
        if '---' in opt:
            color = tc.red
        else:
            color = tc.white
        spaces = maxlen - (len (opt) + 1)
        line = ('  {}{}{}'.format (color (opt), ' ' * spaces, desc))
        print (line)
    exit and sys.exit ()

def add_option (sname = None, lname = None, desc = None, default = None):
    global long_opts, short_opts, aliases, defaults

    sval, lval = None, None
    if lname:
        if lname.startswith ("--"):
            lname = lname [2:]
        try: lname, lval = lname.split ("=", 1)
        except ValueError: pass
        if lname in long_opts:
            return
        long_opts.append (lname + (lval is not None and "=" or ''))

    if sname:
        if sname.startswith ("-"):
            sname = sname [1:]
        try:
            sname, sval = sname.split ("=", 1)
        except ValueError:
            pass
        if sname in short_opts:
            return
        short_opts.append (sname + (sval is not None and ":" or ''))

    if (sname and lname) and ((sval is None and lval is not None) or (lval is None and sval is not None)):
        raise SystemError ('-{} and --{} spec not matched'.format (sname, lname))

    val = sval or lval
    if lname and sname:
        aliases ['--' + lname] = '-' + sname
        aliases ['-' + sname] = '--' + lname
        opt = "-{}, --{}".format (sname, lname)
    elif sname:
        opt = '-{}'.format (sname)
    elif lname:
        opt = '    --{}'.format (lname)
    if val:
        opt += '=' + val

    desc = desc or ''
    if default:
        if sname:
            defaults ['-' + sname] = default
        if lname:
            defaults ['--' + lname] = default
        if desc:
            desc += ' (default={})'.format (default)
        else:
            desc += 'default={}'.format (default)
    helps.append ((opt, desc))

def add_options (*names):
    for name in names:
        assert name and name [0] == "-"
        if name.startswith ("--"):
            add_option (None, name [2:])
        else:
            add_option (name [1:])

class ArgumentOptions:
    def __init__ (self, kopt = {}, argv = []):
        self.__kopt = kopt
        self.argv = argv

    def __str__ (self):
        return str (list (self.items ()))

    def __contains__ (self, k):
        return k in self.__kopt

    def items (self):
        return self.__kopt.items ()

    def get (self, k, v = None):
        global aliases, defaults
        if v is None:
            v = defaults.get (k)
        try:
            val = self.__kopt [k]
        except KeyError:
            if k in aliases:
                k2 = aliases [k]
                val = self.__kopt.get (k2, v)
            else:
                return v
        if isinstance (v, int):
            val = int (val)
        elif isinstance (v, float):
            val = float (val)
        return val

    def set (self, k, v = None):
        self.__kopt [k] = v

    def remove (self, k):
        try:
            del self.__kopt [k]
        except KeyError:
            pass

def collect ():
    global long_opts, short_opts
    argopt = optparse.getopt (sys.argv [1:], "".join (short_opts).replace ("=", ":"), long_opts)
    kopts_ = {}
    for k, v in argopt [0]:
        if k in kopts_:
            if not isinstance (kopts_ [k], list):
                kopts_ [k] = {kopts_ [k]}
            kopts_ [k].add (v)
        else:
            kopts_ [k] = v
    return ArgumentOptions (kopts_, argopt [1])
options = collect
