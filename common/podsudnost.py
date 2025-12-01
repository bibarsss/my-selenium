import re
from globals import Podsudnost

oblastMap = Podsudnost().load_json().data

def getPodsudnostValue(podsudnost: str)->dict:
    podsudnostNormalized = normalize_text(podsudnost.lower())
    for oblast in oblastMap:
        for sud in oblastMap[oblast]['sudebnieOrgany']:
            sudNormalized = normalize_text(sud.lower())
            if podsudnostNormalized in sudNormalized:
                return {
                    "sudValue": oblastMap[oblast]['sudebnieOrgany'][sud],
                    "oblastValue": oblastMap[oblast]['value'],
                    'sudName': sud,
                }

    return {
       "sudValue": None,
       "oblastValue": None,
       'sudName': None
    }

def normalize_text(s: str) -> str:
    s = s.replace('\xa0', ' ')  # replace non-breaking spaces
    s = re.sub(r'\s+', ' ', s)  # collapse multiple spaces/tabs/newlines
    return s.strip()