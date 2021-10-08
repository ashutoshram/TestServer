import re
import os
import datetime

class Markdown:
    def __init__ (self, path):
        self.path = path
        self.f = []
        self.toc = []

    def sizeof_fmt (self, num, suffix='B'):
        if not isinstance (num, (float, int)):
            return '-'
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def write_table (self, rows, *cols):
        self.writeln ('')
        cols = [col.split ('__') for col in cols]
        self.writeln ('|'.join ([col [0].title () for col in cols]))
        cells = []
        for col in cols:
            if len (col) == 2:
                key, fmt = col
            else:
                key, fmt = col [0], None
            v = rows and rows [0][key] or None
            if isinstance (v, (int, float)) or fmt == 'bytes':
                cells.append ('--------:')
            else:
                cells.append ('---------')
        self.writeln ('|'.join (cells))

        for row in rows:
            rowd = []
            for col in cols:
                if len (col) == 2:
                    key, fmt = col
                else:
                    key, fmt = col [0], None
                v = row [key]
                if fmt == 'bytes':
                    v = self.sizeof_fmt (v)
                elif fmt == 'basename':
                    v = os.path.basename (v)
                elif isinstance (v, datetime.date):
                    v = v.strftime ('%Y-%m-%d %H:%M')
                elif v is None:
                    v = '-'
                rowd.append (str (v))
            self.writeln ('|'.join (rowd))
        self.writeln ('')

    def write (self, data):
        self.f.append (data)

    def writeln (self, line):
        if line.startswith ('#'):
            self.toc.append (line)
        self.f.append (line + '\n')

    def read (self):
        with open (self.path) as f:
            return f.read ()

    RX = re.compile ('[^-_a-z0-9]')
    RX_HYPEN = re.compile ('[-]+')
    def close (self, toc_title = None):
        with open (self.path, 'w') as f:
            if toc_title:
                anchors = {}
                toc = [toc_title]
                for t in self.toc:
                    lev, title = t.split (' ', 1)
                    if len (lev) >= 4:
                        continue
                    anchor = self.RX.sub ('', title.lower ().replace (' ', '-'))
                    if anchor [0].isdigit ():
                        anchor = 'anchor-' + anchor
                    try:
                        anchors [anchor] += 1
                    except KeyError:
                        anchors [anchor] = 0
                    if anchors [anchor]:
                        anchor = anchor + '-' + str (anchors [anchor])
                    anchor = self.RX_HYPEN.sub ('-', anchor)
                    toc.append ('{}- [{}](#{})'.format ('  ' * (len (lev) - 1), title, anchor))
                f.write ('\n'.join(toc))
                f.write ('\n')
            f.write (''.join(self.f))
