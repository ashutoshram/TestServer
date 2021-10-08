# pytest framework ---------------------------------------------
import requests
from . import siesta
from .. import attrdict
import time
import sys
import os
import xmlrpc.client
from io import IOBase
import json
from . import apidoc
from urllib.parse import urlparse, quote
from aquests.protocols.http2.hyper import HTTPConnection

has_http3 = False
if os.name != 'nt' and sys.version_info >= (3, 6):
    try:
        from aquests.protocols.http3 import client as h3client
        from aquests.protocols.http3 import requests as h3requests
    except ImportError:
        pass
    else:
        has_http3 = True


class Stub:
    def __init__ (self, cli, baseurl, headers = None, auth = None):
        self._cli = cli
        self._headers = headers
        self._auth = auth
        self._baseurl = self.norm_baseurl (baseurl)

    def __enter__ (self):
        return self

    def __exit__ (self, *args):
        pass

    def __getattr__ (self, name):
        self._method = name
        return self.__proceed

    def __proceed (self, uri, *urlparams, **params):
        __data__ = {}
        if urlparams:
            if isinstance (urlparams [-1], dict):
                __data__, urlparams = urlparams [-1], urlparams [:-1]
            uri = uri.format (*urlparams)
        __data__.update (params)
        uri = self._baseurl + uri
        return self.handle_request (uri, __data__)

    def norm_baseurl (self, uri):
        uri = uri != '/' and uri or ''
        while uri:
            if uri [-1] == '/':
                uri = uri [:-1]
            else:
                break
        return uri

    def handle_request (self, uri, data):
        if self._method in ('post', 'put', 'patch', 'upload'):
            return getattr (self._cli, self._method) (uri, __data__, headers = self._headers, auth = self._auth)
        else:
            return getattr (self._cli, self._method) (uri, headers = self._headers, auth = self._auth)



class HTTP2Response:
    def __init__ (self, r):
        self.headers = self._rebuild_headers (r.headers)
        self.events = r.events
        self.status_code = r.status
        self.reason =  r.reason
        self.content = r.read ()

    def _rebuild_headers (self, headers):
        headers_ = attrdict.CaseInsensitiveDict ()
        for k, v in headers.items ():
            headers_ [k.decode ()] = v.decode ()
        return headers_

    @property
    def text (self):
        return self.content.decode ()

    def json (self):
        json.loads (self.text)

    def get_pushes (self):
        self.conn.get_pushes ()


class HTTP2:
    def __init__ (self, endpoint):
        self.endpoint = endpoint
        parts = urlparse (self.endpoint)
        self.conn = HTTPConnection(parts.netloc, enable_push = True, secure=parts.scheme == 'https')

    def urlencode (self, params, to_bytes = True):
        fm = []
        for k, v in list(params.items ()):
            fm.append ("%s=%s" % (quote (k), quote (str (v))))
        if to_bytes:
            return "&".join (fm).encode ("utf8")
        return "&".join (fm)

    def _rebuild_header (self, headers_, data):
        headers_ = headers_ or {}
        headers = attrdict.CaseInsensitiveDict ()
        for k, v in headers_.items ():
            headers [k] = v
        if data and headers.get ('content-type') is None:
            headers ['Content-Type'] = 'application/x-www-form-urlencoded'
        return headers

    def _request (self, method, url, data = None, headers = None):
        headers = self._rebuild_header (headers, data)
        if data:
            data = self.urlencode (data)
        self.conn.request (method.upper (), url, data, headers)
        return HTTP2Response (self.conn.get_response())

    def get (self, url, headers = {}):
        return self._request ('GET', url, headers = headers)

    def post (self, url, data, headers = {}):
        return self._request ('POST', url, data, headers)


class HTTP3Response (HTTP2Response):
    def __init__ (self, r):
        self.headers = self._rebuild_headers (r.headers)
        try:
            self.status_code = int (self.headers.get (':status'))
        except TypeError:
            raise h3client.ConnectionClosed
        self.reason = ''
        self.content = r.data
        self.events = r.events
        self._promises = r.promises

    def get_pushes (self):
        class Promise:
            def __init__ (self, headers):
                self.path = headers.get (':path').encode ()
        return [Promise (headers) for headers in self._promises]


class HTTP3 (HTTP2):
    def __init__ (self, endpoint):
        self.endpoint = endpoint
        parts = urlparse (self.endpoint)
        self.conn = h3client.Connection (parts.netloc)

    def _request (self, method, url, data = None, headers = None):
        headers = self._rebuild_header (headers, data)
        if data:
            data = self.urlencode (data)
        resp = self.conn.request (method.upper (), url, data, headers)
        return HTTP3Response (resp)

    def MultiCall (self):
        return h3requests.MultiCall (self.endpoint)

