from ... import pathtool
import os
from .speech import (
    get_speech,
    get_translate
)

DEFAULT_CREDENTIAL = os.path.expanduser ('~/.config/googleapi/credentials.json')

def set_credential (path = None):
    global DEFAULT_CREDENTIAL

    path = path or DEFAULT_CREDENTIAL
    assert os.path.isfile (path), 'credential file not found: {}'.format (path)
    os.environ ['GOOGLE_APPLICATION_CREDENTIALS'] = path

if os.path.isfile (DEFAULT_CREDENTIAL):
    set_credential ()
