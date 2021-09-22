==========
SQLPhile
==========

.. contents:: Table of Contents

Introduce
=============

SQLPhile is a SQL template engine and Python style SQL generator. It looks like Django ORM but it hasn't any relationship with Django or ORM.

But it is inspired by Django ORM and iBATIS SQL Maps.

SQLPhile might be useful for keeping clean look of your app script. It can make hide SQL statements for your script by using Python functions or/and writing SQL templates to seperated files.

For Example,

.. code:: python

  conn = psycopg2.connect (...)
  cursor = conn.cursor ()
  cursor.execute ("""
    SELECT type, org, count(*) cnt FROM tbl_file
    WHERE org = {} AND filename LIKE '%{}'
    GROUP BY {}
    ORDER BY {}
    LIMIT {}
    OFFSET {}
  """.format (1, 'OCD', 'type', 'org, cnt DESC', 10, 10))
  cursor.close ()
  conn.close ()

This codes can be written with SQLPhile:

.. code:: python

  import sqlphile as sp

  with sp.postgres ("dbname", "user", "password", "server") as db:
    rows = (db.select ("tbl_file").get ("type", "count(*) cnt")
        .filter (org = 1, name__endswith = 'OCD')
        .group_by ("type").order_by ("org", "-cnt")[10:20]
        .execute ().fetchall ())

Or you can use SQL template file: sqlmaps/file.sql:

.. code:: html

  <sql name="get_stat">
    SELECT type, org, count(*) cnt FROM tbl_file
    WHERE {this.filters} {this.group_by} {this.order_by} {this.limit} {this.offset}
  </sql>

Your app code is,

.. code:: python

  with sp.sqlite3 ("dbname.db3", dir = "./sqlmap") as db:
    rows = (db.file.get_stat.filter (org = 1, name__endswith = 'OCD')
       .group_by ("type").order_by ("org", "-cnt")[10:20]
       .execute ().fetchall ())


Simple Query
--------------

SQLPhile provide select(), update(), insert() and delete() for generic SQL operation.

.. code:: python

  import sqlphile as sp

  with sp.sqlite3 (r"sqlite3.db3") as db:
    q = (db.insert ("tbl_file")
       .set (_id = 1, score = 1.3242, name = "file-A", moddate = datetime.date.today ())
       .execute ())

    q = (db.update ("tbl_file")
        .set (name = "Jenny", modified = datetime.date.today ())
        .filter (...)
        .execute ())

    q = (db.delete ("tbl_file")
        .filter (...))

    q = (db.select ("tbl_file")
        .get ("id", "name", "create", "modified")
        .filter (...))

    for row in q.execute ().fetchall ():
      ...

If you want to insert or update to NULL value, give None.

.. code:: python

  q = db.insert ("tbl_file", score = None)

aggregate () will drop previous get ().

.. code:: python

  q = (db.select ("tbl_file")
        .get ("id", "name", "create", "modified")
        .filter (...))
  q.aggregate ('count (id) as c')
  >> SELECT count (id) as c FROM tbl_file WHEHE ...


Filtering & Excluding
======================

First of all,

.. code:: python

  q.filter (id__eq = 1, name = None)
  >> id = 1

  q.exclude (id__eq = 1, name = None)
  >> NOT (id = 1)

Please give your attention that *name* will be ignored. It makes reducing 'if' statements.

.. code:: python

  def (a = None, b = None):
    q.filter (a__eq = a, b__contains = b)

if a or b is None, it will be simply ignored, and you can keep simple and consistent statement.


Otherwise, filter () is very similar with Django ORM.

