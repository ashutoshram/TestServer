from .houndify import *
import re

CLIENT_ID, CLIENT_KEY = None, None

def set_credential (client_id, client_key):
    global CLIENT_ID, CLIENT_KEY

    CLIENT_ID, CLIENT_KEY = client_id, client_key

RE_PRONOUNCE = re.compile (r"\(/.+?/\)")
def get_answer (question, user = 'test_user'):
    global CLIENT_ID, CLIENT_KEY

    client = houndify.TextHoundClient (CLIENT_ID, CLIENT_KEY, user)
    response = client.query(question)
    try:
        best = response ['AllResults'][0]
    except (KeyError, IndexError):
        return {}
    else:
        subject = best ['WrittenResponse']
        answer = RE_PRONOUNCE.sub ('', best ['WrittenResponseLong'])
        return dict (
            best = {}, answer = answer, subject = subject
        )
