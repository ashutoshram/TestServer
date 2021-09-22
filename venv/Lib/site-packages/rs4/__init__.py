# 2016. 1. 10 by Hans Roh hansroh@gmail.com

__version__ = "0.2.29"
version_info = tuple (map (lambda x: not x.isdigit () and x or int (x),  __version__.split (".")))
from multiprocessing import Pool
from tqdm import tqdm as tqdm_
import concurrent.futures
from colorama import Fore
import functools
from .termcolor import tc
import subprocess as subprocess_
import asyncio as asyncio_
from asyncio.tasks import Task
import requests
from io import IOBase
from datetime import timezone, datetime, date
import time
import sys
if sys.version_info >= (3, 5):
    from .aio import aio

# for lower version compatibles -------------
from . import annotations as versioning
deco = versioning
class udict: pass
# end of compatibles -------------------------

# abbreviations ----------------------------------------------------
def tqdm (iterable, desc = "", color = None, **karg):
    if color:
        return tqdm_ (iterable, desc, bar_format = "{l_bar}%s{bar}%s{r_bar}" % (getattr (Fore, color.upper ()), Fore.RESET), **karg)
    else:
        return tqdm_ (iterable, desc, **karg)

def tpool (workers = 1):
    return concurrent.futures.ThreadPoolExecutor (max_workers = workers)
thread_pool = threading = tpool

def ppool (workers = 1, loky = False):
    return concurrent.futures.ProcessPoolExecutor (max_workers = workers)
process_pool = processing = ppool

def ppool2 (workers = 1):
    return Pool (workers)
process_pool2 = processing2 = ppool2

def subprocessing (cmd_or_func, *args):
    if isinstance (cmd_or_func, (list, tuple, str)):
        res = subprocess_.run (cmd_or_func, shell = True, stdout = subprocess_.PIPE, stderr = subprocess_.PIPE)
        out, err = res.stdout.decode ("utf8"), res.stderr.decode ("utf8")
        if err:
            raise RuntimeError (err)
        return out

    with Pool (1) as p:
        return p.apply (cmd_or_func, args)

def waitf (futures, timeout = None):
    if not futures:
        return [], []
    # wait Futures or async Tasks
    if isinstance (futures [0], Task):
        return aio.wait (futures, timeout = timeout)
    else:
        return concurrent.futures.wait (futures, timeout = timeout)

def wait (futures, timeout = None):
    dones, undones = waitf (futures)
    return timeout is None and dones or (dones, undones)

def as_completed (futures):
    if not futures:
        return []
    return concurrent.futures.as_completed (futures)


TZ_LOCAL = datetime.now (timezone.utc).astimezone().tzinfo
TZ_UTC = timezone.utc

def encodeutc (obj):
    return obj.astimezone (TZ_UTC).strftime ('%Y-%m-%d %H:%M:%S+00')

def decodeutc (s):
    return datetime (*(time.strptime (s, '%Y-%m-%d %H:%M:%S+00')) [:6]).astimezone (TZ_UTC)


class partial:
    def __init__ (self, *args, **kargs):
        self.__func = functools.partial (*args, **kargs)

    def __call__ (self, *args, **kargs):
        return self.__func (*args, **kargs)

    def __enter__ (self):
        return self.__func

    def __exit__ (self, *args):
        pass

class stub:
    def __init__ (self, uri = '', **kargs):
        assert 'data' not in kargs and 'files' not in kargs, 'data and files parameters are not allowed'
        self.__kargs = kargs
        self.__baseurl = uri
        while self.__baseurl:
            if self.__baseurl [-1] == '/':
                self.__baseurl = self.__baseurl [:-1]
            else:
                break
        self.__session = requests.Session ()

    def __enter__ (self):
        return self

    def __exit__ (self, *args):
        pass

    def __getattr__ (self, name):
        self.__method = name == 'upload' and 'post' or name
        return self.__proceed

    def __proceed (self, uri, *urlparams, **params):
        uri = self.__baseurl + uri

        __data__ = {}
        if urlparams:
            if isinstance (urlparams [-1], dict):
                __data__, urlparams = urlparams [-1], urlparams [:-1]
            uri = uri.format (*urlparams)
        __data__.update (params)

        if self.__method not in ('post', 'put', 'patch'):
            return getattr (self.__session, self.__method) (uri, **self.__kargs)

        __files__ = {}
        for k in list (__data__.keys ()):
            if isinstance (__data__ [k], IOBase):
                __files__ [k] = __data__.pop (k)

        return getattr (self.__session, self.__method) (uri, data = __data__ or None, files = __files__ or None, **self.__kargs)
