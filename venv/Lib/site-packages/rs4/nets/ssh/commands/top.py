import re
import pandas as pd
from io import StringIO
from . import default

class Result (default.Result):
    def parse_status_line (self, line, delim = ','):
        line = line.replace (' used.', ' used,')
        gname, d = line.split (':', 1)
        gname = gname.strip ()
        dt = {}
        for e in d.split (delim):
            count, *status = e.split ()
            dt [(' '.join (status)).strip ()] = float (count)
        return gname, dt

    def parse_output (self, output):
        match = re.match (r'^([\w\W]*?)\n( +PID.*COMMAND)\n([\w\W]*)', output)
        meta, self.header, data = match[1], match[2], match[3]
        if self.header.find ('SHR') == -1:
            df = pd.read_fwf (
                StringIO (data)
                , colspecs = [(0,5), (6,16), (16,18), (19,22), (23,30), (31,37), (38,43), (44,48), (49,58), (59,60), (61,999) ]
                , names    = ['PID', 'USER',    'PR',    'NI',  'VIRT',   'RES',   '%CPU',  '%MEM', 'TIME+',     'S', 'COMMAND']
            )
        else:
            df = pd.read_fwf (
                StringIO (data)
                , colspecs = [(0,5), (6,16), (16,18), (19,22), (23,30), (31,37), (38,44), (45,46), (47,52), (53,57), (58,67), (68,999) ]
                , names    = ['PID', 'USER',    'PR',    'NI',  'VIRT',   'RES',   'SHR',     'S',  '%CPU',  '%MEM', 'TIME+', 'COMMAND']
            )

        data = df.to_dict (orient = 'index')
        self.data = [data [i] for i in range (len (data))]
        self.parse_meta (meta)

    def parse_meta (self, lines):
        for idx, line in enumerate (lines.split ('\n')):
            if idx == 0:
                self.meta ['time'] = line [6:14]
                s = line.find ('load average: ')
                self.meta ['up'] = ''
                for each in line [18:s].split (','):
                    if each.endswith ('user'):
                        self.meta ['user'] = int (each [:-4])
                    else:
                        self.meta ['up'] += each
                self.meta ['up'] = self.meta ['up'].strip ()
                self.meta ['load average'] = list (map (float, line [s + 13:].split (',')))

            elif idx in (1, 3, 4):
               gname, data = self.parse_status_line (line)
               self.meta [gname] = data
