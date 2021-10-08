
from hashlib import md5
import math
import time


def _get_otp (now, serial, delta):
    return md5 (str (round (now + delta - serial, -1)).encode ()).hexdigest ()

def generate (salt, delta = 0): # delta is for test
    serial = int (md5 (str (salt).encode ()).hexdigest ()[-8:], 16)
    return _get_otp (time.time (), serial, delta)

def verify (otp, salt):
    now = time.time ()
    serial = int (md5 (str (salt).encode ()).hexdigest ()[-8:], 16)
    for delta in (0, 10, -10, 20, -20):
        v = _get_otp (now, serial, delta)
        if otp == v:
            return v
    return False
