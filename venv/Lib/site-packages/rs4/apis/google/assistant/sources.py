import os
import collections
import threading
import sounddevice as sd
from .grpc import audio_helpers
from .grpc.audio_helpers import (
    DEFAULT_AUDIO_SAMPLE_RATE, # 16000
    DEFAULT_AUDIO_SAMPLE_WIDTH, # 2
    DEFAULT_AUDIO_DEVICE_BLOCK_SIZE # 6400
)

class InputStreamBase:
    def __init__(self, sample_rate = DEFAULT_AUDIO_SAMPLE_RATE, sample_width = DEFAULT_AUDIO_SAMPLE_WIDTH, block_size = DEFAULT_AUDIO_DEVICE_BLOCK_SIZE):
        if sample_width != 2:
            raise Exception('unsupported sample width:', sample_width)
        self._sample_rate = sample_rate
        self._sample_width = sample_width
        self._block_size = block_size

    def read (self, size):
        raise NotImplementedError

    def start (self):
        raise NotImplementedError

    def stop (self):
        raise NotImplementedError

    def close (self):
        raise NotImplementedError

    def write (self):
        raise AttributeError
    flush = write


class SoundDeviceInputStream (audio_helpers.SoundDeviceStream, InputStreamBase):
    def __init__(self, sample_rate = DEFAULT_AUDIO_SAMPLE_RATE, sample_width = DEFAULT_AUDIO_SAMPLE_WIDTH, block_size = DEFAULT_AUDIO_DEVICE_BLOCK_SIZE, device = None):
        InputStreamBase.__init__ (self, sample_rate, sample_width, block_size)
        self._audio_stream = sd.RawInputStream (
            samplerate = sample_rate, dtype = 'int16', channels = 1, device = device,
            blocksize = int (block_size/2)  # blocksize is in number of frames.
        )


class VirtualDeviceInputStream (InputStreamBase):
    def __init__ (self, sample_rate = DEFAULT_AUDIO_SAMPLE_RATE, sample_width = DEFAULT_AUDIO_DEVICE_BLOCK_SIZE, block_size = DEFAULT_AUDIO_DEVICE_BLOCK_SIZE):
        super ().__init__ (sample_rate, sample_width, block_size)
        self._lock = threading.Condition ()
        self._stopped = True
        self._stand_by = False
        self._streams = collections.deque ()

    def put (self, stream):
        with self._lock:
            if self._stopped:
                return
            self._streams.append (stream)
            self._lock.notify ()

    def read (self, size, *args, **kargs):
        with self._lock:
            if self._stopped:
                raise IOError ('closed input stream')
            while not self._stopped and (not self._streams or sum ([len (s) for s in self._streams]) < size):
                self._lock.wait ()
            if self._stopped:
                return b''
            data = b''
            while 1:
                first = self._streams.popleft ()
                if len (data) + len (first) < size:
                    data += first
                else:
                    wanted = size - len (data)
                    data += first [:wanted]
                    self._streams.appendleft (first [wanted:])
                    break
            assert len (data) == size
        return data

    def get_ready (self):
        with self._lock:
            self._stand_by = True

    def start (self):
        with self._lock:
            if not self._stand_by:
                # ignore start
                return
            self._streams.clear ()
            self._stopped = False
            self._lock.notify ()

    def stop (self):
        with self._lock:
            self._stopped = True
            self._lock.notify ()

    def close (self):
        self.stop ()