.. code:: python

  q = sp.get_stat

  q.all ()
  >> 1 = 1

  q.filter (id = 1)
  >> id = 1

  q.filter ("id = 1")
  >> id = 1

  q.filter (id = 1, user__in = ["hansroh", "janedoe"])
  >> id = 1 AND user in ("hansroh", "janedoe")

  q.filter ("a.id = 1", user__in = ["hansroh", "janedoe"])
  >> a.id = 1 AND user in ("hansroh", "janedoe")

  q.filter (tbl__name__startswith = "Hans%20Roh"))
  >> tbl.name LIKE 'Hans\\%20Roh%'

  q.filter (user__in = ["hansroh", "janedoe"])
  q.exclude (id__between = (100, 500), deleted = True)
  >> user in ("hansroh", "janedoe") AND NOT (id BETWEEN 100 AND 500 AND deleted = true)

  q.filter (t1__id = 1)
  >> t1.id = 1

  q.filter (id__exact = 1)
  >> id = 1

  q.filter (id__eq = 1)
  >> id = 1

  q.exclude (id = 1)
  >> NOT (id = 1)

  q.filter (id__neq = 1)
  >> id <> 1

  q.filter (t1__id__neq = 1)
  >> t1.id <> 1

  q.filter (id__gte = 1)
  >> id >= 1

  q.filter (id__lt = 1)
  >> id < 1

  q.filter (id__between = (10, 20))
  >> id BETWEEN 10 AND 20

  q.filter (name__contains = "fire")
  >> name LIKE '%fire%'

  q.exclude (name__contains = "fire")
  >> NOT name LIKE '%fire%'

  q.filter (name__startswith = "fire")
  >> name LIKE 'fire%'

  # escaping %
  q.filter (name__startswith = "fire%20ice")
  >> name LIKE 'fire\%20ice%'

  q.filter (name__endswith = "fire")
  >> name LIKE '%fire'

  q.filter (name__isnull = True)
  >> name IS NULL

  q.filter (name__isnull = False)
  >> name IS NOT NULL

  # PostgrSQL Only
  q.filter (name__regex = "^fires?")
  >> name ~ '^fires?'

	q.filter (tbl__data___name = "Hans Roh")
  >> tbl.data->>'name' = 'Hans Roh'

	q.filter (tbl__data___age = 20)
  >> CAST (tbl.data->>'age' AS int) = 20

  q.filter (tbl__data___person___age = 20)
  >> CAST (tbl.data->'person'->>'age' AS int) = 20

  q.filter (tbl__data___persons__2___age = 20)
  >> CAST (tbl.data#>'{persons, 3}'->>'age' AS int) = 20


Also you can add multiple filters:

.. code:: python

  q.filter (name__isnull = False, id = 4)
  >> name IS NOT NULL AND id = 4

  q.filter ("name IS NOT NULL", id = 4)
  >> name IS NOT NULL AND id = 4


All filters will be joined with "AND" operator.

Q Object
----------

.. code:: python

  f = Q (a__gt = 1)
  f = f & Q (b__gt = 1)
  >> (a > 1 AND b > 1)

  q.filter (f, c__gt 1)
  >> (a > 1 AND b > 1) AND c > 1

  q.filter ("d > 1", f, c__gt = 1)
  >> d > 1 AND (a > 1 AND b > 1) AND c > 1

How can add OR operator?

.. code:: python

  from sqlphile import Q

  q.filter (Q (id = 4) | Q (email__contains = "org"), name__isnull = False)
  >> name IS NOT NULL AND (id = 4 OR email LIKE '%org%')

Note that Q objects are first, keywords arguments late. Also you can add seperatly.

.. code:: python

  q.filter (name__isnull = False)
  q.filter (Q (id = 4) | Q (email__contains = "org"))
  >> (id = 4 OR email LIKE '%org%') AND name IS NOT NULL

If making excluding filter with Q use tilde(*~*),

.. code:: python

  q.filter (Q (id = 4) | ~Q (email__contains = "org"))
  >> (id = 4 OR NOT email LIKE '%org%')


F Object
----------

All value will be escaped or automatically add single quotes, but for comparing with other fileds use *F*.

.. code:: python

  from sqlphile import F

  Q (email = F ("b.email"))
  >> email = b.email

  Q (email__contains = F ("org"))
  >> email LIKE '%' || org || '%'

F can be be used for generic operation methods.

.. code:: python

  q = (db.update (tbl, n_view = F ("n_view + 1"))
      .filter (...))
  cursor.execute (q.as_sql ())

Ordering & Grouping
====================

For ordering,

.. code:: python

  q = (db.select (tbl).get ("id", "name", "create", "modified")
      .filter (...)
      .order_by ("id", "-modified"))
  >> ORDER BY id, modified DESC

For grouping,

.. code:: python

  q = (db.select (tbl).get ("name", "count(*) cnt")
      .filter (...)
      .group_by ("name"))
  >> ... GROUP BY name

  q.having ("count(*) > 10")
  >> GROUP BY name HAVING count(*) > 10

Offset & Limit
================

For limiting record set,

.. code:: python

  q = db.select (tbl).get ("id", "name", "create", "modified")
  q [:100]
  >> LIMIT 100

  q [10:30]
  >> LIMIT 20 OFFSET 10

Be careful for slicing and limit count.


Limit 0
---------------------

.limit (0) can be useful for avoiding excution entire query without 'if' statement with sqlphile.db2 or pg2 module.


Returning
============

For Returning columns after insertinig or updating data,

.. code:: python

  q = db.insert (tbl).set (name = "Hans", created = datetime.date.today ())
  q.returning ("id", "name")
  >> RETURNING id, name


Update On Conflict / Upsert
====================================

.. code:: python

  q = db.insert (tbl).set (name = "Hans", created = datetime.date.today ())
  q.upflict ('name', updated = datetime.date.today ())
  >> INSERT INTO tbl (name, created)
     VALUES ('Hans', '2020-12-24')
     ON CONFLICT (name) DO UPDATE
     SET updated = '2020-12-25'

To upserting

.. code:: python

  q = db.insert (tbl).set (name = "Hans", created = datetime.date.today ())
  q.upflict ('name')
  >> INSERT INTO tbl (name, created)
     VALUES ('Hans', '2020-12-24')
     ON CONFLICT (name) DO NOTHING

*Note*: `name` field must have uniqie index


CTE (Common Table Expression)
============================================

*New in version 0.6*

.. code:: python

  cte = db.insert ("human").set (name = "Hans", division = "HR").returning ("*"))
  q = (db.insert ("reqs").
           .with_ ("inserted", cte)
           .set (tbl_id = F ("inserted.id"), req = "vaccation"))

  >> WITH inserted AS (INSERT INTO human (name, division) VALUES ('Hans', 'HR') RETURNING *)
     INSERT INTO reqs (tbl_id, req) VALUES (inserted.id, 'vaccation')


