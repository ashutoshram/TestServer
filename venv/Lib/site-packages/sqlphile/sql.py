import re
from . import utils
from .q import Q, V, batch, _Q, OPS
from .d import toval, D
from copy import deepcopy
from .dbtypes import DB_PGSQL, DB_SQLITE3
from .skitai_compat import EMPTY
from .model import AbstractModel

def render_table (table, alias):
    table = isinstance (table, str) and table or "({})".format (table)
    return alias and (table + " AS " + alias) or table

class SQL:
    def __init__ (self, template, engine = DB_PGSQL, conn = None, check_filter = False):
        self._template = template
        self._engine = engine
        self._conn = conn
        self._check_filter = check_filter
        self._filters = []
        self._limit = 0
        self._offset = 0
        self._order_by = None
        self._group_by = None
        self._having = None
        self._returning = None
        self._insert_into = None
        self._cte = []
        self._feed = {}
        self._data = {}
        self._conflict = None
        self._unionables = []
        self._statements = []
        self._transact = False
        self._explicit_empty = False
        self._model = None
        self._talias = {}
        self._fk = {}
        self._with_count = 0

    def __enter__ (self):
        return self

    def __exit__ (self, type, value, tb):
        self.auto_closing and self.close ()

    def is_model (self, model, alias, set_model = True):
        if isinstance (model, (str, SQL)):
            if alias:
                self._talias [model] = alias
            return model

        try:
            assert issubclass (model, AbstractModel)
        except TypeError:
            raise TypeError ('model should be a subclass of sqlphile.model.AbstractModel')

        if set_model:
            self._model = model

        t = model.get_table_name ()
        if alias:
            self._talias [t] = alias
        return t

    def insert (self, table, alias = None):
        self._template = "INSERT INTO " + render_table (self.is_model (table, alias), alias) + " ({this.columns}) VALUES ({this.values})"
        return self

    def update (self, table, alias = None):
        self._template = "UPDATE " + render_table (self.is_model (table, alias), alias) + " SET {this.pairs}"
        self._check_filter = True
        return self

    def select (self, table, alias = None):
        self._template = "SELECT {select} FROM " + render_table (self.is_model (table, alias), alias)
        self.feed (select = ["*"])
        return self

    def delete (self, table, alias = None):
        self._template = "DELETE FROM " + render_table (self.is_model (table, alias), alias)
        self._check_filter = True
        return self

    def with_ (self, alias, sql = None):
        if sql is None:
            self._with_count += 1
            sql = alias
            alias = 'cte_{}'.format (self._with_count)

        if isinstance (sql, D):
            if not sql._encoded:
                sql.encode (self._engine)
            self._cte.append ("{} ({}) AS (values ({}))".format (alias, sql.columns, sql.values))
        else:
            self._cte.append ("{} AS ({})".format (alias, str (sql)))
        return self

    def clone (self, conn = None):
        new = self.__class__ (self._template, self._engine, conn or self._conn)
        new._filters = deepcopy (self._filters)
        new._limit = deepcopy (self._limit)
        new._offset = deepcopy (self._offset)
        new._order_by = deepcopy (self._order_by)
        new._group_by = deepcopy (self._group_by)
        new._having = deepcopy (self._having)
        new._returning = deepcopy (self._returning)
        new._insert_into = deepcopy (self._insert_into)
        new._cte = deepcopy (self._cte)
        new._feed = deepcopy (self._feed)
        new._data = deepcopy (self._data)
        new._explicit_empty = self._explicit_empty
        new._check_filter = self._check_filter
        new._conflict = self._conflict
        new._joins = self._joins
        new._model = self._model
        new._fk = self._fk
        new._talias = self._talias
        new._with_count = self._with_count
        return new
    branch = clone

    @property
    def query (self):
        return self.as_sql ()

    def addD (self, prefix, D_):
        assert prefix != "this", "Cannot use data prefix `this`"
        D_.encode (self._engine)
        self._data [prefix] = D_

    def render (self):
        return self.as_sql ()

    def __str__ (self):
        return self.as_sql ()

    def __getitem__(self, key):
        key.start and self.offset (key.start)
        if key.stop:
            self.limit (key.stop - (key.start or 0))
        return self

    def _join_select_fields (self):
        if "select" not in self._feed:
            return
        if isinstance (self._feed ["select"], list):
            self._feed ["select"] = ", ".join (map (str, self._feed ["select"]))
        if not self._model:
            return
        self._feed ['select'] = self._resolve_haystack (self._feed ['select'])

    def _resolve_field (self, k, isfilter = False):
        default = k if isfilter else k.replace ('__', '.')
        if not self._model:
            return default

        try: base_fks = self._model.get_fks ()
        except NotImplementedError: pass
        else:
            if k in base_fks:
                try:
                    return base_fks [k][0]
                except IndexError:
                    return k

        if k.startswith ('this__'):
            return '{}.{}'.format (self._model.get_table_name (), k [6:])
        return default

    def _resolve_haystack (self, s):
        if not self._model:
            return s

        make_list = False
        if isinstance (s, (list, tuple)):
            make_list = True
            s = ", ".join (s)

        s = s.replace ('this__', '{}.'.format (self._model.get_table_name ()))
        try: base_fks = self._model.get_fks ()
        except NotImplementedError: pass
        else:
            for fk, target in base_fks.items ():
                try:
                    column, model = target
                except TypeError:
                    column, model = fk, target
                rx = re.compile (r"(^|[^_.a-z0-9'])(?:{})($|[^_a-z0-9])".format (fk), re.I)
                s = rx.sub (r'\1{}\2'.format (column), s)
        return make_list and s.split (", ") or s

    def execute (self):
        if self._explicit_empty:
            return self
        if self._check_filter:
            assert self._filters, "No filter for modification, if you want to modify anyway use .all ()"
        return self._conn.execute (self.query) or self

    def all (self):
        self._filters.append ("1 = 1")
        return self

    def exclude (self, *Qs, **filters):
        g = []
        for q in Qs + tuple (batch (**filters)):
            if not q:
                continue
            if not isinstance (q, str):
                q.render (self._engine, self._resolve_field, self._resolve_haystack)
            g.append (str (q))

        cluses = " AND ".join (g)
        if cluses:
            self._filters.append ("NOT (" + cluses + ")")
        return self

    def filter (self, *Qs, **filters):
        for q in Qs + tuple (batch (**filters)):
            if not q:
                continue
            if not isinstance (q, str):
                q.render (self._engine, self._resolve_field, self._resolve_haystack)
            self._filters.append (str (q))
        return self

    def into (self, table, *columns):
        self._insert_into = "INSERT INTO " + table
        if columns:
            self._insert_into += ' ({})'.format (', '.join (columns))
        return self

    def returning (self, *args):
        self._returning = "RETURNING " + ", ".join (args)
        return self

    def having (self, cond):
        self._having = "HAVING " + cond
        return self

    def order_by (self, *by):
        self._order_by = utils.make_orders (by)
        return self

    def group_by (self, *by):
        self._group_by = utils.make_orders (by, "GROUP")
        return self

    def limit (self, val):
        if val == 0:
            self._explicit_empty = True
        self._limit = "LIMIT {}".format (val)
        return self

    def offset (self, val):
        self._offset = "OFFSET {}".format (val)
        return self

    def upflict (self, field_name, **data):
        assert self._template.startswith ("INSERT INTO "), "INSERT query required"
        self._conflict = "ON CONFLICT ({}) DO ".format (field_name)
        if not data:
            sql = "NOTHING"
        else:
            _data = {}
            for k, v in data.items ():
                k = self._resolve_field (k)
                if isinstance (v, D):
                    _data [k] = v
                else:
                    _data [k] = toval (v, self._engine)
            sql = "UPDATE SET " + utils.D (**_data).pairs
        self._conflict += sql
        return self

    def const (self, var, val):
        self._cte.append ("{} AS (values ({}))".format (var, toval (val, self._engine)))
        return self

    def set (self, __donotusethisvariable__ = None, **karg):
        if self._data and self._model and not self._check_filter:
            raise ValueError ('to validatte model data, set () can be called just once')

        if __donotusethisvariable__:
            d = __donotusethisvariable__
            d.update (karg)
        else:
            d = karg

        if self._model:
            try:
                d = self._model.validate (d, not self._check_filter)
            except NotImplementedError:
                pass

        for k, v in d.items ():
            k = self._resolve_field (k)
            if isinstance (v, D):
                self.addD (k, v)
            else:
                self._data [k] = toval (v, self._engine)
        return self
    data = set

    def feed (self, **karg):
        for k, v in karg.items ():
            if isinstance (v, D):
                self.addD (k, v)
            else:
                # Q need str()
                if isinstance (v, _Q) and not v:
                    # for ignoring
                    v = "1 = 1"
                elif isinstance (v, (V, _Q)):
                    v.render (self._engine)
                if k == 'select':
                    self._feed [k] = isinstance (v, str) and [v] or v
                else:
                    self._feed [k] = str (v)
        return self

    def as_sql (self):
        raise NotImplementedError

    def tran (self):
        self._transact = True

    def append (self, sql):
        self._statements.append (sql)
        return self

    def intersect (self, sql):
        self._unionables.append ((sql, "INTERSECT"))
        return self

    def except_ (self, sql):
        self._unionables.append ((sql, "EXCEPT"))
        return self

    def union (self, sql):
        self._unionables.append ((sql, "UNION"))
        return self

    def union_all (self, sql):
        self._unionables.append ((sql, 'UNION ALL'))
        return self

    def maybe_union (self, current):
        n_q = len (self._unionables)
        qs = []
        if self._unionables:
            qs.append ('({})'.format (current))
        else:
            qs.append (current)

        for idx, (sql, type) in enumerate (self._unionables):
            qs.append (type)
            qs.append ('({})'.format (sql))
        r = "\n".join (qs)
        if self._transact:
            return "BEGIN TRANSACTION;\n" + r + ";\nCOMMIT;"
        return r

    # only work if self._explicit_empty ---------------------------
    def fetchall (self, *args, **kargs):
        return []

    def fetchmany (self, *args, **kargs):
        return []

    def fetchone (self, *args, **kargs):
        return

    def dispatch (self, *args, **kargs):
        return EMPTY

    def one (self, *args, **kargs):
        return EMPTY.one (*args, **kargs)

    def fetch (self, *args, **kargs):
        return EMPTY.fetch (*args, **kargs)

    def exone (self, *args, **kargs):
        return self.execute ().one (*args, **kargs)

    def exfetch (self, *args, **kargs):
        return self.execute ().fetch (*args, **kargs)

    def excommit (self):
        return self.execute ().commit ()


