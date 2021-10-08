import os
import pickle
from urllib.parse import urlparse
from ..attrdict import CaseInsensitiveDict
import sys
import json
import re

class API:
  def __init__ (self, resource_id):
    self.resource_id = resource_id
    self.endpoints = set ()
    self.routeopt = {}
    self.parameter_requirements = {}
    self.auth_requirements = []
    self.doc = None
    self.METHODS = {}
    self.out = None

  VALID_METHODS = ('GET', 'POST', 'PATCH', 'PUT', 'DELETE')
  def add_call (self, method, url, status_code, reason, reqh, reqd, resh, resd, spec):
    from aquests.protocols.http import http_util

    if not self.endpoints:
      self.routeopt = spec ["routeopt"]
      self.parameter_requirements = spec ["parameter_requirements"]
      self.auth_requirements = spec ["auth_requirements"]
      self.doc = spec ["doc"]
      for each in self.routeopt ['methods']:
        if each in self.VALID_METHODS:
          self.METHODS [each] = {}
    endpoint = self.get_endpoint (spec ['current_request']['uri'], spec ['routeopt']['route'])
    self.endpoints.add (endpoint)

    endpoint = self.get_endpoint (spec ['current_request']['uri'], spec ['routeopt']['route'])
    self.endpoints.add (endpoint)

    if method in self.METHODS:
      reqh = CaseInsensitiveDict (reqh)
      if status_code not in self.METHODS [method]:
        self.METHODS [method][status_code] = []
      if isinstance (reqd, str):
        if reqh.get ('content-type', '').startswith ('application/json'):
          reqd = json.loads (reqd)
        else:
          reqd = http_util.crack_query (reqd)

      reqd = self.squeeze (reqd)
      resd = self.squeeze (resd)
      for d in self.METHODS [method][status_code]:
        if d [3] == reqd:
          return
        if set (d [3].keys ()) == set (reqd.keys ()):
          if d [5] == resd:
            return
        if method in ("GET", "DELETE") and d [0] == url:
          return
      self.METHODS [method][status_code].append ((url, reason, reqh, reqd, resh, resd, spec))

  def get_endpoint (self, endpoint, route):
    parts = urlparse (endpoint)
    a = parts.path.split ("/")
    if not route:
      return parts.path
    b = route.split ("/")
    if b [-1].startswith ("<path:"):
      s = parts.path.rfind ("/".join (b [:-1]))
      return parts.path [:-s] + route
    else:
      return "/".join (a [:-(len (b) - 1)] + b [1:])

  def squeeze (self, d):
    if isinstance (d, dict):
      d_ = {}
      for k, v in list (d.items ()):
        if isinstance (v, (dict, list, str)):
          d_ [k] = self.squeeze (v)
        else:
          d_ [k] = v
      return d_
    elif isinstance (d, list):
      d_ = []
      for each in d:
        d_.append (self.squeeze (each))
      return d_
    elif isinstance (d, str) and len (d) > 80:
      return d [:77] + '...'
    return d

  def to_dict (self, d):
    return crack_query.crack_query (d)

  def write (self, d):
    self.out and self.out.write (d)

  def writeln (self, line = ''):
    self.write (line + '  \n')

  def writebl (self, data, code = 'json'):
    self.write ("\n```{}\n{}\n```\n\n".format (code, data))

  def writep (self, line = ''):
    self.write (line + '\n\n')

  def chiplist (self, l):
    return "`{}`".format ("`, `".join (sorted (l)))

  def argslist (self, part):
    if not self.parameter_requirements.get (part):
      return
    requirements = self.parameter_requirements [part]
    alls = {}
    for param, cond in requirements.items ():
      if isinstance (cond, list) and param.find ('__') == -1:
        for each in cond:
          if param not in alls:
            alls [each] = []
          alls [each].append (param [:-1])

      else:
        parts = param.split ('__')
        param = parts [0]
        if param not in alls:
          alls [param] = []

        if isinstance (cond, (list, tuple)):
          cond = "|".join (map (str, cond))

        if len (parts) == 1:
          if hasattr (cond, 'pattern'):
            alls [param].append ('pattern `{}`'.format (cond.pattern))
          else:
            alls [param].append (cond)
          continue

        if len (parts) == 3:
          alls [param].append ('{} `{}`'.format (parts [1], cond))
          continue

        op = parts [1]
        alls [param].append ('{} `{}`'.format (op, cond))

    self.writeln ("**{}Parameters Requirements Detail**:".format (part != 'ARGS' and part + ' ' or ''))
    for name, reqs in alls.items ():
      self.writeln ("  - {}: {}".format (name, ", ".join (reqs)))

  def render (self, out):
    self.out = out
    self.writep ('## {}'.format (self.resource_id))
    if self.doc:
      self.writep (self.doc)
    # self.writep ("**Methods Allowed**: {}".format (self.chiplist (self.routeopt ['methods'])))

    if self.routeopt.get ('urlargs'):
      self.writeln ("**URL Parameters**: {}".format (self.chiplist (self.routeopt ['args'][:self.routeopt ['urlargs']])))

    qss = self.parameter_requirements.get ("ARGS", {}).get ('required', [])
    if not qss:
      qss = self.routeopt ['args'][self.routeopt.get ('urlargs', 0):]
    if qss:
      self.writeln ("**Common Parameters**:")
      defaults = self.routeopt.get ('defaults', {})
      for arg in qss:
        if arg in defaults:
          if defaults [arg]:
            need = "optional, default: {}".format (defaults [arg])
          else:
            need = "optional".format ()
        else:
          need = "required"
        self.writeln ("  - {} (*{}*)".format (arg, need))
    self.writeln ()

    self.argslist ('ARGS')
    self.writeln ()

    auth = 'NO'
    perms = []
    testpass = None
    login = False
    for t, d in self.auth_requirements:
      if t == "permission":
        if auth == 'NO':
          auth = "YES"
        perms = d or []
      elif t == "login":
        login = True
      elif t == "testpass":
        testpass = d
      elif t == "auth":
        auth = d

    auth and self.writeln ("**Authorization Required**: {}".format (auth))
    perms and self.writeln ("**Permission Required**: {}".format (self.chiplist (perms)))
    testpass and self.writeln ("**Test Pass Required**: `{}`".format (testpass))
    login and self.writeln ("**Login Required**: YES")
    self.writeln ()
    #{'methods': ['OPTIONS', 'GET', 'DELETE'], 'route': '/<name>', 'args': ['name', 'where'], 'defaults': {'where': 'latest'}, 'urlargs': 1}
    for method in self.VALID_METHODS:
      if method not in self.METHODS:
        continue
      if not self.METHODS [method]:
        continue

      self.writep ("#### `{}` {}".format (method, self.chiplist (list (self.endpoints))))
      if method in ("POST", "PUT", "PATCH"):
        self.argslist ('JSON')
        self.argslist ('FORM')
      else:
        self.argslist ('URL')
      self.writeln ()

      idx = [0, 0]
      for status_code in sorted (self.METHODS [method].keys ()):
        for url, reason, reqh, reqd, resh, resd, spec in self.METHODS [method][status_code]:
          if 200 <= status_code < 300:
            idx [0] += 1
            if idx [0] >= 3:
              continue
            self.writep ("**Success Response Example**")
            self.writeln ("> **_URL_**: `{}`".format (spec ["current_request"]['uri']))
            if reqd:
              self.writeln ("> **_Request Data_** ({})".format (reqh.get ('content-type')))
              self.writebl (json.dumps (reqd, ensure_ascii = False, indent = 2))
            self.writeln ()
            self.writeln ("> **_Response_**: `{} {}`".format (status_code, reason))
            if resd:
              self.writeln ("> **_Response Data_** ({})".format (resh.get ('content-type')))
              self.writebl (json.dumps (resd, ensure_ascii = False, indent = 2))

          else:
            idx [1] += 1
            self.writep ("**Error Response Example**")
            self.writeln ("> **_Response_**: `{} {}`".format (status_code, reason))
            if resh.get ('content-type'):
              self.writeln ("> **_Response Data_** ({})".format (resh.get ('content-type')))
            if resd:
              self.writebl (json.dumps (resd, ensure_ascii = False, indent = 2))

          self.writeln ()

