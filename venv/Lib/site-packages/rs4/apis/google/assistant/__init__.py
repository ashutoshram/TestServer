# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sample that implements a gRPC client for the Google Assistant API."""

import logging
import os
import sys
import multiprocessing
import click
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials
import random
import shutil
from .... import pathtool
from tenacity import retry, stop_after_attempt, retry_if_exception
from .grpc import audio_helpers, device_helpers
from . import device_register, modulator
from . import sources, assistant
import json

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5
DEVICE_MODEL_ID = None
DEVICE_ID = None
logging.basicConfig (level=logging.INFO)
device_handler = None
tmpdir = '/tmp/rs4/google-assistant'
pathtool.mkdir (tmpdir)

audio_sample_rate = audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE
audio_sample_width = audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH
audio_iter_size = audio_helpers.DEFAULT_AUDIO_ITER_SIZE
audio_block_size = audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE
audio_flush_size = audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
lock = multiprocessing.Lock ()

# device registering ------------------------------------------
def get_client_id ():
    try:
        with open (os.path.expanduser ('~/.config/google-oauthlib-tool/credentials.json')) as f:
            d = json.load (f)
    except FileNotFoundError:
        raise FileNotFoundError ('OAuth credentail not found. run `google-oauthlib-tool`')
    return d ['client_id']

def register_device (device_model_id, project_id = None, oauth = None):
    global ASSISTANT_API_ENDPOINT, DEVICE_MODEL_ID, DEVICE_ID, grpc_channel, device_handler

    if not project_id:
        project_id = '-'.join (device_model_id.split ('-')[:2])

    if not oauth:
        try:
            with open(os.path.join(click.get_app_dir('google-oauthlib-tool'), 'credentials.json'), 'r') as f:
                oauth = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError ('OAuth credentail not found. run `google-oauthlib-tool`')

    credentials = google.oauth2.credentials.Credentials(token=None, **oauth)
    DEVICE_ID, DEVICE_MODEL_ID = device_register.register (ASSISTANT_API_ENDPOINT, project_id, device_model_id)
    http_request = google.auth.transport.requests.Request()
    credentials.refresh(http_request)
    grpc_channel = google.auth.transport.grpc.secure_authorized_channel (credentials, http_request, ASSISTANT_API_ENDPOINT)
    device_handler = device_helpers.DeviceRequestHandler (DEVICE_ID)


# conversation ------------------------------------------
def _request (audio_source, lang, output_audio_file, display, verbose, timeout, listening_handler):
    global DEVICE_MODEL_ID, DEVICE_ID, grpc_channel, lock, device_handler

    output_audio_file =  output_audio_file or os.path.join (tmpdir, 'out-' + str (random.random ()) [2:] + '.wav')
    audio_sink = audio_helpers.WaveSink(
        open(output_audio_file, 'wb'),
        sample_rate=audio_sample_rate,
        sample_width=audio_sample_width
    )

    # Create conversation stream with the given audio source and sink.
    conversation_stream = audio_helpers.ConversationStream (
        source = audio_source,
        sink = audio_sink,
        iter_size = audio_iter_size,
        sample_width = audio_sample_width,
    )

    with lock:
        # ensure single thread
        with assistant.Assistant (lang, DEVICE_MODEL_ID, DEVICE_ID,
                            conversation_stream, display,
                            grpc_channel, timeout,
                            device_handler,
                            listening_handler) as assi:

            question, supplemental_display_text, detail = assi.assist ()
            return assistant.Answer (lang, question, supplemental_display_text, detail, output_audio_file)


def send_wav (input_audio_file, lang = 'ko-KR', output_audio_file = None, display = True, verbose = False, timeout = DEFAULT_GRPC_DEADLINE, listening_handler = None):
    audio_source = audio_helpers.WaveSource (
        open(input_audio_file, 'rb'),
        sample_rate=audio_sample_rate,
        sample_width=audio_sample_width
    )
    return _request (audio_source, lang, output_audio_file, display, verbose, timeout, listening_handler)

def use_device (device, lang = 'ko-KR', output_audio_file = None, display = True, verbose = False, timeout = DEFAULT_GRPC_DEADLINE, listening_handler = None):
    if isinstance (device, (int, str)):
        audio_source = sources.SoundDeviceInputStream (
            sample_rate=16000,
            sample_width=2,
            block_size=6400,
            device = device
        )
    else:
        audio_source = device # instance of VirtuslDeviceInoutStream
    resp = _request (audio_source, lang, output_audio_file, display, verbose, timeout, listening_handler)
    audio_source.close ()
    return resp

