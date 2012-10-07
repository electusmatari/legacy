#!/usr/bin/env python

import cookielib
import urllib2
import urllib
import wave
import StringIO
import os
import sys
import hashlib
import re
import logging
import tempfile

URL_RAW_MAIL = "http://static.griefwatch.net/raw_mail.php?boardID=%s&mailID=%s"
URL_AUDIO = "http://static.griefwatch.net/captcha/securimage_play.php"
URL_CAPTCHA = "http://static.griefwatch.net/raw_mail.php"

AUDIO_MAP = {
    '15e3fe94987b7f38ba8533635ddacc72': 'A',
    '340221cc0e8756cfce953d4e0c29e538': 'C',
    '2ccf4a438aa88aaa6957bdca97e38c10': 'C',
    '5c189e080490b7aa261aea09d93d34a0': 'D',
    '45973af0d4ddff6ba6009556ae5093ff': 'E',
    '9ccbe7d2dfef7f80633a6e1972299810': 'F',
    '812f9888c7065ee19feacbfde6a50029': 'G',
    'cd21c91afdf42008889fdc3f1582331b': 'H',
    'aba58ca670e127d9b71f9658c9914359': 'K',
    'e25e67a85514d96d957cc34017a261e5': 'L',
    'b332325f4737121bb8d1e05896c29754': 'L',
    '3f18f4726a94d64849dc99d69a0101c6': 'M',
    'ba1a78d6dd0d68e500f282f729fbab9b': 'R',
    '16f7fdb8b5ca49d36b5f079a8e49a789': 'S',
    'a5c3443e8a13fbfaa8b38af9f1b1686e': 'T',
    '9f5277a3971914345d6ce7dade5d7589': 'T',
    '0bd7f2d0e2718c86d4a0e367419cd6c4': 'U',
    '25a5ea14edc521e480f67ec0e34dd191': 'V',
    '0dc77c65ac4a43e12ebc4b0847419944': 'V',
    '6e0424aaf2afdeef1aa0d2397cd88b5b': 'W',
    '72a508019c6312cc4095d2fb11c9ed96': 'Y',

    '27eedc238f8ba86881459f18defa3bc9': '2',
    '1c00e7beec612b20ee6937cfd4debb62': '3',
    'b61fe39d737320ed16921a0dda4b74b7': '4',
    '7a65a4a2e5256e27ad3415b4c57a2776': '5',
    'aee02c3f10fb5ddf5014e3e912d58b52': '6',
    'b2b13f7c937d2d24baababb409826754': '7',
    'da0e7bb340aeb1aa9066401fea88f401': '8',
    '8faafe764b4da9f20d065eae79bafaca': '9',
    }

log = logging.getLogger("gwlib")

# def main():
#     boardid = 163
#     mailid = 38974
#     print getkm([(boardid, mailid)])

def getkms(killmails):
    """
    Retrieve killmails.

    killmails is a list of (boardid, mailid) tuples.
    """
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    results = []
    for boardid, mailid in killmails:
        r = opener.open(URL_RAW_MAIL % (boardid, mailid))
        data = r.read()
        if "securimage_show.php" in data:
            r = opener.open(URL_AUDIO)
            wavdata = r.read()
            captcha = recognize(wavdata)
            r = opener.open(URL_CAPTCHA,
                            urllib.urlencode({'boardID': str(boardid),
                                              'mailID': str(mailid),
                                              'captcha': captcha,
                                              'do': 'Check'}))
            data = r.read()
            if "securimage_show.php" in data:
                md5 = hashlib.md5(wavdata).hexdigest()
                (fd, fname) = tempfile.mkstemp(prefix=md5 + "-",
                                               suffix=".wav")
                f = os.fdopen(fd, "wb")
                f.write(wavdata)
                f.close()
                log.warning("Bad recognition of full-length file %s, please re-check" %
                            (fname,))
                continue
        parsed = parsekm(data)
        if parsed is None:
            log.error("Bad kill mail format for boardID %s, mailID %s: %r" %
                      (boardid, mailid, data))
        results.append((boardid, mailid, data))
    return results

def parsekm(data):
    m = re.match("^(?:.|\n)*<body>[^0-9]*((?:.|\n)*)</body>(?:.|\n)*$",
                 data,
                 re.MULTILINE)
    if m is None:
        return None
    else:
        return m.group(1).replace("<br>", "\n")

def recognize(data):
    s = StringIO.StringIO(data)
    s.seek(0)
    r = wave.open(s, "rb")
    frames = r.readframes(11026)
    result = []
    while frames != '':
        md5 = hashlib.md5(frames).hexdigest()
        o = StringIO.StringIO()
        w = wave.open(o, "wb")
        w.setnchannels(r.getnchannels())
        w.setsampwidth(r.getsampwidth())
        w.setframerate(r.getframerate())
        w.writeframes(frames)
        w.close()
        o.seek(0)
        md5 = hashlib.md5(o.read()).hexdigest()
        if md5 in AUDIO_MAP:
            result.append(AUDIO_MAP[md5])
        else:
            (fd, fname) = tempfile.mkstemp(prefix=md5 + "-",
                                           suffix=".wav")
            f = os.fdopen(fd, "wb")
            o.seek(0)
            f.write(o.read())
            f.close()
            log.warning("Unknown individual character, please add %s" % (
                    (fname,)))
            return None
        frames = r.readframes(11026)
    return "".join(result)