RX_ALNUM = re.compile ('[^_a-zA-Z0-9]')
apis = {}
def build_doc ():
  if not os.path.isdir (".webtest_log/v"):
    sys.stdout.writep ("apidoc.build_doc: no log directory, skipped.")
    return

  for fn in os.listdir (".webtest_log/v"):
    try:
      with open (os.path.join (".webtest_log/v", fn), 'rb') as f:
        method, url, status_code, reason, reqh, reqd, resh, resd, spec = pickle.load (f)
    except EOFError:
      continue

    if not spec:
      continue
    resource_id = spec ['id']
    if resource_id not in apis:
      apis [resource_id] = API (resource_id)
    apis [resource_id].add_call (method.upper (), url, status_code, reason, reqh, reqd, resh, resd, spec)

  with sys.stdout as out:
    out.write ("## Table of Content\n\n")
    sorted_apis = sorted (apis.items (), key = lambda x: sorted (list (x [1].endpoints))[0])
    for idx, (resource_id, api) in enumerate (sorted_apis):
      end_points = " | ".join (list (api.endpoints)).replace ("<", "&lt;").replace (">", "&gt;")
      out.write ("1. [{}](#{})".format (end_points, resource_id.replace (".", "").lower ()))
      for method in API.VALID_METHODS:
        if not api.METHODS.get (method):
          continue
        out.write (" [**`{}`**](#{}-{})".format (method, method.lower (), RX_ALNUM.sub ('', api.chiplist (list (api.endpoints))).lower ()))
      out.write ("\n")

    for resource_id, api in sorted_apis:
      api.render (out)
      out.write ("\n\n")

# logging spec -----------------------------------------------

def truncate_log_dir (remove_only = False):
  from .. import pathtool
  import shutil

  if os.path.isdir (".webtest_log/v"):
      shutil.rmtree (".webtest_log/v")
  if remove_only:
      return
  pathtool.mkdir (".webtest_log/v")

SPECS = 0
if os.path.isdir (".webtest_log/v"):
  for fn in os.listdir (".webtest_log/v"):
    SPECS = max (SPECS, int (fn [:-5]))

def log_spec (method, url, status_code, reason, reqh, reqd, resh, resd):
    global SPECS

    try:
        spec = resd.pop ("__spec__")
    except (AttributeError, KeyError):
        return
    if not os.path.isdir (".webtest_log/v"):
      return
    if SPECS > 1000:
      truncate_log_dir ()
      SPECS = 0
    SPECS += 1

    resd_ = {}; resd_.update (resd) # convert to native dict
    with open (os.path.join (".webtest_log/v", '{:04d}.spec'.format (SPECS)), 'wb') as f:
        pickle.dump ((method, url, status_code, reason, reqh, reqd, resh, resd_, spec), f)
