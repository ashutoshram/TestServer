"""
2015. 12. 10
Hans Roh
"""

__version__ = "0.9.0.0"

version_info = tuple (map (lambda x: not x.isdigit () and x or int (x),  __version__.split (".")))
assert len ([x for  x in version_info [:2] if isinstance (x, int)]) == 2, 'major and minor version should be integer'

from .patches import skitaipatch
from .Atila import Atila

def load (target, pref = None):
    from rs4 import importer
    import os, copy

    def init_app (directory, pref):
        modinit = os.path.join (directory, "__init__.py")
        if os.path.isfile (modinit):
            mod = importer.from_file ("temp", modinit)
            initer = None
            if hasattr (mod, "__setup__"):
                initer = mod.__setup__
            elif hasattr (mod, "bootstrap"):
                initer = mod.bootstrap (pref)
            initer and initer (pref)

    if hasattr (target, "__file__"):
        directory = os.path.abspath (os.path.join (os.path.dirname (target.__file__), "export", "skitai"))
        module, abspath = importer.importer (directory, "__export__")
    else:
        directory, script = os.path.split (target)
        module, abspath = importer.importer (directory, script [-3:] == ".py" and script [:-3] or script)

    if pref:
        init_app (directory, pref)
        app = module.app
        for k, v in copy.copy (pref).items ():
            if k == "config":
                if not hasattr (app, 'config'):
                    app.config = v
                else:
                    for k, v in copy.copy (pref.config).items ():
                       app.config [k] = v
            else:
                setattr (app, k, v)

    return app
