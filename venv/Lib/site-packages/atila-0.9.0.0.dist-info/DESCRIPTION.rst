Atila
===========

*Atila* is simple and minimal framework integrated with `Skitai App Engine`_.
It is the easiest way to make backend API services.

.. code:: python

  # serve.py

  import atila

  app = atila.Atila (__name__)

  @app.route ("/")
  def index (was):
    return "Hello, World"

  if __mame__ == "__main__":
    import skitai

    skitai.mount ("/", app)
    skitai.run (port = 5000)

And run,

.. code:: bash

  python3 serve.py

And you can see `Hello, World` at `http://localhost:5000`.

Here's a more practical example:

.. code:: python

  @app.route ("/<int:uid>/photos", methods = ["GET", "DELETE", "POST", "OPTIONS"])
  @app.permission_required ()
  def photos (was, uid, **DATA):
    uid = uid == "me" and was.request.JWT ["uid"] or uid

    with was.db ("@mydb") as db:
      if was.request.method == "GET":
        rows = db.select ("photo").filter (uid = uid).execute ().fetch ()
        return was.API (rows = rows) # [ {id: 1, ...}, ... ]

      elif was.request.method == "DELETE":
        db.delete ("photo").filter (uid = uid).execute ().commit ()
        return was.API ("205 No Content")

      elif was.request.method == "POST":
        if not DATA.get ("title"):
          raise was.Error ("400 Bad Request", "title required")
        DATA ["uid"] = uid
        row = db.insert ("photo").data (**DATA).returning ("id").execute ().one ()
        return was.API ("201 Created", id = row.id)

.. contents:: Table of Contents

.. _`Skitai App Engine`: https://pypi.org/project/skitai/


Important Notice
=======================

*CAUTION*: Atila is base on WSGI but can be run only
with `Skitai App Engine`_.

This means if you make your app with Atila, you have no
choice but Skitai as WSGI app server. And Atila's unique
and unconventional style may become very hard work to port
to other framework.

I am currently enjoying to develop both Skitai and Atila,
but no one can expect future.

So you should think twice before you decide to use this.


Installation
=========================

**Requirements**

Python 3.5+
PyPy3

**Installation**

Atila and other core base dependent libraries is developing on
single milestone, install/upgrade all please. Otherwise it is
highly possible to meet some errors.

With pip

.. code-block:: bash

    pip3 install -U atila

With git

.. code-block:: bash

    git clone https://gitlab.com/hansroh/atila.git
    cd atila
    pip3 install -e .


Core App Options
======================================

These are for later quick copying.

**Debug Options**

- debug = False
- use_reloader = False

**CORS Options**

- access_control_allow_origin = None: list of origin
- access_control_max_age = 0

**Session/Authenticating Options**

- authenticate = None: basic | digest | bearer
- securekey = None: string for encrypted session cookie
- session_timeout = None

**Sub Module Mount Options**

- enable_namespace = True

  *Default value has been changed in version 0.7: False -> True*

  If you didn't use this option with `True` under version 0.7 you
  may set `False` in version 0.7 for for compatiblity.

  Also DO NOT use this option with `False` if not for compatiblity
  reason.

- auto_mount

  *Deprecated in version 0.7*

  If you call app.mount () or pref.mount (), this option
  will be disabled automatically. Otherwise Atila try to mount
  automatically all sub modules has __mount__ ().


Default App Configuration
=====================================

Below configs are new in version *0.8*.

.. code:: python

  app.config.STATIC_URL = '/'
  app.config.MEDIA_URL = '/media/'
  app.config.MINIFY_HTML = None | 'strip' | 'minify'
  app.config.JSON_ENCODER = 'utcoffset'
  app.config.PRETTY_JSON = False # if True, 2 spaces indent format

To use minify feature, you must install 'css_html_js_minify'.

Note: below version 0.8, JSON_ENCODER works as app.config.JSON_ENCODER = 'str'
which is str (datetime) with system time zone. If you migrate to
above version 0.8 and you want keep this format, you shoud specify
app.config.JSON_ENCODER = 'str'.


App Examples
===========================

You can simply visit `Atila app example`_ for sightseeing.

.. _`Atila app example`: https://gitlab.com/hansroh/atila/tree/master/example


Atila with Skitai App Engine
====================================

Simple App
------------------

.. code:: python

  from atila import Atila
  app = Atila(__name__)

  ...

  @app.route ("/")
  def index (was):
    ...
    return was.response ("200 OK", ...)

  if __name__ == "__main__":
    import skitai

    with skitai.preference () as pref:
      pref.use_reloader = True
      skitai.mount ('/', './static')
      skitai.mount ('/', app, 'app', pref)

    skitai.run ()

If atila app exists seprated file:

.. code:: python

  # serve.py

  if __name__ == "__main__":
    import skitai

    with skitai.preference () as pref:
      pref.use_reloader = True
      skitai.mount ('/', './static')
      skitai.mount ('/', 'myapp/atila_app.py', pref = pref)
    skitai.run ()

Resource Structure For Larger App
-----------------------------------------------

If your app is simple, it can be made into single app.py
and templates and static directory.

.. code:: python

  from atila import Atila

  app = Atila(__name__)

  app.use_reloader = True
  app.debug = True

  @app.route ("/")
  def index (was):
    ...
    return was.response ("200 OK", ...)

  if __name__ == "__main__":
    import skitai

    with skitai.preference () as pref:
      pref.use_reloader = True
      skitai.mount ('/', './static')
      skitai.mount ('/', app, 'app', pref)
    skitai.run ()

And run,

.. code:: bash

  python3 app.py

But Your app is more bigger, it will be hard to make with single
app file. Then, you can make services directory to seperate your
app into several categories.

.. code:: bash

  myapp/
    app.py
    services/
    templates/
    resources/
    static/
  serve.py

All sub modules app need, can be placed into services/. services/\*.py
will be watched for reloading if use_reloader = True.

You can structuring any ways you like and I like this style:

.. code:: bash

  services/views.py
  services/apis.py
  services/helpers.py

All modules to mount to app in services, should have def __mount__ (app).

For example, views.py is like this,

.. code:: python

  from . import helpers

  def __mount__ (app):
    @app.route ("/")
    def index (was):
      ...
      return was.render ("index.html")

Now you just import app decorable moduels at your app.py,

.. code:: python

  from atila import Atila
  from services import views, apis

  app = Atila(__name__)

That's it.

If app scale is more bigger scale, services can be expanded to sub modules.

.. code:: bash

  services/views/index.py, regist.py, search.py, ...
  services/apis/codemap.py,
  services/helpers/utils.py, ...

And import these from app.py,

.. code:: python

  from services.views import index, regist, ...
  from services.apis import codemap, ...

Some more other informations will be mentioned at *Mounting Resources*
section again.

Finally, your server.py:

.. code:: python

  import skitai
  with skitai.preference () as pref:
    pref.use_reloader = True
    skitai.mount ('/', './static')
    skitai.mount ('/', 'myapp/app.py', 'app', pref)
  skitai.run ()

Also you can add myapp2, ... and mount them.


Request Hanlding with Atila
====================================

Runtime App Preference
-------------------------

**New in skitai version 0.26**

Usally, your app preference setting is like this:

.. code:: python

  from atila import Atila

  app = Atila(__name__)

  app.use_reloader = True
  app.debug = True
  app.config ["prefA"] = 1
  app.config ["prefB"] = 2

Skitai provide runtime preference setting.

.. code:: python

  import skitai

  with skitai.preference () as pref:
    pref.use_reloader = True
    pref.debug = True
    pref.config ["prefA"] = 1
    pref.config.prefB = 2
    skitai.mount ("/v1", "app_v1/app.py", "app", pref)
  skitai.run ()

Above pref's all properties will be overriden on your app.

Runtime preference can be used with skitai initializing or
complicated initializing process for your app.

You can create \_\_init\_\_.py at same directory with app.py. And
bootstrap () function is needed.

\_\_init\_\_.py

.. code:: python

  import skitai
  import atila

  def bootstrap (pref):
    skitai.register_states ('tbl.test')

    with open (pref.config.urlfile, "r") as f:
      pref.config.urllist = []
      while 1:
        line = f.readline ().strip ()
        if not line: break
        pref.config.urllist.append (line.split ("  ", 4))


More About Atila App Initialization
```````````````````````````````````````

*Note*: There'are two important things for app.\_\_init\_\_.

- add skitai.register_states () if you need state management.
  Inter process state sharing objects should be defined before
  running Skitai.


Access Atila App
------------------

You can access all Atila object from app.

- app.debug
- app.use_reloader
- app.config # use for custom configuration like
- app.config.my_setting = 1

- app.securekey
- app.session_timeout = None

- app.authorization = "digest"
- app.authenticate = False
- app.realm = None
- app.users = {}
- app.jinja_env

- app.build_url () is equal to was.urlfor ()

Currently app.config has these properties and you can
reconfig by setting new value:

- app.config.MAX_UPLOAD_SIZE = 256 * 1024 * 1024
- app.config.MEDIA_URL = '/media/'
- app.config.STATIC_URL = '/'
- app.config.MINIFY_HTML = False
- app.config.MAX_UPLOAD_SIZE = 256 * 1024 * 1024
- app.config.JSON_ENCODER = 'utcoffset'
- app.config.PRETTY_JSON = False


Debugging and Reloading App
-----------------------------

If debug is True, all errors even server errors is shown on
both web browser and console window, otherhwise shown only on console.

If use_reloader is True, Atila will detect file changes and reload
app automatically, otherwise app will never be reloaded.

.. code:: python

  from atila import Atila

  app = Atila (__name__)
  app.debug = True # output exception information
  app.use_reloader = True # auto realod on file changed


Hot Reloading
``````````````````````

Atila use hot reloading which need not restart worker process. It
use importlib.reload if detected file changing.

But it is recommended restart developing server forcely after significant
source changes or long-run.


Kill Switch
````````````````

Please see, `--devel`_ and `--silent`_ options of Skitai App Engine.

.. _`--devel`: https://pypi.org/project/skitai/#run-as-development-mode
.. _`--silent`: https://pypi.org/project/skitai/#run-as-silent-mode


Routing
----------

Basic routing is like this:

.. code:: python

  @app.route ("/hello")
  def hello_world (was):
    return was.render ("hello.htm")

For adding some restrictions:

.. code:: python

  @app.route ("/hello", methods = ["GET"], content_types = ["text/xml"])
  def hello_world (was):
    return was.render ("hello.htm")

And you can specifyt multiple routing,

.. code:: python

  @app.route ("/hello", mehotd = ["POST"])
  @app.route ("/")
  def hello_world (was):
    return was.render ("hello.htm")

If method is not GET, Atila will response http error code 405 (Method
Not Allowed), and content-type is not text/xml, 415 (Unsupported Content Type).

And here's a notalble routing rule.

.. code:: python

  @app.route ("")
  def hello_world (was):
    return was.render ("hello.htm")

This app is mounted to "/sub" on skitai, /sub URL is valid but
"/sub/" will return 404 code.

On the other hand,

.. code:: python

  @app.route ("/")
  def hello_world (was):
    return was.render ("hello.htm")

“/sub” will return 301 code for “/sub/” and “/sub/” is valid URL.


App and Request context
----------------------------------

- app.r is current request context namespace.
- app.g is global app context namespace.


Request
---------

Reqeust object provides these methods and attributes:

- was.request.method # upper case GET, POST, ...
- was.request.command # lower case get, post, ...
- was.request.uri
- was.request.version # HTTP Version, 1.0, 1.1, 2.0, 3.0
- was.request.scheme # http or https
- was.request.headers # case insensitive dictioanry
- was.request.body # bytes object
- was.request.args # dictionary merged with url, query string,
  form data and JSON
- was.request.routed # routed function
- was.request.routable # {'methods': ["POST", "OPTIONS"],
  'content_types': ["text/xml"], 'options': {...},  'mntopt': {...}}
- was.request.acceptables # {'text/html': {'q': '0.9'}}
- was.request.acceptable (media) # check if acceptable media type
  by given media
- was.request.split_uri () # (script, param, querystring, fragment)
- was.request.json () # decode request body from JSON
- was.request.form () # decode request body to dict
  if content-type is form data
- was.request.dict () # decode request body as dict
  if content-type is compatible with dict - form data or JSON
- was.request.get_header ("content-type") # case insensitive
- was.request.get_headers () # retrun header all list
- was.request.get_body ()
- was.request.get_scheme () # http or https
- was.request.get_remote_addr ()
- was.request.get_user_agent ()
- was.request.get_content_type ()
- was.request.get_main_type ()
- was.request.get_sub_type ()

Getting Parameters
---------------------

Atila parameters are comceptually seperated 3 groups: URL, query
string and body.

Below explaination may be a bit complicated but it is enough to
remember 3 things:

1. Atila resource parameters can be defined as function arguments
and use theses native Python function arguments.

2. Also you can access parameter groups by origin:

  - was.request.DEFAULT: default arguments of your resource
  - was.request.URL: url query string
  - was.request.FORM
  - was.request.JSON
  - was.request.DATA: automatically choosen one of was.request.FORM
    or was.request.JSON by content-type header of request
  - was.request.ARGS: eventaully was.request.ARGS contains all
    parameters of all origins including was.request.DEFAULT

Getting URL Parameters
`````````````````````````

URL Parameters should be arguments of resource.

