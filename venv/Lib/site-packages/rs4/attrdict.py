from collections import abc as collections_abc
import collections
import threading
import time

class AttrDict (dict):
	def __init__(self, *args, **kwargs):
		super(AttrDict, self).__init__(*args, **kwargs)
		self.__dict__ = self


class AttrDictTS:
	def __init__ (self, d = {}):
		self.__d = d
		self.__lock = threading.RLock ()

	def __setattr__ (self, k, v):
		if k.startswith ("_AttrDictTS__"):
			self.__dict__ [k] = v
			return
		else:
			self.set (k, v)

	def __getattr__ (self, k):
		if k.startswith ("_AttrDictTS__"):
			return self.__dict__ [k]
		else:
			return self [k]

	def __delattr__ (self, k):
		self.remove (k)

	def __len__ (self):
		return len (self.__d)

	def __contains__ (self, k):
		with self.__lock:
			return k in self.__d

	def __setitem__ (self, k, v):
		self.set (k, v)

	def __getitem__ (self, k):
		if k not in self:
			raise KeyError
		return self.get (k)

	def __delitem__ (self, k):
		self.remove (k)

	def set (self, k, v, timeout = 0):
		with self.__lock:
			self.__d [k] = (v, timeout and time.time () + timeout or 0)

	def get (self, k, d = None):
		with self.__lock:
			try: v, expires = self.__d [k]
			except KeyError: return d
		if expires and time.time () >= expires:
			self.remove (k)
			return d
		return v

	def clear (self):
		with self.__lock:
			self.__d = {}

	def remove (self, k):
		with self.__lock:
			try:
				self.__d.pop (k)
			except KeyError:
				pass

	def keys (self):
		with self.__lock:
			return self.__d.keys ()

	def values (self):
		with self.__lock:
			return self.__d.values ()

	def items (self):
		with self.__lock:
			return self.__d.items ()


class CaseInsensitiveKey(object):
	def __init__(self, key):
		self.key = key

	def __hash__(self):
		return hash(self.key.lower())

	def __eq__(self, other):
		return self.key.lower() == other.key.lower()

	def __str__(self):
		return self.key

	def __repr__(self):
		return self.key

	def __getattr__ (self, name):
		return getattr (self.key, name)

# memory leaking?
class NocaseDict(dict):
	def __setitem__(self, key, value):
		key = CaseInsensitiveKey(key)
		super(NocaseDict, self).__setitem__(key, value)

	def __getitem__(self, key):
		key = CaseInsensitiveKey(key)
		return super(NocaseDict, self).__getitem__(key)


class CaseInsensitiveDict(collections_abc.MutableMapping):
	def __init__(self, data=None, **kwargs):
		self._store = collections.OrderedDict()
		if data is None:
			data = {}
		self.update(data, **kwargs)

	def __setitem__(self, key, value):
		# Use the lowercased key for lookups, but store the actual
		# key alongside the value.
		self._store[key.lower()] = (key, value)

	def __getitem__(self, key):
		return self._store[key.lower()][1]

	def __delitem__(self, key):
		del self._store[key.lower()]

	def __iter__(self):
		return (casedkey for casedkey, mappedvalue in self._store.values())

	def __len__(self):
		return len(self._store)

	def lower_items(self):
		"""Like iteritems(), but with all lowercase keys."""
		return (
			(lowerkey, keyval[1])
			for (lowerkey, keyval)
			in self._store.items()
		)

	def __eq__(self, other):
		if isinstance(other, collections_abc.Mapping):
			other = CaseInsensitiveDict(other)
		else:
			return NotImplemented
		# Compare insensitively
		return dict(self.lower_items()) == dict(other.lower_items())

	# Copy is required
	def copy(self):
		return CaseInsensitiveDict(self._store.values())

	def __repr__(self):
		return str(dict(self.items()))


if __name__ == "__main__":
	a = AttrDict ()
	a ["a-s"] = 1
	print (a.a_s)
	a.x = 4
	print (a['x'])

	b = NocaseDict ()
	b ['Content-Length'] = 100
	print (b ['content-length'])