import librosa
import soundfile
from pysndfx import AudioEffectsChain
import os

# apt install sox
# pip3 install -U pysndfx

MODULATORS = {
    'ko-KR': (
        AudioEffectsChain ()
            .pitch (-10, True)
            .speed (230, True)
            .equalizer (1000, 0.2, 7.0)
            .equalizer (100, 0.2, -10)
            .equalizer (300, 0.7, 5)
            .equalizer (3000, 0.7, -5)
    ),
    'default': (
        AudioEffectsChain ()
            .pitch (100, True)
            .speed (100, True)
            .equalizer (1000, 0.2, 7.0)
            .equalizer (100, 0.2, -10)
            .equalizer (300, 0.7, 5)
            .equalizer (3000, 0.7, -5)
    )
}

def modulate (y, output, lang = 'en-US', sr = 16000):
    if isinstance (y, str):
        y, sr = librosa.load (y, sr)
    assert len (y) > 0
    fx = MODULATORS.get (lang)
    if fx is None:
        fx = MODULATORS ['default']
    soundfile.write (output, fx (y), sr)
    assert os.path.isfile (output)
    return output


if __name__ == "__main__":
    modulate ('samples/gavoices/ko-asstitant.mp3', 'ttt1.wav', lang = 'ko-KR')
    modulate ('samples/gavoices/en-asstitant.mp3', 'ttt2.wav', lang = 'en-US')