.. code:: python

  @app.route ("/episode/<int:id>")
  def episode (was, id):
    return id
  # http://127.0.0.1:5000/episode

for fancy url building, available param types are:

- int: integers and INCLUDING 'me', 'notme' and 'new'
- path: /download/<int:major_ver>/<path>, should be positioned
  at last like /download/1/version/1.1/win32
- If not provided, assume as string. and all space will be replaced to "_"

At your template engine, you can access through was.request.PARAMS ["id"].

It is also possible via keywords args,

.. code:: python

  @app.route ("/episode/<int:id>")
  def episode (was, \*\*karg):
    retrun was.request.ARGS.get ("id")
  # http://127.0.0.1:5000/episode/100

You can set default value to id,

.. code:: python

  @app.route ("/episode/<int:id>", methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
  def episode (was, id = None):
    if was.request.method == "POST" and id is None:
      ...
      return was.API (id = new_id)
    return ...

It makes this URL working,

.. code:: bash

  http://127.0.0.1:5000/episode

And was.urlfor will behaive like as below,

.. code:: bash

  was.urlfor ("episode")
  >> /episode

 was.urlfor ("episode", 100)
  >> /episode/100

*Note* that this does not works for root resource,

.. code:: python

  @app.route ("/<int:id>", methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
  def episode (was, id = None):
    if was.request.method == "POST" and id is None:
      ...
      return was.API (id = new_id)
    return ...

By above code, http://127.0.0.1:5000/ will not work. You should define "/" route.



Query String Parameters
``````````````````````````````

qiery string parameter can be both resource arguments but needn't be.

.. code:: python

  @app.route ("/hello")
  def hello_world (was, num = 8):
    return num
  # http://127.0.0.1:5000/hello?num=100

It is same as these,

.. code:: python

  @app.route ("/hello")
  def hello_world (was):
    return was.request.ARGS.get ("num")

  @app.route ("/hello")
  def hello_world (was, **url):
    return url.get ("num")
    # of
    return was.request.URL.get ("num)

Above 2 code blocks have a significant difference. First one can
get only 'num' parameter. If URL query string contains other
parameters, Skitai will raise 508 Error. But 2nd one can be any
parameters.

Getting Form/JSON Parameters
```````````````````````````````

Getting form is not different from the way for url parameters, but
generally form parameters is too many to use with each function
parameters, can take from single args \*\*form or take mixed with
named args and \*\*form both.

if request header has application/json

.. code:: python

  @app.route ("/hello")
  def hello (was, **form):
    return "Post %s %s" % (form.get ("userid", ""), form.get ("comment", ""))

  @app.route ("/hello")
  def hello_world (was, userid, **form):
    return "Post %s %s" % (userid, form.get ("comment", ""))

Note that for receiving request body via arguments, you specify
keywords args like \*\*karg or specify parameter names of body data.

If you want just handle POST body, you can use was.request.json ()
or was.request.form () that will return dictionary object.

Getting Composed Parameters
```````````````````````````````

You can receive all type of parameters by resource arguments. Let's
assume yotu resource URL is http://127.0.0.1:5000/episode/100?topic=Python.

.. code:: python

  @app.route ("/episode/<int:id>")
  def hello (was, id, topic):
    pass

if URL is http://127.0.0.1:5000/episode/100?topic=Python with Form/JSON
data {"comment": "It is good idea"}

.. code:: python

  @app.route ("/episode/<int:id>")
  def hello (was, id, topic, comment):
    pass

Note that argument should be ordered by:

- URL parameters
- URL query string
- Form/JSON body

And note if your request has both query string and form/JSON body,
and want to receive form paramters via arguments, you should receive
query string parameters first. It is not allowed to skip query string.

Also you can use keywords argument.

.. code:: python

  @app.route ("/episode/<int:id>")
  def hello (was, id, \*\*karg):
    karg.get ('topic')

Note that \*\*karg is contains both query string and form/JSON data
and no retriction for parameter names.

was.requests.args is merged dictionary for all type of parameters. If
parameter name is duplicated, its value will be set to form of value
list (But If parameters exist both URL and form data, form data always
has priority. It means URL parameter will be ignored).

Then simpletst way for getting parameters, use was.request.args.


.. code:: python

  @app.route ("/episode/<int:id>")
  def hello (was, id):
    was.request.args.get ('topic')

Testing Parameters
```````````````````````````````

For parameter checking,

.. code:: python

  @app.route ("/test")
  @app.inspect ("ARGS", ["id"], ints = ["id"])
  def test (was, id):
    return was.render ("test.html")

'id' is required and sholud be int type.

Spec is,

.. code:: python

  @app.inspect (
    scope, required = None, ints = None, floats = None,
    emails = None, uuids = None, nones = None, lists = None,
    strings = None, booleans = None, dicts = None,
    oneof = None, manyof = None,
    notags = None, safes = None,
    **kargs
  )

- notags: replace all < and >
- safes: reject if find XSS possible string

*scope* can be:

- URL
- FORM
- JSON
- ARGS: default, all of above

- GET
- DELETE
- PATCH
- POST
- PUT

.. code:: python

    @app.route ("/1")
    @app.inspect ("GET", ints = ['offset', 'limit'])
    @app.inspect ("PUT", ['id'])
    def index6 (was, offset = 0, limit = 10, **DATA):
        assert isinstance (limit, int) # limit converted into int type
        if was.request.method == 'PUT':
          current = DATA [id]

Also you can use specify each paramenter types.

.. code:: python

    @app.route ("/<int:id>")
    @app.inspect (offset = int, prodtype = [int, str])
    def index6 (was, id, offset, prodtype):
        ...

You can test more detail using kargs.

.. code:: python

    @app.route ("/1")
    @app.inspect ("ARGS", a__gte = 5, b__between = (-4, -1), c__in = (1, 2))
    def index6 (was):
        return ""

- __neq
- __gt, __gte
- __lt, __lte
- __in, __notin
- __between
- __startswith
- __endswith
- __notstartwith
- __notendwith
- __contains
- __notcontain

Checking parameter with regular expression,

.. code:: python

    @app.route ("/2")
    @app.reqinspectuire ("ARGS", a = re.compile ("^hans"))
    def index7 (was):
        return ""

Checking parameter length, use __len:

.. code:: python

    @app.route ("/3")
    @app.inspect ("ARGS", a__len__between = (4, 8))
    def index7 (was):
        return ""

Checking JSON nodes, use triple under bars for key and double ones
for array indexing.

.. code:: python

    @app.route ("/15")
    @app.require (data___scores__1__gte = 10)
    def index15 (was, d):
        return ""
    # {"data": {"scores": [9, 12, 16]}} will be passed


Pre-Defined Parameter Values
``````````````````````````````````````````````````````

'me', 'notme' is special prameter value used by authentication.

- 'me' can be resolved into user ID on request handling
- 'notme' can ignore specific user ID for administative
  search purpose, BUT for your safey, 'notme' is allowed
  only with "GET" request
- 'new' is dummy value especially with "POST" method. But
  it is not restricted by methods. Maybe you can use 'new'
  with 'GET' for getting newlest items.

.. code:: python

  @app.route ("/episodes/<int:uid>")
  @app.permission_required (uid = ["staff"])
  def episodes (uid):
    ...

Now paramter 'uid' is bound with permission.

Belows are all valid URI.

- GET /episodes/me, if request user have any permission
- DELETE /episodes/me if request user have any permission
- GET /episodes/4, if request user have staff permission,
  else raise 403 error
- PATCH /episodes/4, if request user have staff permission,
  else raise 403 error
- GET /episodes/new, if request user have staff permission,
  else raise 403 error
- POST /episodes/new, if request user have staff permission,
  else raise 403 error
- GET /episodes/notme, if request user have staff permission,
  else raise 403 error

But belows are all invalid and HTTP 421 error will be raised
for your safety reason. If these're allowed, there is lot of
danger delete/update all users (or all rows of database table).

- DELETE /episodes/notme
- POST /episodes/notme
- PATCH /episodes/notme
- PUT /episodes/notme

Obviously, I am sure you already know exact resource ID for
above tasks.


Make Your Own Rule
``````````````````````````

The way to get parameters is little messy. But I want to try to
make more pythonic style. Even all routed method can be called by
another non app functions.

Initially I want to use like this.

.. code:: python

  @app.route ("/pets/<kind>")
  def pets (was, kind, limit, offset = 0, **JSON):
    ...

It can be requested by requests.

.. code:: python

  requests.post (
    "http://localhost/pets/dog?limit=10",
    json = {"area": "LA"}
  )

If you need to check the origin of parameters, require decorator
is useful.

.. code:: python

  @app.route ("/pets/<kind>")
  @app.inspect ("JSON", ["area"])
  def pets (was, kind, limit, offset = 0, **JSON):
    ...

That's just my opinion.


Response
-------------

Basically, just return contents.

.. code:: python

  @app.route ("/hello")
  def hello_world (was):
    return was.render ("hello.htm")

If you need set additional headers or HTTP status,

.. code:: python

  @app.route ("/hello")
  def hello (was):
    return was.response ("200 OK", was.render ("hello.htm"), [("Cache-Control", "max-age=60")])

  def hello (was):
    return was.response (
      body = was.render ("hello.htm"),
      headers = [("Cache-Control", "max-age=60")]
    )

  def hello (was):
    was.response.set_header ("Cache-Control", "max-age=60")
    return was.render ("hello.htm")

Above 3 examples will make exacltly same result.

Sending specific HTTP status code,

.. code:: python

  def hello (was):
    return was.response ("404 Not Found", was.render ("err404.htm"))

  def hello (was):
    # if body is not given, automaticcally generated with default error template.
    return was.response ("404 Not Found")

If app raise exception, traceback information will be displayed
only app.debug = True. But you intentionally send it inspite of
app.debug = False:

.. code:: python

  # File
  @app.route ("/raise_exception")
  def raise_exception (was):
    try:
      raise ValueError ("Test Error")
    except:
      return was.response ("500 Internal Server Error", exc_info = sys.exc_info ())

If you use custom error handler, you can set detail explaination
to error ["detail"].

.. code:: python

  @app.default_error_handler
  def default_error_handler (was, error):
    return was.render ("errors/default.html", error = error)

  def error (was):
    return was.response.with_explain ('503 Serivce Unavaliable', "Please Visit On Thurse Day")


You can return various objects.

.. code:: python

  # File
  @app.route ("/streaming")
  def streaming (was):
    return was.response ("200 OK", open ("mypicnic.mp4", "rb"), headers = [("Content-Type", "video/mp4")])

  # Generator
  def build_csv (was):
    def generate():
      for row in iter_all_rows():
        yield ','.join(row) + '\n'
    return was.response ("200 OK", generate (), headers = [("Content-Type", "text/csv")])


All available return types are:

- String, Bytes, Unicode
- File-like object has 'read (buffer_size)' method, optional 'close ()'
- Iterator/Generator object has 'next() or _next()' method, optional
  'close ()' and shoud raise StopIteration if no more data exists.
- Something object has 'more()' method, optional 'close ()'
- Classes of skitai.lib.producers
- List/Tuple contains above objects
- XMLRPC dumpable object for if you want to response to XMLRPC

The object has 'close ()' method, will be called when all data
consumed, or socket is disconnected with client by any reasons.

- was.response (status = "200 OK", body = None, headers = None,
  exc_info = None)
- was.response.throw (status = "200 OK"): abort handling request,
  generated contents and return http error immediatly
- was.API (\_\_data_dict\_\_ = None, \*\*kargs): return api
  response container
- was.Fault (status = "200 OK",\*args, \*\*kargs): shortcut for
  was.response (status, was.API (...)) if status code is 2xx
  and was.response (status, was.Fault (...))
- was.response.traceback (msg = "", code = 10001,  debug = 'see traceback',
  more_info = None):
  return api response container with setting traceback info

- was.response.set_status (status) # "200 OK", "404 Not Found"
- was.response.get_status ()
- was.response.set_headers (headers) # [(key, value), ...]
- was.response.get_headers ()
- was.response.set_header (k, v)
- was.response.get_header (k)
- was.response.del_header (k)
- was.response.hint_promise (uri) # *New in skitai version 0.16.4*,
  only works with HTTP/2.x and will be ignored HTTP/1.x

Cache controlling,

- was.response.set_etag (identifier, max_age = 0, as_etag = False)
- was.response.set_mtime (mtime, length = None, max_age = 0)
- was.response.set_etag_mtime (identifier, mtime, length = None,
  max_age = 0, as_etag = False)


HTTP Exception
``````````````````````````

Abort immediatly and send HTTP eroor content.

.. code:: python

  @app.route ("/<filename>")
  def getfile (was, filename):
    if not os.path.isfile (filename):
      raise was.Error ("404 Not Found", "{} not exists".format (filename))
    return was.File (filename)

Using assert, you can quick send HTTP Error.

.. code:: python

  @app.route ("/<filename>")
  def getfile (was, filename):
    assert filename.endswith ('.png'), was.Error ("400 Not My Fault", 'filename must be end with png')
    return was.File (filename)


Data Streaming
```````````````````````

.. code:: python

  @app.route ("/stream")
  def stream (was):
      def stream ():
          for i in range (100):
              yield '<CHUNK>'
      return was.response ("200 OK", stream (), headers = [('Content-Type', 'text/plain')])


Treaded Data Streaming
````````````````````````````````

.. code:: python

  class Producer:
    def get (self, n):
      return [random.randrange (1000) for _ in range (n)]

  def producing (producer):
      def produce (queue):
          while 1:
              items = producer.get (100)
              if not items:
                  queue.put (None) # end of stream
                  break
              queue.put (str (items))
      return produce

  @app.route ("/threaproducer")
  def threaproducer (was):
      return was.Queue (producing (Producer ()))


Redirecting To Static File
``````````````````````````````````

.. code:: python

  @app.route ("/robots.txt")
  def robots (was):
      if app.debug:
          was.response ['Content-Type'] = 'text/plain'
          return "User-Agent: *\nDisallow: /\n"
      return was.Static ('/robots.real.txt')

It will handle ETag, Last-Modified, Range etc just like common static files.


File Stream On Local File System
``````````````````````````````````````

.. code:: python

  @app.route ("/<filename>")
  def getfile (was, filename):
    return was.File ('/data/%s' % filename)


API Response
````````````````````
*New in skitai version 0.26.15.9*

In cases you want to retrun JSON API reponse,

.. code:: python

  # return JSON {data: [1,2,3]}
  return was.Fault ('200 OK', data = [1, 2, 3])
  # return empty JSON {}
  return was.Fault (201 Accept')

  # and shortcut if response HTTP status code is 200 OK,
  return was.API (data =  [1, 2, 3])

  # return empty JSON {}
  return was.API ()

For sending error response with error information,

.. code:: python

  # client will get, {"message": "parameter q required", "code": 10021}
  return was.Fault ('400 Bad Request', 'missing parameter', 10021)

  # with additional information,
  was.Fault (
    '400 Bad Request',
    'missing parameter', 10021,
    'need parameter offset and limit', # detailed debug information
    'http://127.0.0.1/moreinfo/10021', # more detail URL something
  )

You can send traceback information for debug purpose like in case
app.debug = False,

.. code:: python

  try:
    do something
  except:
    return was.Fault (
      '500 Internal Server Error',
      'somethig is not valid',
      10022,
      traceback = True
    )

  # client see,
  {
    "code": 10001,
    "message": "somethig is not valid",
    "debug": "see traceback",
    "traceback": [
      "name 'aa' is not defined",
      "in file app.py at line 276, function search"
    ]
  }

Important note that this response will return with HTTP 200 OK status.
If you want return 500 code, just let exception go.

But if your client send header with 'Accept: application/json'
and app.debug is True, Skitai returns traceback information automatically.

**Datetime Encoding JSON**

.. code:: python

  app.config.JSON_ENCODER = 'utcoffset'

- utcoffset: 2030-12-24 15:09:00+00 (default, utc timezone)
- str: 2030-12-24 15:09:00 (with system timezone)
- iso: 2030-12-04T15:09:00 (utc timezone)
- unixepoch: 1582850951.0 (utc timezone)
- digit: 20301224150900 (utc timezone)


Selective Media Response By Accept Header
`````````````````````````````````````````````````````

If client's `Accept` header contains 'text/html', respond as rendered
HTML or as JSON/XML API response.

.. code:: python

  @app.route ('/')
  def index (was, error):
    return was.render_or_API ("index.html", result = result)


Map / Mapped Response
`````````````````````````````

*New in version 0.35.1*

It is comprehensive and faster API response with key mapping from
corequest objects directly.

Starndard version of API response,

.. code:: python

  task = was.db ("@sqlite3").execute ("select * from test")
  return was.API (result = task.fetch ())

  # JSON response,
  # { result: [...] }

More faster version,

.. code:: python

  def respond (was, task):
    was.API (result = task.fetch ())

  task = was.db ("@sqlite3").execute ("select * from test")
  return task.then (respond)

Same but using lambda for simplicity,

.. code:: python

  task = was.db ("@sqlite3").execute ("select * from test")
  return task.then (lambda x = was, y = task: x.API (result = y.fetch ()))

Same but using was.Map for more simplicity,

.. code:: python

  task = was.db ("@sqlite3").execute ("select * from test")
  return was.Map (result = task)

Another examples.

.. code:: python

  @app.route ("/bench/sp", methods = ['GET'])
  def bench_sp (was):
    with was.db ('@mydb') as db:
      root = (db.select ("foo")
                  .order_by ("-created_at")
                  .limit (10)
                  .filter (Q (from_wallet_id = 8) | Q (detail = 'ReturnTx')))

      return was.Map (
        was.Thread (time.sleep, args = (0.3,)), # no need map
        files = was.Subprocess ('ls /var/log'),
        result = root.clone ().execute (),
        record_count__one = root.clone ().aggregate ('count (id) as cnt').execute ()
      )

    # JSON response, 1st args had been executed but ignored in results because no map name
    # >> { result: [...],  record_count: {cnt: 123}, ls: 'syslog ...' }

Like was.Tasks, above 4 corequests will be executes concurrently. So it is
equivalent below.

.. code:: python

  tasks = was.Tasks (
    was.Thread (time.sleep, args = (0.3,)), # no need map
    files = was.Subprocess ('ls /var/log'),
    result = was.db ('@mydb', filter = hide_password).execute ('select * from user')
  )

  _, ls, result, record_count = tasks.fetch ()
  return was.API (
    files = ls,
    result = result,
    record_count = record_count [0]
  )

Is it more superior choice to use was.Map than was.API?

No, was.Map () is useful only if you need NOT modify them. If you can make
good and complex SQL with functions, was.Map () is suprior for the most time.

Also Instead of complex SQL, you can use filter option for modifying results,

.. code:: python

  def hide_password (rows):
    for row in rows:
      row.password = '****'
    return rows

  return was.Map (
    files = was.Subprocess ('ls /var/log', filter = lammda x: x.replace (' ', '_')),
    result = was.db ('@mydb', filter = hide_password).execute ('select * from user')
  )

Further more,

.. code:: python

    # __one__FIELD_NAME
    record_count__one__cnt = root.aggregate ('count (id) as cnt').execute ()
    # >> { record_count: 123 }

    # shortly,
    record_count__cnt = root.aggregate ('count (id) as cnt').execute ()


Also for returning custom HTTP status coe,

.. code:: python

  return was.Map ('210 Something', result = root.execute ())

was.Map can have these arguments.

- \_\_timeout: processing timeout.
- \_\_mtime: dot joined key names, ex) 'result.last_update'.
  target value should be an timestamp or datetime type and
  this value used to set 'Last-Modified' header
- \_\_etag: dot joined key names, ex) 'result.last_update'.
  this value used to set 'Etag' header
- \_\_maxage: int seconds


was.Mapped () is also available.

.. code:: python

  # service.py
  def get_result ():
    return was.Tasks (
      files = was.Subprocess ('ls /var/log', filter = lammda x: x.replace (' ', '_')),
      result = was.db ('@mydb', filter = hide_password).execute ('select * from user')
    )

  # apis.py
  tasks = service.get_result ()
  return was.Mapped (tasks)


Selective Media Response By Accept Header With Map Respinse
`````````````````````````````````````````````````````````````````

If client's `Accept` header contains 'text/html', respond as rendered
HTML or as JSON/XML API response.

.. code:: python

  @app.route ('/')
  def index (was, error):
    return was.render_or_Map ("index.html", result = db.execute ('...'))

  @app.route ('/')
  def index (was, error):
    tasks = was.Taks (result = db.execute ('...'))
    return was.render_or_Mapped ("index.html", tasks)


Process / Thread Response
`````````````````````````````````````````

These are very same with Future response.

If you have CPU bound jobs, use was.Process.

.. code:: python

  @app.route ('...')
  def foo ():
    def repond (was, task):
        return was.API (result = task.fetch (), a = task.meta ['a'])
    return was.Process (math.sqrt, args = (4.0,), meta = {'a': 1}).then (respond)

If you have I/O bound jobs, use was.Thread.

.. code:: python

  @app.route ('...')
  def foo ():
    def repond (was, task):
        return was.API (result = task.fetch ())

    def sqrt (a):
      return math.sqrt (a)

    return was.Thread (sqrt, args = (4.0,)).then (respond)


ThreadPass Response
`````````````````````````````````````````

For returning request handling threads, you can use was.ThreadPass.

In ThreadPass you can also use corequest in that function.

.. code:: python

  @app.route ("/thread_future", methods = ['GET'])
  def thread_future_respond (was):
      def respond (was, a):
          a = some_synchronous_task ()
          # you can make corequest
          was.db ('@mydb').execute (...).commit ()
          return was.API (
            result = a
          )
      return was.ThreadPass (respond, args = (4.0,))

*Note*: There isn't was.ProcessPass ().


Proxypass Response
```````````````````````````````````

Skitai's mounted proxypass is higher priority than WSGI app. If you
want make this to lower  priority, can use was.ProxyPass.

.. code:: python

  @app.route ("/<path:path>")
  def proxy (was, path = None):
    return was.ProxyPass ("@myupstream", path)

But it is valid only if request method is GET, because it is mainly
used for building integrated development environment with
frontend frameworks linke Node.js.


Generator Based Coroutine
----------------------------------------

* New in version 0.8.6*

Coroutine use '@app.coroutine' and 'yield' like 'async and await'.


Coroutine
`````````````````````

.. code:: python

  @app.route ("/coroutine/1")
  def coroutine (was):
      def respond (was, task):
          return task.fetch ()

      with was.stub ("http://example.com") as stub:
          return stub.get ("/").then (respond)

  @app.route ("/coroutine/2")
  @app.coroutine
  def coroutine2 (was):
      with was.stub ("http://example.com") as stub:
          task = yield stub.get ("/")
      return task.fetch ()

Both functions are exactly same behaivior and results.

'@app.coroutine' can replacable with @app.router parameter.

.. code:: python

  @app.route ("/coroutine/2", coroutine = True)
  def coroutine2 (was):
      with was.stub ("http://example.com") as stub:
          task = yield stub.get ("/")
      return task.fetch ()


*Note:* DO USE was.Thread for blocking operation after first yield.

.. code:: python

  @app.route ("/coroutine")
  @app.coroutine
  def coroutine (was):
      with was.stub ("http://example.com") as stub:
          task1 = yield stub.get ("/")
      task2 = yield was.Mask ('mask')
      return was.API (a = task1.fetch (), b = task2.fetch ())

  @app.route ("/coroutine/9", coroutine = True)
  def coroutine9 (was):
    def wait_hello (timeout = 1.0):
      time.sleep (timeout)
      return 'mask'

      tasks = yield was.Tasks (
        a = was.Mask ("Example Domain"),
        b = was.Thread (wait_hello, args = (1.0,))
      )
      task3 = yield was.Thread (wait_hello, args = (1.0,))
      task4 = yield was.Subprocess ('ls')
      return was.API (d = task4.fetch (), c = task3.fetch (), **tasks.fetch ())

Response Streaming
`````````````````````

Coroutine also yield response data as generator. This would be
useful for massive and long running database query result
streaming for example.

.. code:: python

  @app.route ("/download_csv", coroutine = True)
  def download_csv (was):
      yield "ID, NAME\n"
      current_id = 0
      while 1:
          task = yield (was.db ('@mydb').select ('tble')
                          .get ('id, name')
                          .filter (id__gt = current_id).
                          limit (fetch_count)).execute ()
          rows = task.fetch ()
          if not rows:
            break
          current_id += fetch_count
          yield '\n'.join (['{}, "{}"'.format (row.id, row.name) for row in rows])


**Note**: Yielding data type SHOULD be string or bytes (or Corequest object).

**Caution**: If you need just data generator, DO NOT use @app.coroutine. You
just use yield data. @app.coroutine try to collect data until meeting Corequest
object, so it will block your routine or not release your request thread.


Request Streaming
`````````````````````

Use was.Input ().

.. code:: python

  @app.route ("/bistreaming", methods = ['POST'], coroutine = True, input_stream = True)
  def coroutine_streaming (was):
      buf = []
      while 1:
          data = yield was.Input (4096)
          if not data:
              break
          buf.append (data)
      return b''.join (buf)


**Caution**: Be careful to use request streaming. Request streaming need only
a few specific conditions.

1. Small chunked request data which is intermittent and need long terms
   connection like receiving GPS coordinate data from client device
2. Bidirectional streaming like detectecting silence for 10~30ms segments
   of audio data stream. See next `Bidirectional Streaming` topic.

If you just want upload data, just use regular POST upload method. DO NOT
use request streaming which may cause event loop blocking and also is
very inefficient.


Bidirectional Streaming
``````````````````````````````

Use was.Input () and yield.

.. code:: python

  @app.route ("/bistreaming", methods = ['POST'], coroutine = True, input_stream = True)
  def coroutine_streaming (was):
      while 1:
          data = yield was.Input (16184)
          if not data:
              break
          yield b':' + data


gRPC Examples
``````````````````````

- `server side`_
- `client side`_

.. _`server side`: https://gitlab.com/hansroh/skitai/-/blob/master/tests/examples/grpc_route_guide.py
.. _`client side`: https://gitlab.com/hansroh/skitai/-/blob/master/tests/level4-1/test_grpc.py


Mounting Resources: Making Simpler & Modular App
-------------------------------------------------------------------

*New in skitai version 0.26.17*

Implicit Mount Services On Your App
````````````````````````````````````````````

I already mentioned *App Structure* section, you can split yours views
and help utilties into services directory.

Assume your application directory structure is like this,

.. code:: bash

  templates/*.html
  services/*.py # app library, all modules in this directory will be watched for reloading
  static/images # static files
  static/js
  static/css

  app.py # this is starter script

app.py

.. code:: python

  from services import auth

  app = Atila (__name__)

  app.debug = True
  app.use_reloader = True

  @app.default_error_handler
  def default_error_handler (was, e):
    return str (e)

services/auth.py

.. code:: python

  # shared utility functions used by views

  def titlize (s):
    ...
    return s

  def __mount__ (app):
    @app.login_handler
    def login_handler (was):
      if was.request.session.get ("username"):
        return
      next_url = not was.request.uri.endswith ("signout") and was.request.uri or ""
      return was.redirect (was.urlfor ("signin", next_url))

    @app.route ("/signout")
    def signout (was):
      was.request.session.remove ("username")
      was.request.mbox.push ("Signed out successfully", "success")
      return was.redirect (was.urlfor ('index'))

    @app.route ("/signin")
    def signin (was, next_url = None, **form):
      if was.request.args.get ("username"):
        user = auth.authenticate (username = was.request.args ["username"], password = was.request.args ["password"])
        if user:
          was.request.session.set ("username", was.request.args ["username"])
          return was.redirect (was.request.args ["next_url"])
        else:
          was.request.mbox.push ("Invalid User Name or Password", "error", icon = "new_releases")
      return was.render ("sign/signin.html", next_url = next_url or was.urlfor ("index"))

You just import module from services. but *def __mount__ (app)* is core in
each module. Every modules can have *__mount__ (app)* in *services*, so you
can split and modulize views and utility functions. __mount__ (app) will be
automatically executed on starting. If you set app.use_reloader, theses services
will be automatically reloaded and re-executed on file changing. Also you can
make global app sharable functions into seperate module like util.py without
views.


Mounting Services With Options
`````````````````````````````````````````````````

If you need additional options on decorating,

.. code:: python

  def __mount__ (app):
    @app.route ("/login")
    def login (was):
      ...

  # or with mount options
  def __mount__ (app, mntopt):
    @app.route ("/login")
    def login (was):
      ...


And on app,

.. code:: python

  from services import auth

  app = Atila (__name__)
  app.mount ('/regist', auth)

Finally, route of login is "/regist/login".

Sometimes function names are duplicated if like you
import contributed services.

.. code:: python

  from services import auth

  app = Atila (__name__)
  app.mount ( '/regist', auth, ns = "regist")

Now, you can import iport without name collision. But be careful
when use was.urlfor () etc.

Note that options should be keyword arguments.

.. code:: python

  {{ was.urlfor ("regist.login") }}

If you want to mount only debug environment,

.. code:: python

  app.mount (auth, debug_only = True)

If you want to authentify to all services,

.. code:: python

  app.mount (auth, authenticate = "bearer")

Currently *reserved arguments* are:

- authenticate
- debug_only
- point

Your custom options can be accessed by __mntopt__ in your module.

First, mount with redirect option.

.. code:: python

    app.mount (auth, redirect = "index")
    # automatically set to auth.__mntopt__ = {"redirect": "index"}

then you can access in auth.py,

.. code:: python

    @app.route ("/regist/signout")
    def signout (was):
        was.request.mbox.push ("Signed out successfully", "success")
        return was.redirect (was.urlfor (__mntopt__.get ("redirect", 'index')))

Setup Services
`````````````````````

all service can also have \_\_setup\_\_ hook.

.. code:: python

  # foo.py
  BASE_PATH = '/var'
  def __setup__ (app):
    ...

  # or with mount options
  def __setup__ (app, mntopt):
    global BASE_PATH
    BASE_PATH = mntopt.get ('base_path', BASE_PATH)

  def __mount__ (app):
    ...

  # app.py

  from services import foo
  from atila import Atila

  app = Atila (__name__)
  app.mount ('/', foo, base_path = '/home/ubuntu')


Recursive Sub Services Mounting
````````````````````````````````````````

Assume you have examples package in your service.

.. code:: bash

  services/examples/__init__.py
  services/examples/foo.py
  services/examples/bar.py

You can use \_\_setup\_\_ hook for mounting all sub services.

.. code:: python

  # services/examples/__init__.py
  from . import foo, bar

  def __setup__ (app, mntopt):
    app.mount ('/foo', foo, threshold = mntopt.get ('threashold', 5))
    app.mount ('/bar', bar)

Then you can mount just top package one.

.. code:: python

    # app.py
    from services import examples

    app.mount ('/examples', examples, threshold = 10)

As a result, foo will be mounted on `/examples/foo`.


Your all sub packeges can be mounted as this way recursivley. It
makes several advantages.

- You can precise control on exact mount or umount timing
- Managable sub packages as plugins and increse reusability


Unmounting Resources
```````````````````````````````

*New in skitai version 0.27*

Also 'umount' is avaliable for cleaning up module resource.

.. code:: python

  resource = ...

  def __umount__ (app):
    resource.close ()
    app.someghing = None

This will be automatically called when:

- before module itself is reloading
- before app is reloading
- app unmounted from Skitai


URL Building with Namespace
````````````````````````````````````

*New in version 0.3.3*

If you want to access resources to another sub module, you can use
with full module name.

For example,

.. code:: python

  # services/v1/account.py
  def __mount__ (app):
    @app.route ("/register")
    def register (was):
      ...

An you can access like this,

.. code:: python

  was.urlfor ("v1.account.register")


More About Websocket
--------------------------------------

*New in Skitai version 0.26.18*

**websocket design specs** can be choosen one of 3.

This decorator spec is,

.. code:: python

  @app.websocket (
    spec,
    timeout = 60,
    onopen = None,
    onclose = None
  )


WS_COROUTINE (*New in version 0.8.8*)
`````````````````````````````````````````````````

- messaging with coroutine

.. code:: python

  @app.route ("/echo_coroutine")
  @app.websocket (skitai.WS_COROUTINE, 60)
  def echo_coroutine (was):
    while 1:
      msg = yield was.Input ()
      if not msg:
        break

      with was.stub ('http://example.com') as stub:
        task = yield stub.get ("/")
        yield task.fetch ()


WS_CHANNEL
`````````````````````````````````````````````````

- simple request and response way like AJAX
- with WS_THREAD, WS_SESSION, WS_NOTHREAD, WS_NOTHREAD options

**websocket message handling options**

**WS_THREAD**

- default, function base websocket message handling
- it treats every single websocket message as single request to
  resources like url requests.
- on receiving message from client, it will call function
  for handling with queue and thread pool, it is basically
  same as request resource

**WS_SESSION** (New in version Skitai 0.30)

- non-threaded generator base websocket message handling
- cannot use this option with WS_THREADSAFE

**WS_NOTHREAD**

- non-threaded function call base websocket message handling
- it is faster than WS_THREAD

**WS_THREADSAFE** (New in version Skitai 0.26)

- Mostly same as WS_THREAD
- Message sending is thread safe
- Most case you needn't this option, but you create yourself one or
  more threads using websocket.send () method you need this for
  your convinience

*Note:* WS_NOTHREAD and WS_SESSION will block SKitai event loop while
you generate message to respond. If sending messasge generation time is
reltively long, use WS_THREAD or WS_THREADSAFE.


Websokect usage is already explained, but Atila provide @app.websocket
decorator for more elegant way to use it.

.. code:: python

  def onopen (was):
    print ('websocket opened')

  def onclose (was):
    print ('websocket closed')

  @app.route ("/websocket")
  @app.websocket (skitai.WS_CHANNEL, 1200, onopen, onclose)
  def websocket (was, message):
    return 'you said: ' + message


In some cases, you need additional parameter for opening/closing websocket.

.. code:: python

  @app.route ("/websocket")
  @app.websocket (skitai.WS_CHANNEL | skitai.WS_THREADSAFE, 1200, onopen)
  def websocket (was, message, option):
    return 'you said: ' + message

Then, your onopen function must have additional parameters except *message*.

.. code:: python

  def onopen (was):
    print ('websocket opened with', was.request.ARGS ["option"])

Now, your websocket endpoint is "ws://127.0.0.1:5000/websocket?option=value"

Save websocket client id to session.

.. code:: python

  def onopen (was):
    was.request.session.set ("WS_ID", was.websocket.client_id)

  def onclose (was):
    was.request.session.remove ("WS_ID")

  @app.route ("/websocket")
  @app.websocket (skitai.WS_CHANNEL | skitai.WS_FAST, 1200, onopen, onclose)
  def websocket (was, message):
    return 'you said: ' + message

And push message to client.

.. code:: python

  @app.route ("/item_in_stock")
  def item_in_stock (was):
    app.websocket_send (
      was.request.session.get ("WS_ID"),
      "Item In Stock!"
    )

*Note:*: I'm not sure it is works in all web browser.


**WS_NOTHREAD**

WS_NOTHREAD does not use queue or thread pool. In this case, response is
more faster but if response includes IO blocking operation, entire
Skitai event loop will be blocked.

.. code:: python

  @app.route ("/websocket")
  @app.websocket (skitai.WS_CHANNEL | skitai.WS_NOTHREAD, 60, onopen)
  def websocket (was, message):
    return 'you said: ' + message

**WS_SESSION**

With WS_SESSION should return Python generator object,

.. code:: python

  @app.route ("/websocket")
    @app.websocket (skitai.WS_CHANNEL | skitai.WS_SESSION, 60)
    def websocket (was):
      while 1:
        message = yield
        if not message:
          return #strop iterating
        yield "ECHO:" + message

*Note:* If you use WS_SESSION option, onopen and onclose should be None,
because in session, you can handle open and close within your function.


WS_GROUPCHAT (New in version Skitai 0.24)
`````````````````````````````````````````````````

- thread pool manages n websockets connection
- chat room model



Building Static URL
--------------------------

.. code:: python

  app.config.STATIC_URL = '/static/'
  app.config.MEDIA_URL = '/media/'

*Note*: Each url must be end with '/'.

.. code:: python

  @app.route ("/")
  def add (was):
    was.static ('assets/style.css') # resolve to /static/assets/style.css
    was.media ('movie.mov') # resolve to /media/movie.mov

*Note*: `was.Static` is reponsible object,

.. code:: python

  @app.route ("/")
  def add (was):
    return was.Static (was.static ('assets/style.css'))
    # OR shortly,
    return was.Static ('assets/style.css')


Building URL
---------------

If your app is mounted at "/math",

.. code:: python

  @app.route ("/add")
  def add (was, num1, num2):
    return int (num1) + int (num2)

  app.build_url ("add", 10, 40) # returned '/math/add?num1=10&num2=40'

  # BUT it's too long to use practically,
  # was.urlfor is acronym for app.build_url
  was.urlfor ("add", 10, 40) # returned '/math/add?num1=10&num2=40'
  was.urlfor ("add", 10, num2=60) # returned '/math/add?num1=10&num2=60'

  #You can use function directly as well,
  was.urlfor (add, 10, 40) # returned '/math/add?num1=10&num2=40'

  @app.route ("/hello/<name>")
  def hello (was, name = "Hans Roh"):
    return "Hello, %s" % name

  was.urlfor ("hello", "Your Name") # returned '/math/hello/Your_Name'

Basically, was.urlfor is same as Python function call.


If your module is,

.. code:: python

  # services/boards/index.py

  def __mount__ (app):
    @app.route ('/search'):
    def search (was, q):
      ...

You can make url like this,

.. code:: python

  was.urlfor ('boards.index.search', q = 'news')


Building URL by Updating Parameters Partially
````````````````````````````````````````````````

**New in skitai version 0.27**

.. code:: python

  @app.route ("/navigate")
  def navigate (was, limit = 20, pageno = 1):
    return ...

If this resource was requested by /naviagte?limit=100&pageno=2, and
if you want to make new resource url with keep a's value (=100),
you can make URL like this,

.. code:: python

  was.urlfor ("navigate", was.request.args.limit, 3)

But you can update only changed parameters partially,

.. code:: python

  was.urlpatch ("add", pageno = 3)

Parameter a's value will be kept with current requested parameters.
Note that was.urlpatch can be recieved keyword arguments only except
first resource name.

was.urlpatch is used changing partial parameters (or none) based over
current parameters.


Building Base URL without Parameters
````````````````````````````````````

**New in skitai version 0.27**

Sometimes you need to know just resource's base path info - especially
client-side javascript URL building, then use *was.basepath*.

.. code:: python

  @app.route ("/navigate")
  def navigate (was, limit, pageno = 1):
    return ...

.. code:: python

  was.basepath ("navigate")
  >> return "/navigate"

For example, in your VueJS template,

.. code:: html

  <a :href="'{{ was.basepath ('navigate') }}?limit=' + limit_option + '&pageno=' + (current_page + 1)">Next Page</a>

Note that base path means for fancy Url,

.. code:: python

  @app.route ("/user/<id>")
  >> base path is "/user/"

  @app.route ("/user/<id>/pat")
  >> base path is "/user/"



Piping
--------------

was.pipe () can call function by resource names. This make call
nested function within \_\_mount\_\_ (app) in another module.

For accessing by resource name, See was.urlfor ().

.. code:: python

    @app.route ("/1")
    @app.inspect (offset = int)
    def index (was, offset = 1):
        return was.API (result = offset)

    @app.route ("/2")
    def index2 (was):
        return was.pipe (index)

    @app.route ("/3")
    def index3 (was):
        return was.pipe (index, offset = 4)

    @app.route ("/4")
    def index4 (was):
        return was.pipe ('index', offset = 't')


If your module is,

.. code:: python

  # services/boards/index.py

  def __mount__ (app):
    @app.route ('/search'):
    def search (was, q):
      ...

You can make call by,

.. code:: python

  was.pipe ('boards.index.search', q = 'news')


Access Environment Variables
------------------------------

**was.request.env** (*alias: was.env*)

was.request.env is just Python dictionary object.

.. code:: python

  if "HTTP_USER_AGENT" in was.request.env:
    ...
  was.request.env.get ("CONTENT_TYPE")


Access Cookie
----------------

**was.request.cookie** (*alias: was.cookie*)

was.request.cookie has almost dictionary methods.

.. code:: python

  if "user_id" not in was.request.cookie:
    was.request.cookie.set ("user_id", "hansroh")
    # or
    was.request.cookie ["user_id"] = "hansroh"


*Changed in version 0.15.30*

'was.request.cookie.set()' method prototype has been changed.

.. code:: python

  was.request.cookie.set (
    key, val,
    expires = None,
    path = None, domain = None,
    secure = False, http_only = False
  )

'expires' args is seconds to expire.

 - if None, this cookie valid until browser closed
 - if 0 or 'now', expired immediately
 - if 'never', expire date will be set to a hundred years from now

If 'secure' and 'http_only' options are set to True, 'Secure' and
'HttpOnly' parameters will be added to Set-Cookie header.

If 'path' is None, every app's cookie path will be automaticaaly
set to their mount point.

For example, your admin app is mounted on "/admin" in configuration
file like this:

.. code:: python

  app = ... ()

  if __name__ == "__main__":

    import skitai

    skitai.run (
      address = "127.0.0.1",
      port = 5000,
      mount = {'/admin': app}
    )

If you don't specify cookie path when set, cookie path will be automatically
set to '/admin'. So you want to access from another apps, cookie should
be set with upper path = '/'.

.. code:: python

  was.request.cookie.set ('private_cookie', val)

  was.request.cookie.set ('public_cookie', val, path = '/')

- was.request.cookie.set (key, val, expires = None, path = None,
  domain = None, secure = False, http_only = False)
- was.request.cookie.remove (key, path, domain)
- was.request.cookie.clear (path, domain)
- was.request.cookie.keys ()
- was.request.cookie.values ()
- was.request.cookie.items ()
- was.request.cookie.has_key ()


Access Session
----------------

**was.request.session** (*alias: was.session*)

Strictly speaking, Atila hasn't got traditional session which some data
is stored on server side. And it doesn't provide any abstract classes or
methods for storing.

Ailta's session is just one of cookie value which contains signature
for checking alternation by any other things except Atila.

was.request.session has almost dictionary methods.

To enable session for app, random string formatted securekey should
be set for encrypt/decrypt session values.

*WARNING*: `securekey` should be same on all skitai apps at least
within a virtual hosing group, Otherwise it will be serious disaster.

.. code:: python

  app.securekey = "ds8fdsflksdjf9879dsf;?<>Asda"
  app.session_timeout = 1200 # sec

  @app.route ("/session")
  def hello_world (was, **form):
    if "login" not in was.request.session:
      was.request.session.set ("user_id", form.get ("hansroh"))
      # or
      was.request.session ["user_id"] = form.get ("hansroh")

If you set, alter or remove session value, session expiry is automatically
extended by app.session_timeout. But just getting value will not be extended.
If you extend explicit without altering value, you can use touch() or
set_expiry(). session.touch() will extend by app.session_timeout.
session.set_expiry (timeout) will extend by timeout value.

Once you set expiry, session auto extenstion will be disabled until
expiry time become shoter than new expiry time is calculated by
app.session_timeout.

- was.request.session.set (key, val)
- was.request.session.get (key, default = None)
- was.request.session.source_verified (): If current IP address
  matches with last IP accesss session
- was.request.session.getv (key, default = None): If not
  source_verified (), return default
- was.request.session.remove (key)
- was.request.session.clear ()
- was.request.session.keys ()
- was.request.session.values ()
- was.request.session.items ()
- was.request.session.has_key ()
- was.request.session.set_expiry (timeout)
- was.request.session.touch ()
- was.request.session.expire ()
- was.request.session.use_time ()
- was.request.session.impending (): if session timeout remains 20%


Messaging Box
----------------

**was.request.mbox** (*alias: was.mbox*)

Like Flask's flash feature, Skitai also provide messaging tool.

.. code:: python

  @app.route ("/msg")
  def msg (was):
    was.request.mbox.send ("This is Flash Message", "flash")
    was.request.mbox.send ("This is Alert Message Kept by 60 seconds on every request", "alram", valid = 60)
    return was.redirect (was.urlfor ("showmsg", "Hans Roh"), status = "302 Object Moved")

  @app.route ("/showmsg")
  def showmsg (was, name):
    return was.render ("msg.htm", name=name)

A part of msg.htm is like this:

.. code:: html

  Messages To {{ name }},
  <ul>
    {% for message_id, category, created, valid, msg, extra in was.request.mbox.get () %}
      <li> {{ mtype }}: {{ msg }}</li>
    {% endfor %}
  </ul>

Default value of valid argument is 0, which means if page called
was.request.mbox.get() is finished successfully, it is automatically deleted
from mbox.

But like flash message, if messages are delayed by next request, these
messages are save into secured cookie value, so delayed/long term valid
messages size is limited by cookie specificatio. Then shorter and fewer
messsages would be better as possible.

'was.request.mbox' can be used for general page creation like handling notice,
alram or error messages consistently. In this case, these messages
(valid=0) is consumed by current request, there's no particular size
limitation.

Also note valid argument is 0, it will be shown at next request just one
time, but inspite of next request is after hundred years, it will be
shown if browser has cookie values.

.. code:: python

  @app.before_request
  def before_request (was):
    if has_new_item ():
      was.request.mbox.send ("New Item Arrived", "notice")

  @app.route ("/main")
  def main (was):
    return was.render ("news.htm")

news.htm like this:

.. code:: html

  News for {{ app.r.username }},
  <ul>
    {% for mid, category, created, valid, msg, extra in was.request.mbox.get ("notice", "news") %}
      <li class="{{category}}"> {{ msg }}</li>
    {% endfor %}
  </ul>

- was.request.mbox.send (msg, category, valid_seconds, key=val, ...)
- was.request.mbox.get () return [(message_id, category, created_time,
  valid_seconds, msg, extra_dict)]
- was.request.mbox.get (category) filtered by category
- was.request.mbox.get (key, val) filtered by extra_dict
- was.request.mbox.source_verified (): If current IP address
  matches with last IP accesss mbox
- was.request.mbox.getv (...) return get () if source_verified ()
- was.request.mbox.search (key, val): find in extra_dict. if val
  is not given or given None, compare with category name. return
  [message_id, ...]
- was.request.mbox.remove (message_id)


Named Session & Messaging Box
------------------------------

*New in skitai version 0.15.30*

You can create multiple named session and mbox objects by mount() methods.

.. code:: python

  was.request.session.mount (
    name = None,
    session_timeout = None,
    securekey = None,
    path = None,
    domain = None,
    secure = False,
    http_only = False,
    extend = True
   )

  was.request.mbox.mount (
    name = None,
    securekey = None,
    path = None,
    domain = None,
    secure = False,
    http_only = False
  )

For example, your app need isolated session or mbox seperated
default session for any reasons, can create session named 'ADM'
and if this session or mbox is valid at only /admin URL.

.. code:: python

  @app.route("/")
  def index (was):
    was.request.session.mount ("ADM", path = '/admin')
    was.request.session.set ("admin_login", True)

    was.request.mbox.mount ("ADM", path = '/admin')
    was.request.mbox.send ("10 data has been deleted", 'warning')

SECUREKEY_STRING needn't same with app.securekey. And path, domain,
secure, http_only args is for session cookie, you can mount any
named sessions or mboxes with upper cookie path and upper cookie
domain. In other words, to share session or mbox with another apps,
path should be closer to root (/).

.. code:: python

  @app.route("/")
  def index (was):
    was.request.session.mount ("ADM", path = '/')
    was.request.session.set ("admin_login", True)

Above 'ADM' sesion can be accessed by all mounted apps because path is '/'.

Also note was.request.session.mount () is exactly same as mounting default session.

mount() is create named session or mbox if not exists, exists() is
just check wheather exists named session already.

.. code:: python

  if not was.request.session.exists (None):
    return "Your session maybe expired or signed out, please sign in again"

  if not was.request.session.exists ("ADM"):
    return "Your admin session maybe expired or signed out, please sign in again"



File Upload
---------------

.. code:: python

  FORM = """
    <form enctype="multipart/form-data" method="post">
    <input type="hidden" name="submit-hidden" value="Genious">
    <p></p>What is your name? <input type="text" name="submit-name" value="Hans Roh"></p>
    <p></p>What files are you sending? <br />
    <input type="file" name="file">
    </p>
    <input type="submit" value="Send">
    <input type="reset">
  </form>
  """

  @app.route ("/upload")
  def upload (was, *form):
    if was.request.command == "get":
      return FORM
    else:
      file = form.get ("file")
      if file:
        file.save ("d:\\var\\upload", dup = "o") # overwrite

'file' object's attributes are:

- file.path: temporary saved file full path
- file.name: original file name posted
- file.size
- file.mimetype
- file.save (into, name = None, mkdir = False, dup = "u")
- file.remove ()
- file.read ()

  * if name is None, used file.name
  * dup:

    + u - make unique (default)
    + o - overwrite


Using SQL Map with SQLPhile
---------------------------------

*New in Version 0.26.13*

SQLPhile_ is SQL generator and can be accessed from was.sql.

was.sql is a instance of sqlphile.SQLPhile.

If you want to use SQL templates, create sub directory 'sqlmaps'
and place sqlmap files.

.. code:: python

  # default engine is skitai.DB_PGSQL and also available skitai.DB_SQLITE3
  # no need call for skitai.DB_PGSQL
  app.setup_sqlphile (skitai.DB_SQLITE3)

  @app.route ("/")
  def index (was):
    q = was.sql.select (tbl_'user').get ('id, name').filter (id = 4)
    req = was.db ("@db").execute (q)
    result = req.dispatch ()

*New in skitai version 0.27*

>From version 0.27 SQLPhile_ is integrated with PostgreSQL and SQLite3.

.. code:: python

    app = Atila (__name__)
    app.setup_sqlphile (skitai.DB_PGSQL)

    @app.route ("/")
    def query (was):
      dbo = was.db ("@mypostgres")
      req = dbo.select ("cities").get ("id, name").filter (name__like = "virginia").execute ()
      result = req.dispatch ()
      response = req.dispatch (timeout = 2)
      dbo.insert ("cities").data (name = "New York").execute ().wait_or_throw ("500 Server Error")


Please, visit SQLPhile_ for more detail.

.. _SQLPhile: https://pypi.python.org/pypi/sqlphile


Registering Per Request Calling Functions
-------------------------------------------

Method decorators called automatically when each method is
requested in a app.

.. code:: python

  @app.before_request
  def before_request (was):
    if not login ():
      return "Not Authorized"

  @app.finish_request
  def finish_request (was):
    app.r.user_id
    app.r.user_status
    ...

  @app.failed_request
  def failed_request (was, exc_info):
    app.r.user_id
    app.r.user_status
    ...

  @app.teardown_request
  def teardown_request (was):
    app.r.resouce.close ()
    ...

  @app.route ("/view-account")
  def view_account (was, userid):
    app.r.user_id = "jerry"
    app.r.user_status = "active"
    app.r.resouce = open ()
    return ...

For this situation, 'was' provide app.r that is empty class instance.
app.r is valid only in current request. After end of current request.

If view_account is called, Atila execute these sequence:

.. code:: python

  try:
    try:
      content = before_request (was)
      if content:
        return content
      content = view_account (was, *args, **karg)

    except:
      content = failed_request (was, sys.exc_info ())
      if content is None:
        raise

    else:
      finish_request (was)

  finally:
    teardown_request (was)

  return content

Be attention, failed_request's 2nd arguments is sys.exc_info ().
Also finish_request and teardown_request (NOT failed_request)
should return None (or return nothing).

If you handle exception with failed_request (), return custom error
content, or exception will be reraised and Atila will handle exception.

*New in skitai version 0.14.13*

.. code:: python

  @app.failed_request
  def failed_request (was, exc_info):
    # releasing resources
    return was.response (
      "501 Server Error",
      was.render ("err501.htm", msg = "We're sorry but something's going wrong")
    )

Define Autoruns
--------------------------------

*New in skitai version 0.26.18*

You can make automation for preworks and postworks.

.. code:: python

  def pre1 (was):
    ...

  def pre2 (was):
    ...

  def post1 (was):
    ...

  @app.run_before (pre1, pre2)
  @app.run_after (post1)
  def index (was):
    return was.render ('index.html')

@app.run_before can return None or responsable contents for
aborting all next run_before and main request.

@app.run_after return will be ignored

Define Conditional Prework
-------------------------------

*New in skitai version 0.26.18*

@app.if~s are conditional executing decorators.

.. code:: python

  def reload_config (was, path):
    ...

  @app.if_file_modified ('/opt/myapp/config', reload_config, interval = 1)
  def index (was):
    return was.render ('index.html')

@app.if_updated need more explaination.


Inter Process Update Notification and Consequences Automation
----------------------------------------------------------------

*New in skitai version 0.26.18*

@app.if_updated is related with skitai.register_states (), was.setlu()
and was.getlu() and these are already explained was cache contorl
part. And Atila app can use more conviniently.

These're used for mostly inter-process notification protocol.

Before skitai.run (), you should define updatable objects as
string keys:

.. code:: python

  skitai.register_states ("weather-news", ...)

Then one process update object and update time by setlu ().

.. code:: python

  @app.route ("/")
  def add_weather (was):
    was.db.execute ("insert into weathers ...")
    was.setlu ("weather-news")
    return ...

This update time stamp will be recorded in shared memory, then all skitai
worker processes can catch this update by comparing previous last update
time and automate consequences like refreshing cache.

.. code:: python

  def reload_cache (was, key):
    ...

  @app.if_updated ('weather-news', reload_cache)
  def index (was):
    return was.render ('index.html')


App Lifecycle Hook
----------------------

These app life cycle methods will be called by this order,

- before_mount (wac): when app imported on skitai server started
- mounted (*was*): called first with was (instance of wac)
- mounted_or_reloaded (*was*): called with was (instance of wac)
- loop whenever app is reloaded,

  - oldapp.before_reload (*was*)
  - newapp.reloaded (*was*)
  - mounted_or_reloaded (*was*): called with was (instance of wac)

- before_umount (*was*): called last with was (instance of wac),
  add shutting down process
- umounted (wac): when skitai server enter shutdown process

Please note that first arg of startup, reload and shutdown is *wac*
not *was*. *wac* is Python Class object of 'was', so mainly used
for sharing Skitai server-wide object via was.object before
instancelizing to *was*.

.. code:: python

  @app.before_mount
  def before_mount (wac):
    logger = wac.logger.get ("app")
    # OR
    logger = wac.logger.make_logger ("login", "daily")
    config = wac.config
    wac.register ("loginengine", SNSLoginEngine (logger))
    wac.register ("searcher", FulltextSearcher (wac.numthreads))

  @app.before_reload
  def before_remount (wac):
    wac.loginengine.reset ()

  @app.umounted
  def before_umount (wac):
    wac.umounted.close ()

    wac.unregister ("loginengine")
    wac.unregister ("searcher")

You can access numthreads, logger, config from wac.

As a result, myobject can be accessed by all your current app
functions even all other apps mounted on Skitai.

.. code:: python

  # app mounted to 'abc.com/register'
  @app.route ("/")
  def index (was):
    was.loginengine.check_user_to ("facebook")
    was.searcher.query ("ipad")

  # app mounted to 'def.com/'
  @app.route ("/")
  def index (was):
    was.searcher.query ("news")

*Note:* The way to mount with host, see *'Mounting With Virtual
Host'* chapter below.

It maybe used like plugin system. If a app which should be mounted
loads pulgin-like objects, theses can be used by Skitai server
wide apps via was.object1, was.object2,...

*New in skitai version 0.26*

If you have databases or API servers, and want to create cache object
on app starting, you can use @app.mounted decorator.

.. code:: python

  def create_cache (res):
    d = {}
    for row in res.data:
      d [row.code] = row.name
    app.store.set ('STATENAMES', d)

  @app.mounted
  def mounted (was):
    was.db ('@mydb', callback = create_cache).execute ("select code, name from states;")
    # or use REST API
    was.get ('@myapi/v1/states', callback = create_cache)
    # or use RPC
    was.rpc ('@myrpc/rpc2', callback = create_cache).get_states ()

  @app.reloaded
  def reloaded (was):
    mounted (was) # same as mounted

  @app.before_umount
  def before_umount (was):
    was.delete ('@session/v1/sessions', callback = lambda x: None)

But both are not called by request, you CAN'T use request related
objects like was.request, was.request.cookie etc. And SHOULD use callback
because these are executed within Main thread.


Login and Permission Helper
------------------------------

*New in skitai version 0.26.16*

You can define login & permissoin check handler,

.. code:: python

  @app.login_handler
  def login_handler (was):
    if was.request.session.get ("demo_username"):
      return

    if was.request.args.get ("username"):
      if not was.verify_csrf ():
        raise was.Error ("400 Bad Request")

      if was.request.args.get ("signin"):
        user, level = authenticate (username = was.request.args ["username"], password = was.request.args ["password"])
        if user:
          was.request.session.set ("demo_username", user)
          was.request.session.set ("demo_permission", level)
          return

        else:
          was.request.mbox.send ("Invalid User Name or Password", "error")
    return was.render ("login.html", user_form = forms.DemoUserForm ())

  @app.permission_check_handler
  def permission_check_handler (was, perms):
    if was.request.session.get ("demo_permission") in perms:
      raise was.Error ("403 Permission Denied")

  @app.staff_member_check_handler
  def staff_check_handler (was):
    if was.request.session.get ("demo_permission") not in ('staff'):
      raise was.Error ("403 Staff Permission Required")

If you are using JWT you can integrate with this, And it
is replacable instead of app.authorization_required.

.. code:: python

  @app.permission_check_handler
  def permission_check_handler (was, perms):
      claims = was.request.JWT
      if "err" in claims: return claims ["err"]
      if not perms:
        return # permit
      for p in claims ["levels"]:
          if p in perms:
              return # permit
      raise was.Error ("403 Permission Denied")

And use it for your resources if you need,

.. code:: python

  @app.route ("/")
  @app.permission_required (["admin"])
  @app.login_required
  def index (was):
    return "Hello"

  @app.staff_member_required
  def index2 (was):
    return "Hello"

If every thing is OK, it *SHOULD return None, not True*.

'clarify_permission' and 'clarify_login' will ignore any raise
HTTP error but just try run 'permission_check_handler'. You can
set request.user object if user has permission.

.. code:: python

  @app.permission_check_handler
  def permission_check_handler (was, perms):
      claims = was.request.JWT
      if "err" in claims:
        return claims ["err"]
      was.request.user = claims ['uid']
      if not perms:
        return # permit
      raise was.Error ("403 Permission Denied")

  @app.clarify_permission # ignore http error on handler
  def index (was):
    if not was.request.user:
      return 'permission denied'
    return 'permission granted'


Conditional Permission Control
````````````````````````````````````````````````````

*New in version 0.3*

Let's assume you manage permission by user levels: admin,
staff and user.

.. code:: python

  @app.permission_check_handler
  def permission_check_handler (was, perms):
    claims = was.request.JWT
    if "err" in claims:
      return claims ["err"]

    if not perms:
      return # permit for anyone who is authorized
    if claims ["level"] == "admin":
      return # premit always
    if "admin" in perms:
      raise was.Error ("403 Permission Denied")
    if "staff" in prems and claims ["level"] != "staff":
        raise was.Error ("403 Permission Denied")

.. code:: python

  @app.route ("/animals/<id>")
  @app.permission_required ([], id = ["staff"])
  def animals (was, id = None):
      id = id or was.request.JWT ["userid"]

This resources required any permission for "/animals/" or
"/animals/me". But '/animals/100' is required 'staff' permission.
It may make permission control more simpler.

Also you can specify premissions per request methods.

.. code:: python

  @app.route ("/animals/<id>", methods = ["POST", "DELETE"])
  @app.permission_required (['user'], id = ["staff"], DELETE = ["admin"])
  def animals (was, id = None):
      id = id or was.request.JWT ["userid"]

This resources required 'user' permission for "/animals/" or "/animals/me".
'/animals/100' is required 'staff' permission. It may make
permission control more simpler.


Testpassing
`````````````````````````

Also you can test if user is valid,

.. code:: python

  def is_superuser (was):
    if was.user.username not in ('admin', 'root'):
      reutrn was.response ("403 Permission Denied")

  @app.testpass_required (is_superuser)
  def modify_profile (was):
    ...

The binded testpass_required function can return,

- True or None: continue request
- False: response 403 Permission Denied immediately
- Responsable object: response object immediately


Cross Site Request Forgery Token (CSRF Token)
------------------------------------------------

*New in skitai version 0.26.16*

At template, insert CSRF Token,

.. code:: html

  <form>
  {{ was.csrf_token_input }}
  ...
  </form>

then verify token like this,

.. code:: python

  @app.before_request
  def before_request (was):
    if was.request.args.get ("username"):
      if not was.verify_csrf ():
        return was.response ("400 Bad Request")

Or use decorator,

.. code:: python

  @app.csrf_verification_required
  def before_request (was):
    ...


Making JWT Token
--------------------

.. code:: python

  @app.route ('/make_token')
  def make_token (was)
      t = was.encode_jwt ({'iss': 'example.com', 'exp': time.time () + 3600})

  @app.route ('/verify_token')
  def make_token (was, token)
      payload = was.decode_jwt (token)

At your client,

.. code:: python

  from atila.was import generate_otp

  generate_otp (secret_key)


Making One-Time Password
-----------------------------

*New in skitai version 0.35.0*

.. code:: python

  def check_otp (was):
     if not was.verify_otp (was.request.get_header ('x-otp')):
        raise was.Error ('403 Unauthorized')

  @app.route ('/admin-task')
  @app.testpass_required (check_otp)
  def task (was)
      ...

At your client,

.. code:: python

  from atila.was import generate_otp

  generate_otp (secret_key)


Making One-Time Token
--------------------------------------

*New in skitai version 0.26.17*

For creatiing onetime link url, you can convert your data to
signatured token string.

Note: Like JWT token, this token contains data and decode easily,
then you should not contain important information like password or
PIN. This token just make sure contained data is not altered by
comparing signature which is generated with your app scret key.

.. code:: python

  @app.route ('/password-reset')
  def password_reset (was)
    if was.request.args ('username'):
      username = "hans"
      token = was.encode_ott (username, 3600, "pwrset") # valid within 1 hour
      pw_reset_url = was.urlfor ('reset_password', token)
      # send email
      return was.render ('done.html')

    if was.request.args ('token'):
      username = was.decode_ott (was.request.args ['token'])
      if not username:
        return was.response ('400 Bad Request')
      # processing password reset
      ...

If you want to expire token explicit, add session token key

.. code:: python

  # valid within 1 hour and create session token named '_reset_token'
  token = was.encode_ott ("hans", 3600, 'rset')
  >> kO6EYlNE2QLNnospJ+jjOMJjzbw?fXEAKFgGAAAAb2JqZWN0...

  username = was.decode_ott (token)
  >> "hans"

  # if processing is done and for revoke token,
  was.revoke_ott (token)


App Event Handling
---------------------

Most of Atila's event handlings are implemented with
excellent `event-bus`_ library.

*New in skitai version 0.26.16*, *Availabe only on Python 3.5+*

.. code:: python

  import atila

  @app.on ("request:failed")
  def request_failed_handler (was, exc_info):
    print ("I got it!")

There're some app events.

- before_mount
- mounted
- before_reload
- reloaded
- before_umount
- umounted
- mounted_or_reloaded

- request:before_start
- request:failed
- request:success
- request:teardown
- request:finished

.. _`event-bus`: https://pypi.python.org/pypi/event-bus


App Storage
----------------------------------------

*app.store* object is ditionary like object and provide
thread-safe accessing.

It SHOULD be simple primitive value like string, int, float.
About dictionary or class instances, It can't give no guarantee
for thread-safe.

.. code:: python

  def  (was, current_users):
    total = app.store.get ("total-user")
    app.store.set ("total-user", total + 1)
    ...


Inverval Base App Maintenancing
---------------------------------------------

If you need interval base maintaining jobs,

.. code:: python

  app.config.MAINTAIN_INTERVAL = 60  # seconds, default is 60
  app.store.set ("num-nodes", 0) # thread safe store

  @app.maintain (10, threading = False) # execute every 10 maintaining (500 sec.)
  def maintain_num_nodes (was, now, count):
    ...
    num_nodes = was.getlu ("cluster.num-nodes")
    if app.store ["num-nodes"] != num_nodes:
      app.store ["num-nodes"] = num_nodes
      app.broadcast ("cluster:num_nodes")

You can add multiple maintain jobs but maintain function
names is SHOULD be unique.


Creating and Handling Custom Event
---------------------------------------

*Availabe only on Python 3.5+*

For creating custom event and event handler,

.. code:: python

  @app.on ("user-updated")
  def user_updated (was, user):
    ...

For emitting,

.. code:: python

  @app.route ('/users', methods = ["POST"])
  def users (was):
    args = was.request.json ()
    ...

    app.emit ("user-updated", args ['userid'])

    return ''

If event hasn't args, you can use `emit_after` decorator,

.. code:: python

  @app.route ('/users', methods = ["POST"])
  @app.emit_after ("user-updated")
  def users (was):
    args = was.request.json ()
    ...
    return ''

Using this, you can build automatic excution chain,

.. code:: python

  @app.on ("photo-updated")
  def photo_updated (was):
    ...

  @app.on ("user-updated")
  @app.emit_after ("photo-updated")
  def user_updated (was):
    ...

  @app.route ('/users', methods = ["POST"])
  @app.emit_after ("user-updated")
  def users (was):
    args = was.request.json ()
    ...
    return ''


Cross App Communication & Accessing Resources
----------------------------------------------

Skitai prefer spliting apps to small microservices and mount
them each. This feature make easy to move some of your mounted
apps move to another machine. But this make difficult to
communicate between apps.

Here's some helpful solutions.


Accessing App Object Properties
`````````````````````````````````

*New in skitai version 0.26.7.2*

You can mount multiple app on Skitai, and maybe need to another
app is mounted seperatly.

.. code:: python

  skitai.mount ("/", "main.py")
  skitai.mount ("/query", "search.py")

And you can access from filename of app from each apps,

.. code:: python

  search_app = was.apps ["search"]
  save_path = search_app.config.save_path


URL Building for Resource Accessing
````````````````````````````````````

*New in skitai version 0.26.7.2*

If you mount multiple apps like this,

.. code:: python

  skitai.mount ("/", "main.py")
  skitai.mount ("/search", "search.py")

For building url in `main.py` app from a query function of
`search.py` app, you should specify app file name with colon.

.. code:: python

  was.urlfor ('search:query', "Your Name") # returned '/search/query?q=Your%20Name'

And this is exactly same as,

  was.apps ["search"].build_url ("query", "Your Name")

But this is only functioning between apps are mounted
within same host.


Custom Error Handling
``````````````````````````````````````````

*New in skitai version 0.26.7*

.. code:: python

  @app.default_error_handler
  def default_error_handler (was, error):
    return "<h1>{code} {message}</h1>".format (**error)

Or you can respond with JSON only.

.. code:: python

  @app.error_handler (404)
  def not_found (was, error):
    return "<h1>{code} {message}</h1>".format (**error)

- code: error code
- message: error message
- detail: error detail
- mode: debug or normal
- debug: debug info
- time: time when error occured
- url: request url
- software: server name and version
- traceback: available only if app.debug = True or None

Note that custom error templates can not be used before
routing to the app.


Communication with Event
``````````````````````````

*New in skitai version 0.26.10*
*Availabe only on Python 3.5+*

'was' can work as an event bus using app.on_broadcast ()
- was.broadcast () pair. Let's assume that an users.py app
handle only user data, and another photo.py app handle only
photos of users.

.. code:: python

  skitai.mount ('/users', 'users.py')
  skitai.mount ('/photos', 'photos.py')

If a user update own profile, sometimes photo information
should be updated.

At photos.py, you can prepare for listening to 'user:data-added'
event and this event will be emited from 'was'.

.. code:: python

  @app.on_broadcast ('user:data-added')
  def refresh_user_cache (was, userid):
    was.sqlite3 ('@photodb').execute ('update ...').wait ()

and uses.py, you just emit 'user:data-added' event to 'was'.

.. code:: python

  @app.route ('/users', methods = ["PATCH"])
  def users (was):
    args = was.request.json ()
    was.sqlite3 ('@userdb').execute ('update ...').wait ()

    # broadcasting event to all mounted apps
    was.broadcast ('user:data-added', args ['userid'])

    return was.response (
      "200 OK",
      json.dumps ({}),
      [("Content-Type", "application/json")]
    )

If resource always broadcasts event without args, use
`broadcast_after` decorator.

.. code:: python

  @app.broadcast_after ('some-event')
  def users (was):
    args = was.request.json ()
    was.sqlite3 ('@userdb').execute ('update ...').wait ()

Note that this decorator cannot be routed by app.route ().

**CAUTION**: Do not use request specific variables - like request,
cookie, session and etc in event handler.


CORS (Cross Origin Resource Sharing) and Preflight
-----------------------------------------------------

For allowing CORS, you should do 2 things:

- set app.access_control_allow_origin
- allow OPTIONS methods for routing

.. code:: python

  app = Atila (__name__)
  app.access_control_allow_origin = ["*"]
  # OR specific origins
  app.access_control_allow_origin = ["http://www.skitai.com:5001"]
  app.access_control_max_age = 3600

  @app.route ("/post", methods = ["POST", "OPTIONS"])
  def post (was):
    args = was.request.json ()
    return was.jstream ({...})


If you want function specific CORS,

.. code:: python

  app = Atila (__name__)

  @app.route (
   "/post", methods = ["POST", "OPTIONS"],
   access_control_allow_origin = ["http://www.skitai.com:5001"],
   access_control_max_age = 3600
  )
  def post (was):
    args = was.request.json ()
    return was.jstream ({...})


WWW-Authenticate
-------------------

*Changed in version 0.15.21*

  - removed app.user and app.password
  - add app.users object has get(username) methods like dictionary

Atila provide simple authenticate for administration or
perform access control from other system's call.

Authentication On Specific Methods
`````````````````````````````````````````

Otherwise you can make some routes requirigng authorization
like this:

.. code:: python

  @app.route ("/hello/<name>", authenticate = "digest")
  def hello (was, name = "Hans Roh"):
    return "Hello, %s" % name

Or you can use @app.authorization_required decorator.

.. code:: python

  @app.route ("/hello/<name>")
  @app.authorization_required ("digest")
  def hello (was, name = "Hans Roh"):
    return "Hello, %s" % name

Available authorization methods are basic, digest and bearer.


Password Provider
````````````````````

You can provide password and user information getter by 2 ways.

First, users object

.. code:: python

  # users object shoukd have get(username) method
  app.users = {"hansroh": ("1234", False)}

Second, use decorator

.. code:: python

  @app.authorization_handler
  def auth_handler (was, username):
    ...
    return ("1234", False)

The return object can be:

  - (str password, boolean encrypted, obj userinfo)
  - (str password, boolean encrypted)
  - str password
  - None if authorization failed

If you use encrypted password, you should use digest authorization
and password should encrypt by this way:

.. code:: python

  from hashlib import md5

  encrypted_password = md5 (
    ("%s:%s:%s" % (username, realm, password)).encode ("utf8")
  ).hexdigest ()


If authorization is successful, app can access username and userinfo
vi was.request.user.

  - was.request.user.name
  - was.request.user.realm
  - was.request.user.info

If your server run with SSL, you can use app.authorization = "basic",
otherwise recommend using "digest" for your password safety.

Authentication On Entire App
```````````````````````````````

For your convinient, you can set authorization requirements to app level.

.. code:: python

  app = Atila (__name__)

  app.authenticate = "digest"
  app.realm = "Partner App Area of mysite.com"
  app.users = {"app": ("iamyourpartnerapp", 0, {'role': 'root'})}

  @app.route ("/hello/<name>")
  def hello (was, name = "Hans Roh"):
    return "Hello, %s" % name

If app.authenticate is set, all routes of app require authorization
(default is False).


(JWT) Bearer Authorization
--------------------------------------

To making JWT token, your app need securekey.

.. code:: python

  app.securekey = '5b2c4f18-01fd-4b85-8cfa-01827878562f'

.. code:: python

  was.encode_jwt ({"username": "hansroh", "exp": time.time () + 3600, ...})
  >> eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXV...

Note: was.decode_jwt (token) is also available.

Then client should add 'Authorization' to API request like,

.. code:: python

  Authorization: Bearer eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXV...

And use bearer_handler decorators.

.. code:: python

  @app.bearer_handler
  def bearer_handler (was, token):
    # if not JWT token,
    claims = parse_your_token_yourself (token)
    # if JWT, just use was.request.JWT
    claims = was.request.JWT
    if "err" in claims:
      return claims ["err"]

  @app.route ("/api/v1/predict")
  @app.authorization_required ("bearer")
  def predict (was):
    # now you can use these
    was.request.user # hansroh
    was.request.JWT # dict {"username": "hansroh", "exp": 2900...}

For your convinient, above bearer_handler is registered as
default handler, but you can still override it.

Implementing XMLRPC Service
-----------------------------

Client Side:

.. code:: python

  import aquests

  stub = aquests.rpc ("http://127.0.0.1:5000/rpc")
  stub.add (10000, 5000)
  fetchall ()

Server Side:

.. code:: python

  @app.route ("/add")
  def index (was, num1, num2):
    return num1 + num2

Is there nothing to diffrence? Yes. Atila app methods are also
used for XMLRPC service if return values are XMLRPC dumpable.


Implementing gRPC Service
-----------------------------

Client Side:

.. code:: python

  import aquests
  import route_guide_pb2

  stub = aquests.grpc ("http://127.0.0.1:5000/routeguide.RouteGuide")
  point = route_guide_pb2.Point (latitude=409146138, longitude=-746188906)
  stub.GetFeature (point)
  aquests.fetchall ()

Server Side:

.. code:: python

  import route_guide_pb2

  def get_feature (feature_db, point):
    for feature in feature_db:
      if feature.location == point:
        return feature
    return None

  @app.route ("/GetFeature")
  def GetFeature (was, point):
    feature = get_feature(db, point)
    if feature is None:
      return route_guide_pb2.Feature(name="", location=point)
    else:
      return feature

  if __name__ == "__main__":

  skitai.mount = ('/routeguide.RouteGuide', app)
  skitai.urn ()


For an example, here's my tfserver_ for Tensor Flow Model Server.

For more about gRPC and route_guide_pb2, go to `gRPC Basics - Python`_.

Note: I think I don't understand about gRPC's stream request and
response. Does it means chatting style? Why does data stream has
interval like GPS data be handled as stream type? If it is chat style
stream, is it more efficient that use proto buffer on Websocket protocol?
In this case, it is even possible collaborating between multiple gRPC
clients.

.. _`gRPC Basics - Python`: http://www.grpc.io/docs/tutorials/basic/python.html
.. _tfserver: https://pypi.python.org/pypi/tfserver


Logging and Traceback
------------------------

.. code:: python

  @app.route ("/")
  def sum ():
    was.log ("called index", "info")
    try:
      ...
    except:
      was.log ("exception occured", "error")
      was.traceback ()
    was.log ("done index", "info")

Note inspite of you do not handle exception, all app exceptions will
be logged automatically by Atila. And it includes app importing and
reloading exceptions.

- was.log (msg, category = "info")
- was.traceback (id = "") # id is used as fast searching log line
  for debug, if not given, id will be *Global transaction ID/Local
  transaction ID*


Exposing API Specification
-----------------------------------------

For debugging and helping to write API specification, Atila
expose all specification of each resources.

.. code:: python

  @app.route ("/isitok/<code>/<type>", methods = ["GET", "POST", "PATCH", "OPTIONS"])
  def isitok (was, code, type):
    return was.API (result = "ok")

That will return,

.. code:: python

  {"result": "ok"}

If you set like this,

.. code:: python

  app.expose_spec = True

Then will be returned with spec,

.. code:: python

  {
    "result": "ok",
    "__spec__": {
        'id': 'isitok',
        'routeopt': {
            'methods': ["GET", "POST", "PATCH", "OPTIONS"],
            'route': '/isitok/<code>/<type>',
            'args': ['code', 'type'],
            'keywords': None,
            'urlargs': 2,
            'mntopt': {
                'module_name': 'services.v1.apis',
                'point': '/v1/apis'
            }
        },
        'auth_requirements': [],
        'parameter_requirements': {},
        'doc': None,
        'current_request': {
            'http_method': 'GET',
            'http_version': '1.1',
            'uri': '/v1/apis/isitok'
        }
     }
  }

Note: This will only work at your local machine (IP address
starts with 127.0.0.).

App Testing
---------------------------

For automated test, Atila provide test_client (). Test client
will just emulate client-server communication.

myapp.py is:

.. code:: python

  app = Atila (__name__)

  @app.route ("/")
  def index (was):
    return "<h1>something</h1>"

  @app.route ("/apis/pets/<int:id>")
  def pets (was, id):
    return was.API ({"id": id, "kind": "dog", "name": "Monk"})

  if __name__ == "__main__":
    skitai.mount ("/", app)
    skitai.run (port = 5000)

If you run unittest with pytest, your test script is like this.

.. code:: python

  def test_myapp ():
    from myapp import app

    with app.test_client ("/", approot = ".") as cli:
      # html request
      resp = cli.get ("/")
      assert "something" in resp.text

      # api call
      stub = cli.api ()
      resp = stub.apis.pets (45).get ()
      assert resp.data ["id"] == 45

      resp = stub.apis.pets (100).get ()
      assert resp.data ["id"] == 100

Now run pytest.

Above code works fine if your app is composed with single
file. If your app has sub modules, app will raise relative
import related error.

..code:: python

  import skitai
  import atila

  def test_myapp ():
    with skitai.preference () as pref:
      app = atila.load ("./mayapp/app.py", pref)

If your app is located as your module's export/skitai/__export__.py,

..code:: python

  import your_module
  app = atila.load (your_module, pref)

Now, you are ready to test.

Note: Internal requests like was.get, was.post, was.jsonrpc
and database engine operations will work with synchronous
mode and may will be slow.



VueJS with Skito-Atila
==========================

Without Module Bundlers
---------------------------------

I recently wrote about `Single File Component Based Website`_.

It is based on `FranckFreiburger/http-vue-loader`_ and I made
some examplary templates.

.. _`Single File Component Based Website`: https://gitlab.com/hansroh/http-sfc
.. _`FranckFreiburger/http-vue-loader`: https://github.com/FranckFreiburger/http-vue-loader



With Bundlers
-------------------------

I prefer to build VueJS as frontend app and Atila as backend.

Basic project directory stucture is,

project root

- frontend (vue project)

  * <dist>
  * <node_modules>
  * <src>
  * <public>
  * package.json
  * vue.config.js
  * ...

- backend

  * <services>
  * serve.py

The core line sof serve.py,

.. code:: python

  from atila import Atila
  import skitai
  import os
  import sys
  from services import api

  app = Atila (__name__)
  app.mount ("/api/v1", api) # for backend API service

  @app.route ("/<path:path>")
  def vapp (was, path = None):
      return was.File (skitai.joinpath ("../frontend", "dist", "index.html"), "text/html")

  if __name__ == "__main__":
      with skitai.preference () as pref:
        pref.securekey = None
        pref.max_client_body_size = 2 << 32
        pref.access_control_allow_origin = ["127.0.0.1:5000"]

        if "---production" not in sys.argv:
            pref.debug = True
            pref.use_reloader = True
            pref.access_control_allow_origin.append ("127.0.0.1:8080")

        skitai.mount ("/", app)
        skitai.mount ("/", "../frontend/dist", pref = pref)
      skitai.run (name = "myapp", port = 5000)

This skitai starting script do these things,

- If requested URL is one of atila routes, then routed to it
- Otherwise all URL is routed to vue SPA (dist/index.html)
- All static root mounted to frontend/dist directory
  for service compiled js and css by webpack

You can develop vue app by,

.. code:: bash

  npm run serve
  # generally use port 8080

And Atila app developing by,

.. code:: bash

  python3 ../backend/serve.py
  # use port 5000

Finally,

.. code:: bash

  npm run build
  python3 ../backend/serve.py


If you interest about thi stuff, you can have reference_
which I personally build as bolier-plate. But it is just planning stage.

.. _reference: https://gitlab.com/hansroh/skito-vue


Working With Jinja2 Template Engine
==============================================================

If you want to use Jinja2 template engine, install first.

.. code:: bash

  pip3 install -U jinja2

Although You can use any template engine, Skitai provides was.render()
which uses Jinja2_ template engine. For providing arguments to Jinja2,
use dictionary or keyword arguments.

.. code:: python

  return was.render ("index.html", choice = 2, product = "Apples")

  #is same with:

  return was.render ("index.html", {"choice": 2, "product": "Apples"})

  #BUT CAN'T:

  return was.render ("index.html", {"choice": 2}, product = "Apples")

Directory structure sould be:

- /project_home/app.py
- /project_home/templates/index.html

Within template, you can access `was` and aliases for your convinient.

- was
- app
- request: alias for was.request
- response: alias for was.response
- context: namespace for given keyword arguments (or dictionary keys)

Note that these names cannot ne used as context variable name.

Also available registered with @app.template_global decorator and
given keyword arguments (or dictionary keys).

.. code:: html

  {{ request.cookie.username }} choices item {{ request.ARGS.get ("choice", "N/A") }}.

  <a href="{{ was.urlfor ('checkout', context.choice) }}">Proceed</a>

Also 'was.r' is can be useful in case threr're lots
of render parameters.

.. code:: python

  app.r.product = "Apple"
  app.r.howmany = 10

  return was.render ("index.html")

And at jinja2 template,

.. code:: html

  Checkout for {{ app.r.howmany }} {{ app.r.product }}{{ app.r.howmany > 1 and "s" or ""}}


If you want modify Jinja2 envrionment, can through
app.jinja_env object.

.. code:: python

  def generate_form_token ():
    ...

  app.jinja_env.globals['form_token'] = generate_form_token

And this is same as,

.. code:: python

  @app.template_global ('form_token')
  def generate_form_token ():
    ...


*New in skitai version 0.15.16*

Added new app.jinja_overlay () for easy calling
app.jinja_env.overlay ().

Recently JS HTML renderers like Vue.js, React.js
have confilicts  with default jinja mustache variable.
In this case you mightbe need change it.

.. code:: python

  app = Atila (__name__)
  app.debug = True
  app.use_reloader = True
  app.jinja_overlay (
    variable_start_string = "{{",
    variable_end_string = "}}",
    block_start_string = "{%",
    block_end_string = "%}",
    comment_start_string = "{#",
    comment_end_string = "#}",
    line_statement_prefix = "%",
    line_comment_prefix = "%%",
    **kargs # Jinja2 Environment arguments
  )

To add Jinja2 extensions,

.. code:: python

  app.add_jinja_ext ('jinja2.ext.i18n')

Currently, Atila use "jinja2.ext.do", "jinja2.ext.loopcontrols" defaultly.

If you want remove extensions,

.. code:: python

  app.jinja_overlay (extensions = [])


.. _Jinja2: http://jinja.pocoo.org/
.. _`Vue.js`: https://vuejs.org/


Using Skitai Async Requests Services Working With Jinja2 Template
---------------------------------------------------------------------------
If you want to use Jinja2 template engine, install first.

.. code:: bash

  pip3 install -U jinja2

Basic usage is here_.

.. _here: https://pypi.org/project/skitai/#skitai-was-services

Async request's benefit will be maximied at your view template
rather than your controller. At controller, you just fire your
requests and get responses at your template.

.. code:: python

  @app.route ("/")
  @app.login_required
  def intro (was):
    app.r.aa = was.get ("https://example.com/blur/blur")
    app.r.bb = was.get ("https://example.com/blur/blur/more-blur")
    return was.render ('template.html')

Your template,

.. code:: html

  {% set response = app.r.aa.dispatch () %}
  {% if response.status == 3 %}
    {{ was.response.throw ("500 Internal Server Error") }}
  {% endif %}

  {% if response.status_code == 200 %}
    {% for each in response.data %}
      ...
    {% endfor %}
  {% endif %}

*Available only with Atila*

Shorter version is for dispatch and throw HTTP error,

.. code:: html

  {% set response = app.r.aa.dispatch_or_throw ("500 Internal Server Error") %}


Registering Global Template Function
-------------------------------------------------------------

*New in skitai version 0.26.16*

template_global decorator makes a function possible to use
in your template,

.. code:: python

  @app.template_global ("test_global")
  def test (was):
    return ", ".join.(was.request.args.keys ())

At template,

.. code:: html

  {{ test_global () }}

Note that all template global function's first parameter
should be *was*. But when calling, you SHOULDN't give *was*.


Registering Jinja2 Filter
--------------------------------------------------------------

*New in skitai version 0.26.16*

template_filter decorator makes a function possible
to use in your template,

.. code:: python

  @app.template_filter ("reverse")
  def reverse_filter (s):
    return s [::-1]

At template,

.. code:: html

  {{ "Hello" | reverse }}


Custom Error Template
--------------------------------------------------------------

*New in skitai version 0.26.7*

.. code:: python

  @app.default_error_handler
  def default_error_handler (was, error):
    return was.render ('default.htm', error = error)

  @app.error_handler (404)
  def not_found (was, error):
    return was.render ('404.htm', error = error)

Template file 404.html is like this:

.. code:: html

  <h1>{{ error.code }} {{ error.message }}</h1>
  <p>{{ error.detail }}</p>
  <hr>
  <div>URL: {{ error.url }}</div>
  <div>Time: {{ error.time }}</div>

Note that custom error templates can not be used before
routing to the app.


Working With Chameleon Template Engine
==============================================================

Chameleon_ is an beautiful HTML/XML template engine.

For using this engine you install first.

.. code:: bash

    pip3 install -U chameleon

If you save Chameleon template with '.pt' or '.ptal'
extensions at templates directory, Atila will render
this template with Chameleon.

.. _Chameleon: : https://pypi.org/project/Chameleon/


Working With Django
===========================================

*New in skitai version 0.26.15*

I barely use Django, but recently I have opportunity using
Django and it is very fantastic and especially impressive
to Django Admin System.

Here are some examples collaborating with Djnago and Atila.

Before it begin, you should mount Django app,

.. code:: python

  # mount django admin
  with skitai.preference () as pref:
    pref.use_reloader = True
    pref.use_debug = True
    # '/' mapped with django.admin in urls.py
    skitai.mount ("/admin", 'django/wsgi.py', 'application', pref)

  # mount main app
  with skitai.preference () as pref:
    pref.use_reloader = True
    pref.use_debug = True
    skitai.mount ('/', 'app.py', pref = pref)

  skitai.run ()

When Django app is mounted, these will be processed.

1. add django project root path will be added to sys.path
2. app is mounted
3. database alias (@mydjangoapp) will be created as
   base name of django project root

Using Django Models
------------------------------------

You can use also Django models without mount app.

First of all, you should specify django setting with
alias for django database engine.

.. code:: python

  skitai.alias ("@django", skitai.DJANGO, "myapp/settings.py")

Then call django.setup ()  and you can use your models,

.. code:: python

  import django
  django.setup () # should call
  from mydjangoapp.photos import models

  @app,route ('/django/hello')
  def django_hello (was):
    models.Photo.objects.create (user='Hans Roh', title = 'My Photo')
    result = models.Photo.filter (user='hansroh').order_by ('-create_at')

You can use Django Query Set as SQL generator for
Skitai's asynchronous query execution. But it has
some limitations.

- just vaild only select query and prefetch_related ()
- effetive only to PostgreSQL and SQLite3 (but SQLite3
  dose not support asynchronous execution, so it is practically meaningless)

.. code:: python

  from mydjangoapp.photos import models

  @app,route ('/hello')
  def django_hello (was):
    query = models.Photo.objects.filter (topic=1).order_by ('title')
    return was.jstream (was.sqlite3 ("@entity").execute (query).dispatch ().data, 'data')


How To
================

Response All Errors As JSON
--------------------------------------

.. code:: python

  @app.default_error_handler
  def default_error_handler (was, error):
    code = error ["errno"] or str (error ["code"]) + '00'
    return was.Fault (
      error ["message"].lower (), code, None,
      error ["detail"], exc_info = error ["traceback"]
    )


Links
======

- `GitLab Repository`_
- Bug Report: `GitLab issues`_

.. _`GitLab Repository`: https://gitlab.com/hansroh/atila
.. _`GitLab issues`: https://gitlab.com/hansroh/atila/issues


Change Log
============

- 0.8  (Feb, 2020)

  - add request stream feature, @app.route (..., input_stream = True)
  - add was.Queue
  - add atila.service
  - fix was.pipe ()
  - add generator based coroutine and @app.coroutine
  - was.g and app.r has benn deprecated, use app.g and app.r
  - add app.r for current request context, was.g is changed to global
    app context with thread-safe
  - add was.pipe ()
  - @app.inspect can inspect JSON data
  - @app.maintain can have threading option
  - remove *400 Not My Fault* with assert
  - rename from @app.require to @app.inspect but still valid
  - @app.maintain can have interval parameter
  - add was.Media () and was.Mounted ()
  - add was.render_or_Map ()
  - add was.Map () and was.ThreadPass ()
  - add was.static and was.media
  - both \_\_setup\_\_ and \_\_mount\_\_ can have mntopt argument optionally
  - add was.Static ()
  - add *400 Not My Fault* with assert
  - add notags and safes arguments to @app.require
  - now, csrf token uses cookie not session and kept with browser
  - add remove_csrf ()
  - fix corequest cache sync
  - update, config.MINIFY_HTML = None (default) | 'strip' | 'minify'
  - add @app.csrf_verification_required
  - add '@app.clarify_permission' and '@app.clarify_login' decorators
  - add \_\_setup\_\_ hook for service packages.\_\_init\_\_.py

- 0.7 (Dec, 2019)

  - fix <path> type routing
  - change URL build alias from was.urlspec ()
  - change URL build alias from was.ab () to was.urlfor ()
  - add alias was.urlpatch () for was.partial () for clarity
  - add session.impending () and session.use_time ()
  - change default options for Jinja2
  - change session key name
  - fix session expireation
  - add extend param to session.mount ()
  - add was.render_or_API ()
  - add was.request.acceptables and was.request.acceptable (media)
  - fix @app.fix testpass_required when reloading
  - change session.mount spec
  - fix multiple mount bug related `enable_namespace`
  - fix websocket bug related `enable_namespace`
  - `app.auto_mount` was deprecated
  - default value of  `app.enable_namespace` has been
    from False to True. ACTION REQUIRED, lower version
    incompatible

- 0.6 (Oct, 2019)

  - fix query string exception handling
  - readd Chameleon template engine chapter to README
  - test on PyPy

- 0.5 (Sep, 2019)

  - add app example
  - update requirements

- 0.4 (Aug, 2019)

  - now, modules within \_\_mount\_\_ are reloadable
  - deprecated @app.test_params, use @app.require
  - deprecated was.Future and was.Futures, it doesn't need.

- 0.3 (Mar 13, 2019)

  - remove proxing django route
  - remove login service with django
  - remove django model signal redirecting
  - add @app.require
  - change mount handler: def mount (app) =>
    def __mount__ (app) but lower version compatible
  - make available @app.route ("")
  - add was.ProxyPass (alias, path, timeout = 3)
  - add special pre-defined URL parameter value: me, notme, new
  - add parameter validation, now response code 400,
    if validatiion if failed
  - fix implicit routing
  - add conditional permission control

- 0.2 (Feb 18, 2019)

  - fix implicit routing for root
  - remove jinja2 from requirements
  - add app.websocket_send ()
  - fix Futures respinse bugs
  - add was.API (), was.Fault (), was.File and
    was.Futures ()

- 0.1 (Jan 17, 2019)

  - was.promise () has been deprecated, use was.Futures ()
  - add interval based maintain jobs executor
  - change name from app.storage to app.store
  - add default_bearer_handler
  - fix routing bugs related fancy URL
  - add was.request.URL, DEFAULT, FORM (former was.request.form ()),
    JSON (former was.request.json ()), DATA (former was.request.data),
    ARGS (former was.request.args)
  - add @app.test_param (required = None, ints = None, floats = None)
  - project has been seperated from skitai and rename from
    saddle to atila, because saddle project is already exist on PYPI


