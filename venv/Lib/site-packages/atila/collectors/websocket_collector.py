from .grpc_collector import GRPCStreamCollector
from io import BytesIO
from aquests.protocols.ws import *
from aquests.protocols.ws.collector import Collector as BaseWebsocketCollector

class WebsocketCollector (BaseWebsocketCollector, GRPCStreamCollector):
    def __init__ (self, handler, request, *args):
        self.handler = handler
        self.request = request
        self.content_length = -1

        self.msgs = []
        self.rfile = BytesIO ()
        self.masks = b""
        self.has_masks = True
        self.buf = b""
        self.payload_length = 0
        self.opcode = None
        self.default_op_code = OPCODE_TEXT
        self.ch = self.channel = request.channel

        self.initialize_stream_variables ()

    def collect_incoming_data (self, data):
        if not data:
            # closed connection
            self.close ()
            return

        if self.masks or (not self.has_masks and self.payload_length):
            self.rfile.write (data)
        else:
            self.buf += data

    def start_collect (self):
        self.channel.set_terminator (2)
        self.first_data and self.continue_request ()

    def flush (self):
        if not self.proxy:
            return
        while self.msgs:
            self.queue.append (self.msgs.pop (0))
            self.callback ()
        if self.end_of_data:
            self.callback ()

    def close (self):
        self.end_of_data = True
        GRPCStreamCollector.close (self)

    def handle_message (self, msg):
        GRPCStreamCollector.handle_message (self, msg)
        self.flush ()
