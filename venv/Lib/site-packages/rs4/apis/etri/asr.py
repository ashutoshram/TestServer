import json
import base64
import librosa
from io import BytesIO
import soundfile
import os
from ... import pathtool
from ...webkit import siesta

def resampling (audioFilePath):
    y, sr = librosa.load (audioFilePath, sr = 22050, mono = True)
    with BytesIO () as f:
       soundfile.write (f, y, 16000, format = "WAV")
       return f.getvalue ()

openApiURL = "http://aiopen.etri.re.kr:8000"
API = siesta.API (openApiURL)

def get_speech (audioFilePath, lang = "korean"):
    from . import ACCESS_KEY

    audioContents = base64.b64encode (resampling (audioFilePath)).decode("utf8")
    requestJson = {
        "access_key": ACCESS_KEY,
        "argument": {"audio": audioContents, "language_code": lang},
        "request_id": "sns",
    }
    resp = API.WiseASR.Recognition.post (
        requestJson,
        {"Content-Type": "application/json; charset=UTF-8"}
    )
    try:
        assert resp.status_code == 200
        text = resp.data ['return_object']['recognized']
    except (AssertionError, KeyError):
        return ''
    return text