*New in version 0.6.4*

Starting with\_ is alos possible, that is more clare than above, I think.

.. code:: python

  q =  db.with_ ("inserted", db.insert ("human").set (name = "Hans", division = "HR").returning ("*")))
  q = (db.insert ("reqs").
           .set (tbl_id = F ("inserted.id"), req = "vaccation"))

  >> WITH inserted AS (INSERT INTO human (name, division) VALUES ('Hans', 'HR') RETURNING *)
     INSERT INTO reqs (tbl_id, req) VALUES (inserted.id, 'vaccation')

Multiple CTEs are also possible,

.. code:: python

  q = (db.insert ("reqs")
           .with\_ ("inserted", cte)
           .with\_ ("inserted2", cte)
           .set (tbl_id = F ("inserted.id"), req = "vaccation"))

  >> WITH inserted AS (INSERT INTO human (name, division) VALUES ('Hans', 'HR') RETURNING *),
          inserted2 AS (INSERT INTO human (name, division) VALUES ('Hans', 'HR') RETURNING *)
     INSERT INTO reqs (tbl_id, req) VALUES (inserted.id, 'vaccation')

.. code:: python

  from sqlphile import D

  data = D (a = 1, b = "c")
  sql = (
      sqlmaps.select ("tbl").with_ ("temp", cte).join ("temp", "true")
  )
  >> WITH temp (a, b) AS (values (1, 'c'))
     SELECT * FROM tbl
     INNER JOIN temp ON true


Using Constant
=====================

.. code:: python

  from sqlphile import const

  sql = (
      sqlmaps.select ("temp").const ("a", 1).const ('b', 'c').filter (a = const ("a"))
  )
  >>  WITH a AS (values (1)), b AS (values ('c'))
      SELECT * FROM temp
      WHERE a = (table a)


Joining
============

For joining tables,

.. code:: python

  q = db.select ("tbl_file t1").join ("names t2", "t1.name = t2.name")
  q.filter (id__gt > 100)
  q.get ("score", "t2.name")

  >> SELECT score, t2.name FROM tbl_file AS t1
     INNER JOIN names AS t2 ON t1.name = t2.name
     WHERE id > 100

For joining with sub query,