class TemplateParams:
    def __init__ (self, this, data):
        self.filter = " AND ".join ([f for f in this._filters if f])
        self.limit = this._limit
        self.offset = this._offset
        self.group_by = this._group_by
        self.order_by = this._order_by
        self.having = this._having
        self.returning = this._returning
        self.insert_into = this._insert_into
        self.cte = this._cte

        self.columns = data.columns
        self.values = data.values
        self.pairs = data.pairs


class SQLTemplateRenderer (SQL):
    def __call__ (self, **karg):
        return self.feed (**karg)

    def as_sql (self):
        data = utils.D (**self._data)
        this = TemplateParams (self, data)
        self._join_select_fields ()
        self._feed.update (self._data)
        self._feed ["this"] = this
        if self._template.find ("{_") != -1:
            compatables = {
                "_filters": this.filter,
                "_limit": this.limit,
                "_offset": this.offset,
                "_order_by": this.order_by,
                "_group_by": this.group_by,
                "_having": this.having,
                "_returning": this.returning,
                "_columns": data.columns,
                "_values": data.values,
                "_pairs": data.pairs
            }
            self._feed.update (compatables)
        r = self._template.format (**self._feed)
        return self.maybe_union (r)


class SQLComposer (SQL):
    def __init__ (self, template, engine = DB_PGSQL, conn = None, check_filter = False):
        SQL.__init__ (self, template, engine, conn, check_filter)
        self._joins = []

    def branch (self, conn = None):
        new = SQL.branch (self, conn)
        new._joins = deepcopy (self._joins)
        return new

    def aggregate (self, *columns, ignore_limit = True):
        # drop prev selects
        clo = self.clone ()
        clo._feed ["select"] = []
        clo._order_by = None
        clo._group_by = None
        clo._having = None
        if ignore_limit:
            clo._limit = 0
            clo._offset = 0
        return clo.get (*columns)

    def get (self, *columns):
        columns = list (filter (None, columns))
        if not columns:
            return self
        if "select" not in self._feed:
            self._feed ["select"] = []
        if self._feed ['select'] == ['*']:
            self._feed ['select'] = []
        self._feed ["select"].extend (columns)
        return self

    def _join (self, jtype, obj, alias, on, *Qs, **filters):
        if alias == 'true':
            alias, on = '',  'true'

        if alias:
            if alias.find (".") != -1:
                Qs = (alias,) + Qs
                alias = ''
            else:
                self._talias [obj] = alias
                alias = ' AS {}'.format (alias)
        else:
            alias = ''

        _filters = []
        for q in (on,) + Qs + tuple (batch (**filters)):
            if not q:
                continue
            if not isinstance (q, str):
                q.render (self._engine, self._resolve_field, self._resolve_haystack)
            _filters.append (str (q))
        _filters = " AND ".join ([f for f in _filters if f])

        if isinstance (obj, SQL):
            obj = "({})".format (obj)
        elif not isinstance (obj, str):
            obj = obj.get_table_name ()
        else:
            assert isinstance (obj, str), 'invalid table name'

        self._joins.append (
            "{} {}{}{}".format (jtype, obj, alias, _filters and (' ON ' + _filters) or '')
        )
        return self

    def from_ (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("FROM", obj, alias, on, *Qs, **filters)

    def join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("INNER JOIN", obj, alias, on, *Qs, **filters)

    def left_join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("LEFT OUTER JOIN", obj, alias, on, *Qs, **filters)

    def right_join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("RIGHT OUTER JOIN", obj, alias, on, *Qs, **filters)

    def full_join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("FULL OUTER JOIN", obj, alias, on, *Qs, **filters)

    def cross_join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("CROSS JOIN", obj, alias, *Qs, on, **filters)

    def order_by (self, *by):
        return super ().order_by (*self._resolve_haystack (by))

    def group_by (self, *by):
        return super ().group_by (*self._resolve_haystack (by))

    def _join_related (self, jtype, fk_chain, alias):
        assert self._model, 'base model required'
        base_model = self._model
        for fk in fk_chain.split ('__'):
            table = base_model.get_table_name ()
            try:
                fk_column, target_model = base_model.get_fks () [fk]
            except TypeError:
                fk_column, target_model = fk, base_model.get_fks () [fk]
            target_table, target_pk = target_model.get_table_name (), target_model.get_pk ()
            base_model = target_model
        self._fk [fk_chain] = target_table
        on = '{}.{} = {}.{}'.format (self._talias.get (table, table), fk_column, alias or target_table, target_pk)
        if jtype == "FROM":
            self._join (jtype, target_table, alias, on = None)
            return self.filter (on)
        return self._join (jtype, target_table, alias, on = on)

    def join_related (self, fk_chain, alias):
        return self._join_related ("INNER JOIN", fk_chain, alias)

    def left_join_related (self, fk_chain, alias):
        return self._join_related ("LEFT OUTER JOIN", fk_chain, alias)

    def right_join_related (self, fk_chain, alias):
        return self._join_related ("RIGHT OUTER JOIN", fk_chain, alias)

    def full_join_related (self, fk_chain, alias):
        return self._join_related ("FULL OUTER JOIN", fk_chain, alias)

    def cross_related (self, fk_chain, alias):
        return self._join_related ("CROSS JOIN", fk_chain, alias)

    def from_related (self, fk_chain, alias):
        return self._join_related ("FROM", fk_chain, alias)

    def as_sql (self):
        data = utils.D (**self._data)
        self._join_select_fields ()
        self._feed ["this"] = data
        if self._template.find ("{_") != -1:
            compatables = {
                "_columns": data.columns,
                "_values": data.values,
                "_pairs": data.pairs
            }
            self._feed.update (compatables)
        sql = [
            self._template.format (**self._feed)
        ]
        for join in self._joins:
            sql.append (join)
        _filters = [f for f in self._filters if f]
        _filters and sql.append ("WHERE " + " AND ".join (_filters))
        if self._group_by:
            sql.append (self._group_by)
            self._having and sql.append (self._having)
        self._order_by and sql.append (self._order_by)
        self._limit and sql.append (self._limit)
        self._offset and sql.append (self._offset)
        self._conflict and sql.append (self._conflict)
        self._returning and sql.append (self._returning)
        if self._insert_into:
            sql.insert (0, self._insert_into)

        if self._cte:
            sql.insert (0, "WITH " + ", ".join (self._cte))
        r = "\n".join (sql)
        _ = self.maybe_union (r)
        if self._statements:
            _ += ";\n" + ";\n".join ([s.as_sql () for s in self._statements])
        return _
