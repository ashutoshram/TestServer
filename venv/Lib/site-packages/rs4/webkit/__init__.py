
from ..annotations import Uninstalled
from .webtest import Target
from hashlib import md5

Site = Target


try:
    from .drivers import Chrome, Firefox, IE
except ModuleNotFoundError:
    IE = Firefox = Chrome = Uninstalled ('selenium')

try:
    from .nops import nops
except ModuleNotFoundError:
    nops = Uninstalled ('cssselect==0.9.1, lxml==4.4.0 and html5lib==0.999999999')
