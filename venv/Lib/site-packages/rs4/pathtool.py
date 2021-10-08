import os
import re
import glob
import types
import sys
from setuptools.command.easy_install import easy_install
import zipfile
from shutil import rmtree, move, copyfile, copy, copytree

try:
	import urllib.parse
	unquote = urllib.parse.unquote
except ImportError:
	import urlparse
	unquote = urlparse.unquote

def remove (d):
	targets = glob.glob (d)
	if not targets: return

	for path in targets:
		if os.path.isdir (path):
			remove_silent (os.path.join (path, "*"))
			try: os.rmdir (path)
			except: pass
			continue
		os.remove (path)

def mkdir (tdir, mod = 0o755):
	tdir = os.path.abspath (tdir)
	while tdir:
		if tdir [-1] in ("\\/"):
			tdir = tdir [:-1]
		else:
			break

	if os.path.isdir (tdir): return
	chain = [tdir]
	while 1:
		tdir, last = os.path.split (tdir)
		if not last:
			break
		if tdir:
			chain.insert (0, tdir)

	for dir in chain [1:]:
		if os.path.isdir (dir):
			continue
		os.mkdir (dir)
		if os.name == "posix":
			os.chmod (dir, mod)

def modpath (mod_name):
	if type (mod_name) in (str, bytes):
		try:
				mod = sys.modules [mod_name]
		except KeyError:
			return "", ""
		return mod.__name__, mod.__file__

class easy_install_default(easy_install):
	def __init__(self):
		from distutils.dist import Distribution
		self.distribution = Distribution()
		self.initialize_options()

def get_package_dir ():
	e = easy_install_default()
	try: e.finalize_options()
	except: pass
	return e.install_dir


NAFN = re.compile (r"[\\/:*?\"<>|]+")
def mkfn (text):
	text = unquote (text)
	return NAFN.sub ("_", text)

def zipdir (zip_path, target_path):
	def _zipdir (path, zipf):
		removable = len (path) + 1
		for root, dirs, files in os.walk (path):
			for file in files:
				fullpath = os.path.join (root, file)
				zipf.write (fullpath, fullpath [removable:])
	with zipfile.ZipFile (zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
		_zipdir (target_path, zipf)

def unzipdir (zip_path, target_path = '.'):
	mkdir (target_path)
	with zipfile.ZipFile (zip_path) as zipf:
		for f in zipf.namelist ():
			fullpath = os.path.join (target_path, f)
			directory = os.path.dirname (fullpath)
			if not os.path.isdir (directory):
				mkdir (directory)
			zipf.extract (f, target_path)

def uploadzip (url, fn, **data):
	import requests
	parts = os.path.basename (fn).split ('.')
	assert len (parts) == 2, 'Zip filename must have single dot'
	return requests.post (url, data = data, files = {parts [0]: open (fn, 'rb')})


class FlashFile (str):
    def __new__(cls, *args, **kw):
        return str.__new__(cls, *args, **kw)

    def __enter__ (self):
        return self

    def __exit__ (self, type, value, tb):
        self.__remove ()

    def __remove (self):
        os.path.isfile (self) and os.remove (self)

def flashfile (name):
	return FlashFile (name)