.. code:: python

  subq = db.select ("tbl_project").get ("name")
  q = db.select ("tbl_file t1").join (subq, "t2", "t1.name = t2.name")
  q.filter (id__gt = 100)
  q.get ("score", "t2.name")

  >> SELECT score, t2.name FROM tbl_file AS t1
     INNER JOIN (SELECT * FROM tbl_project) AS t2 ON t1.name = t2.name
     WHERE id > 100

You can use 'from\_()' for update query,

.. code:: python

  q = db.update ("tbl_file", "t1")
  q.from_ ("tbl_record t2", "t1.id = t2.id")
  q.set (score = F ("t2.score"))
  q.filter (t1__id = 1)

  >> UPDATE tbl_file AS t1 SET score = t2.score
     FROM tbl_record AS t2 ON t1.id = t2.id
     WHERE t1.id = 1

Also available,

- left_join ()
- right_join ()
- full_join ()


Union, Intersect, Except
=====================================

.. code:: python

  q1 = db.select ("tbl_project").get ("name")
  q2 = db.select ("tbl_file t1").get ("name")
  q1.union (q2)

Also union_all, intersect and except\_ are available.


INSERT INTO ... SELECT ...
=====================================

.. code:: python

  sql = (
    db.select ("tbl1")
      .get ("name")
      .into ("tbl2", "name")
  )
  >> INSERT INTO tbl2 (name) SELECT name from tbl1


Transaction
====================

.. code:: python

  q = (db.tran ()
      .update ("tbl_file")
      .set (score = 5.0).filter (id = 6)
      .execute (True))
	>>> BEGIN TRANSACTION;
	      UPDATE tbl_file SET score = 5.0 WHERE id = 5;
	      COMMIT;


Multiple Statement
================================

.. code:: python

  sql = db.insert ("temp").set (id = 2, comment = 'Comment')
  sql.append (db.update ("temp2").set (comment_count = F ('comment_count + 1')).filter (id = 2))
  >>> INSERT INTO temp (id, comment) VALUES (2, 'Comment');
  UPDATE temp2 SET comment_count = comment_count + 1 WHERE id = 2


Branching
================

You can branch your query branch() method.

.. code:: python

  stem = db.select ("tbl_file").filter (...)
  q1 = stem.clone ().get ("id, name, create, modified").order_by (-id)
  q2 = stem.clone ().get ("counte (*) as cnt")


Using Template
=================

For simple example,

.. code:: python

  with sp.sqlite3 (r"sqlite3.db3") as db:
    q = (db.tempate ("SELECT {columns} FROM tbl_file WHERE {this.filters} {this.order_by}")
        .feed (columns = "id, name")
        .filter (id__eq = 6)
        .order_by ("-id"))
    q.as_sql () # OR q.render ()
    >> SELECT id, name FROM tbl_file WHERE id = 6 ORDER BY id DESC

If you create SQL templates in specific directory,

.. code:: python

  with sp.sqlite3 ("sqlite3.db3", dir = "./sqlmaps", auto_reload = True) as db:
    ...

SQLPhile will load all of your templates in ./sqlmaps.

If you are under developing phase, set auto_reload True.

Assume there is a template file named 'file.sql':

.. code:: html

  <sqlmap version="1.0">

  <sql name="get_stat">
    SELECT type, org, count(*) cnt FROM tbl_file
    WHERE {this.filters}
    GROUP BY type
    ORDER BY org, cnt DESC
    {this.limit} {this.offset}
  </sql>

It looks like XML file, BUT IT'S NOT. All tags - <sqlmap>, <sql></sql> should be started at first of line. But SQL of inside is at your own mind but I recommend give some indentation.

Now you can access each sql temnplate via filename without extension and query name attribute:

.. code:: python

  # filename.query name
  q = db.file.get_stat
  q.filter (...).order_by (...)

  # or
  q = db.file.get_stat.filter (...).order_by (...)

Note: filename is *default.sql*, you can ommit filename.

.. code:: python

  q = db.get_stat
  q.filter (...).order_by (...)

Note 2: SHOULD NOT use starts with "select", "update", "insert", "delete" or "template" as template filename.


For another example template is like this,

