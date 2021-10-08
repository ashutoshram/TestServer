import os
import re
from skitai.handlers import collectors
from skitai.corequest import corequest

class StreamCollector (collectors.FormCollector, corequest):
    DEFAULT_BUFFER_SIZE = 65536
    END_DATA = b''

    def __init__ (self, handler, request, *args, **kargs):
        self.handler = handler
        self.request = request
        self.te = request.get_header ('transfer-encoding')
        self.ch = request.channel
        self.content_length = -1
        self.buffer = b''
        self.buffer_size = 0
        self.length = b''
        self.initialize_stream_variables ()

    def initialize_stream_variables (self):
        self.closed = False
        self.first_data = True
        self.end_of_data = False
        self.proxy = None
        self.queue = []

    def set_proxy_coroutine (self, proxy):
        self.proxy = proxy
        self.flush ()

    def fetch (self):
        if not self.queue and self.end_of_data:
            return self.END_DATA
        return self.queue.pop (0)

    #----------------------------------------------------
    @property
    def bs (self):
        return self.buffer_size or self.DEFAULT_BUFFER_SIZE

    def set_max_buffer_size (self, buffer_size):
        self.buffer_size = buffer_size

    def start_collect (self):
        self.ch.set_terminator (b'\r\n')

    def collect_incoming_data (self, data):
        if self.ch.get_terminator () == b'\r\n':
            self.length += data
            return
        self.buffer += data

    def continue_request (self):
        self.first_data = False
        self.handler.continue_request (self.request, self)

    def callback (self):
        try:
            self.proxy.send (self)
        except ValueError:
            pass

    def flush (self):
        self.first_data and self.continue_request ()
        if not self.proxy:
            return
        for _ in range (len (self.buffer) // self.bs):
            b, self.buffer = self.buffer [:self.bs], self.buffer [self.bs:]
            self.queue.append (b)
            self.callback ()

        if self.end_of_data:
            if self.buffer:
                b, self.buffer = self.buffer, []
                self.queue.append (b)
                self.callback ()
            self.callback ()

    def close (self):
        if not self.closed:
            self.request.collector = None
            self.ch.set_terminator (b"\r\n\r\n")
            self.closed = True
            self.flush ()

    def found_terminator (self):
        current_terminator = self.ch.get_terminator ()
        if self.end_of_data:
            self.close ()
            return

        if self.length:
            length, self.length = self.length, b''
            chunked_size = int (length.split (b";") [0], 16)
            if chunked_size == 0:
                self.end_of_data = True
                self.ch.set_terminator (b"\r\n")
            elif chunked_size > 0:
                self.ch.set_terminator (chunked_size)
            return

        self.ch.set_terminator (b"\r\n")
        self.flush ()
