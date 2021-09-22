from . import default
import re

class Result (default.Result):
    def parse_output (self, output):
        lines = output.split ("\n")
        self.header = lines [0]
        for line in lines[1:-1]:
            fs, blocks, used, avail, usep, *mounted = line.split ()
            self.data.append ({
                'Filesystem': fs,
                '1K-blocks': int (blocks),
                'Used': int (used),
                'Available': int (avail),
                'Use%': usep,
                'Mounted on': ' '.join (mounted)
            })