.. code:: html

  <sqlmap version="1.0">

  <sql name="get_stat">
    SELECT type, org, count(*) cnt FROM tbl_file
    WHERE {this.filters}
    GROUP BY type
    ORDER BY org, cnt DESC
    {this.limit} {this.offset}
  </sql>

  <sql name="get_file">
    SELECT * cnt FROM tbl_file
    WHERE {this.filters}
    {this._order_by}
    {this.limit}
    {this.offset}
  </sql>

You just fill variables your query reqiures,

.. code:: python

  q = db.file.get_file.filter (id__gte = 1000)[:20]
  q.order_by ("-id")

Current reserved variables are,

- this.filters
- this.group_by
- this.order_by
- this.limit
- this.offset
- this.having
- this.returning


Adding Data
--------------

data () also creates 3 variables automatically for inserting and updating purpose,

- this.pairs
- this.columns
- this.values

.. code:: html

  <sql name="update_profile">
    UPDATE tbl_profile SET {this.pairs} WHERE {this.filters};
    INSERT INTO tbl_profile ({this.columns}) VALUES ({this.values});
  </sql>

.. code:: python

  q = db.update_profile
  q.set (name = "Hans Roh", birth_year = 2000)
  q.set (email = None, age = 20)

Will be rendered:

.. code:: python

  {this.columns} : name, birth_year, email, age
  {this.values} : 'Hans Roh', 2000, NULL, 20
  {this.pairs} : name='Hans Roh', birth_year=2000, email=NULL, age=20