class Target:
    # f = Target ('http://localhost:')
    # f.get ("/v1/accounts/me") == f.http.get ("/v1/accounts/me")
    # f.axios.get ("/v1/accounts/me")
    # f.stub.v1.accounts ("me").get ()
    # f.driver.navigate ('/')

    def __init__ (self, endpoint, api_call = False, session = None, temp_dir = None):
        self.endpoint = endpoint
        self.temp_dir = temp_dir
        self.s = session or requests.Session ()
        self._api_call = api_call
        self._headers = {}
        if not self._api_call:
            self.axios = Target (endpoint, True, session = self.s)
        else:
            self.set_default_header ('Accept', "application/json")
            self.set_default_header ('Content-Type', "application/json")
        self.siesta = siesta.API (endpoint, reraise_http_error = False, session = self.s)
        self._driver = None
        self.http2 = HTTP2 (endpoint)
        self.http3 = has_http3 and HTTP3 (endpoint) or None

    @property
    def http (self):
        return self

    @property
    def driver (self):
        if self._driver:
            return self._driver

        from rs4.webkit import Chrome
        ENDPOINT = self.endpoint
        TEMP_DIR = self.temp_dir
        class Chrome (Chrome):
            def navigate (self, url):
                return super ().navigate (ENDPOINT + url)

            def capture (self):
                super ().capture (os.path.join (TEMP_DIR, 'selenium.jpg'))

        self._driver = Chrome ("/usr/bin/chromedriver", headless = True)
        return self._driver

    def set_jwt (self, token = None):
        self.siesta._set_jwt (token)
        if self._api_call:
            self.set_default_header ('Authorization', "Bearer " + token)

    def sync (self):
        if self.driver:
            for cookie in self.driver.cookies:
                if 'httpOnly' in cookie:
                    httpO = cookie.pop('httpOnly')
                    cookie ['rest'] = {'httpOnly': httpO}
                if 'expiry' in cookie:
                    cookie ['expires'] = cookie.pop ('expiry')
                self.s.cookies.set (**cookie)

            for c in self.s.cookies:
                cookie = {'name': c.name, 'value': c.value, 'path': c.path}
                if cookie.get ('expires'):
                    cookie ['expiry'] = c ['expires']
                self.driver.add_cookie (cookie)

        return dict (
            cookies = [(c.name, c.value) for c in self.s.cookies]
        )

    def websocket (self, uri):
        from websocket import create_connection

        u = urlparse (self.endpoint)
        return create_connection ("ws://" + u.netloc + uri)

    def set_default_header (self, k, v):
        self._headers [k] = v

    def api (self, point = None):
        if point:
            return siesta.API (point, reraise_http_error = False, session = self.s)
        return self.siesta

    def __enter__ (self):
        return self

    def __exit__ (self, type, value, tb):
        self._close ()

    def __del__ (self):
        self._close ()

    def _close (self):
        pass

    def resolve (self, url):
        if url.startswith ("http://") or url.startswith ("https://"):
            return url
        else:
            return self.endpoint + url

    def _request (self, method, url, *args, **kargs):
        url = self.resolve (url)
        rf = getattr (self.s, method)
        if args:
            args = list (args)
            request_data = args.pop (0)
            args = tuple (args)
        else:
            try:
                request_data = kargs.pop ('data')
            except KeyError:
                request_data = None

        if 'headers' in kargs:
            headers = kargs.pop ('headers')
        else:
            headers = {}

        if hasattr (headers, 'append'):
            [ headers.append (h) for h in self._headers.items () ]
        else:
            headers.update (self._headers)

        if isinstance (request_data, dict) and self._api_call:
            request_data = json.dumps (request_data)

        if request_data:
            resp = rf (url, request_data, *args, headers = headers, **kargs)
        else:
            resp = rf (url, *args, headers = headers, **kargs)

        if resp.headers.get ('content-type', '').startswith ('application/json'):
            try:
                resp.data = resp.json ()
            except:
                resp.data = {}

            if "__spec__" in resp.data:
                reqh = kargs.get ('headers', {})
                reqh.update (self.s.headers)
                apidoc.log_spec (method.upper (), url, resp.status_code, resp.reason, reqh, request_data, resp.headers, resp.data)
        else:
            resp.data = resp.content
        return resp

    def get (self, url, *args, **karg):
        return self._request ('get', url, *args, **karg)

    def post (self, url, *args, **karg):
        return self._request ('post', url, *args, **karg)

    def upload (self, url, data, **karg):
        files = {}
        for k in list (data.keys ()):
            if isinstance (data [k], IOBase):
                files [k] = data.pop (k)
        return self._request ('post', url, files = files, data = data, **karg)

    def put (self, url, *args, **karg):
        return self._request ('put', url, *args, **karg)

    def patch (self, url, *args, **karg):
        return self._request ('patch', url, *args, **karg)

    def delete (self, url, *args, **karg):
        return self._request ('delete', url, *args, **karg)

    def head (self, url, *args, **karg):
        return self._request ('head', url, *args, **karg)

    def options (self, url, *args, **karg):
        return self._request ('options', url, *args, **karg)

    def stub (self, baseurl = '', *args, **kargs):
        return Stub (self.axios, baseurl, *args, **kargs)

    def rpc (self, url, proxy_class = None):
        return (proxy_class or xmlrpc.client.ServerProxy) (self.resolve (url))
    xmlrpc = rpc

    def jsonrpc (self, url, proxy_class = None):
        import jsonrpclib
        return (proxy_class or jsonrpclib.ServerProxy) (self.resolve (url))

    def grpc (self, url, proxy_class = None):
        raise NotImplementedError


if __name__ == "__main__":
    if "--init" in sys.argv:
        apidoc.truncate_log_dir ()
    if "--make" in sys.argv:
        apidoc.build_doc ()
    if "--clean" in sys.argv:
        apidoc.truncate_log_dir (remove_only = True)


