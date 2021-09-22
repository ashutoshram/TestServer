import socket, struct
import subprocess
import os

def get_mac (iname):
    import fcntl
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', iname [:15].encode ("utf8")))
    return ':'.join(['%02x' % hex for hex in info[18:24]])

def get_ip ():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_hwid():
    if os.name == 'nt':
        return subprocess.check_output('wmic csproduct get uuid'.split()).decode ().split ()[-1]
    else:
        return subprocess.check_output('cat /sys/class/dmi/id/product_uuid'.split()).decode ().strip ()
    