D Object
```````````

D object convert dictionary into SQL column and value format and can feed them into SQL template.

.. code:: python

  from sqlphile import D

  d = D (name = "Hans", id = 1, email = None)
  d.values
  >> 'Hans', 1, NULL

  d.columns
  >> name, id, email

  d.pairs
  >> name = 'Hans', id = 1, email = NULL

And you can feed to template with prefix.

.. code:: html

  <sql name="get_file">
    INSERT ({this.columns}, {additional.columns})
    VALUES ({this.values}, {additional.values})
    {this.returning};
  </sql>

In app,

.. code:: python

  q = db.file.get_file.set (area = "730", additional = D (name = 'Hans', id = 1))
  q.returning ("id")
  q.execute ()

In a conclusion, it will be created 3 variables automatically,

- additional.pairs
- additional.columns
- additional.values

More About filter()
---------------------

In some cases, filter is tricky.

.. code:: html

  <sqlmap version="1.0">

  <sql name="get_stat">
    SELECT type, org, count(*) cnt FROM tbl_file
    WHERE isdeleted is false AND {this.filters}
  </sql>

Above SQL is only valid when {this.filters} exists, but what if filter doesn't be provided all the time? You can write like this:

.. code:: python

  q = db.file.get_file.filter (__all = True, id__gte = None)
  >> WHERE isdeleted is false AND 1 = 1

  q = db.file.get_file.filter (__all = True, id__gte = 1)
  >> WHERE isdeleted is false AND 1 = 1 AND id >= 1


Variablize Your Query
-----------------------

You can add variable on your sql by feed() and data() and both can be called multiple times.

Feeding Variable Key-Value Pairs
``````````````````````````````````````

.. code:: html

  <sql name="get_file">
    SELECT {cols} FROM {tbl}
    WHERE {this.filters}
  </sql>

Now feed keywords args with feed ():

.. code:: python

  q = db.file.get_file
  q.feed (cols = "id, name, created", tbl = "tbl_file")
  q.filter (id__gte = 1000)


Also you can feed filter.

.. code:: html

  <sql name="get_file">
    SELECT * FROM tbl_file
    WHERE {id} AND {name} AND create BETWEEN {created}
  </sql>

.. code:: python

  q.feed (id = Q (id__in = [1,2,3,4,5]))
  >> id IN (1,2,3,4,5)

  q.feed (id = Q (id__in = [1,2,3,4,5]), name = "Hans")
  >> id IN (1,2,3,4,5) AND name = 'Hans'

  q.feed (id = Q (id__in = [1,2,3,4,5]), name = Q (name = None), created = B (1, 4))
  # name is ignored by 1 = 1
  >> id IN (1,2,3,4,5) AND 1 = 1

Actually, feed () can be omitable,

.. code:: python

  # like instance constructor
  q = db.file.get_file (cols = "id, name, created", tbl = "tbl_file")
  q.filter (id__gte = 1000)

Actually this template formating use python format function,

.. code:: html

  <sql name="get_file">
    SELECT * FROM tbl_file
    WHERE id = '{id:010d}' AND name = '{name:10s}'
  </sql>

  q.feed (id = 10000, name = 'hansroh')
  >> WHERE id = '0000010000' AND name = 'hansroh   '


Feeding V Object
````````````````````

If V will escape values for fitting SQL. You needn't care about sing quotes, escaping or type casting on date time field.

.. code:: python

  V (1)
  >> 1

  V (__eq = 1)
  >> 1

  V (datetime.date.today ())
  >> TIMESTAMP '20171224 00:00:00'

  V ("Hans")
  >> 'Hans'

  V (None)
  >> NULL

  V ()
  >> NULL

  V (__eq = "Hans")
  >> 'Hans'

  V (__contains = "Hans")
  >> '%Hans%'

  V (__in = [1,2])
  >> (1,2)

  V (__between = [1,2])
  >> 1 AND 2

For example,

.. code:: html

  <sql name="get_file">
    UPDATE tbl_profile
    SET {this.pairs}
    WHERE id IN (
      SELECT id FROM tbl_member
      WHERE name = {name}
    );
    UPDATE tbl_stat SET count = count + 1
    WHERE birth_year IN {birth_year};
  </sql>

.. code:: python

  q = db.file.get_file.feed (
    email = V ("hansroh@email.com"),
    birth_year = V (__in = (2000, 2002, 2004))
  )
  q.set (name = "Hans Roh")


Using SQLPhile as SQL Query Generator
=========================================

If you need just SQL statement, you can use SQLPhile as template engine.

.. code:: python

  import sqlphle as sp

  template = sp.Template ("postgresql")
  q = template.select ("tbl_file").get ("score", "t2.name")
  q.as_sql () == str (q)

  # specify template file
  template = sp.Template ("postgresql", "./sqlmaps/test.sql")
  q = template.house (tbl = 'tbl_file')

  # specify template directory
  template = sp.Template ("postgresql", "./sqlmaps")
  q = template.test.house (tbl = 'tbl_file')


Migrating to version 0.5
===================================

In version 0.5 template format string has been changed. most of them are compatable but some aren't.

If you used D (...), look carefully and SHOUD rewrite.

.. code:: html

  # default.sql
  <sql name="get_file">
    UPDATE tbl_profile
    SET {mydata_pairs}
    WHERE {_filters}
  </sql>

At your code,

.. code:: python

  template = sp.Template ("postgresql", "./sqlmaps")
  q = template.get_file (mydata = D (name = 'Hans Roh'))

In version 0.5, you should change **{mydata_pairs}** into **{mydata.pairs}**.

Also _something has been deprecated, I recommend changes.

- {_filters} => {this.filter}
- {_order_by} => {this.oreder_by}
- {_group_by} => {this.group_by}
- {_having} => {this.having}
- {_returning} => {this.returning}
- {_columns} => {this.columns}
- {_values} => {this.values}
- {_pairs} => {this.pairs}


Change Logs
=============

- 0.6

  - add x_join_related ()
  - add fetch1 () and fetchn ()
  - add excommit (), exfetch () and exone ()
  - add haskey and haskeyin operators for JSON object query
  - add JSON query
  - add .aggregate ()
  - .branch () => .clone ()
  - .data () => .set ()
  - add upflict (field_name, \*\*data)
  - with\_ can be for initiating
  - add const
  - add multiple statement using .append ()
  - with\_ for CTE

- 0.5

  - add .with\_ (sql, alias) for common table expression
  - add .intersect (sql) and .except\_ (sql)
  - change templating format style: this not compatable with version 0.4, see upgrade section

- 0.4.9

  - add .union () abd union_all ()

- 0.4

  - add .clone ()
  - add __regex
  - fix exclude
  - fix ~Q
  - add fetchxxx to SQL class
  - fetchxxx (as_dict = True) returns AttrDict
  - add sqlphile.Template

- 0.3.5

  - add sp.sqlite3 and sp.postgres (== prevous sp.db3.open and qlphile.pg2.open)

- 0.3.4

  - extend IN query
  - enalbe multiple keyword argument for Q

- 0.3.3

  - add db3 and pg2

- 0.3.1

  - fix datetime type
  - add boolean type casting



