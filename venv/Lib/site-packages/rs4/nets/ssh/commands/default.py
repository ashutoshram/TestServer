class Result:
    def __init__ (self, output, cmd = None):
        self._cmd = cmd
        self.output = output
        self.header = None
        self.meta = {}
        self.data = []
        self.parse_output (output)

    @property
    def command (self):
        if self._cmd:
            return self._cmd
        return self.__class__.__module__.split ('.')[-1]

    def parse_output (self, output):
        self.data = output.split ("\n")[:-1]
