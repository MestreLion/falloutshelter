#!/usr/bin/env python3
#
#    Copyright (C) 2018 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>


"""
    Fallout Shelter save game encryptor and decryptor

    Saved games are Vault*.sav files, located at:

    Android: /Android/data/com.bethsoft.falloutshelter/files
    Windows: C:\\Users\\YOURUSERNAME\\Documents\\My Games\\Fallout Shelter
    Steam:   C:\\Users\\YOURUSERNAME\\AppData\\Local\\FalloutShelter

    Currently reads binary data from stdin and output formatted JSON to stdout

    Usage:
        ./fscrypt3 < Vault1.save > Vault1.json
"""


import sys
import base64
import json


import Crypto.Cipher.AES as AES  # PyPI: pip install pycrypto


IV  = b'tu89geji340t89u2'
KEY = b'A7CA9F3366D892C2F0BEF417341CA971B69AE9F7BACCCFFCF43C62D1D7D021F9'
CIPHER = AES.new(base64.b16decode(KEY), AES.MODE_CBC, IV)


def fs_key():
    '''
    Alternate ways to calculate AES key for CIPHER using PASSWORD and SALT
    This function is purely optional, kept only for historical purposes

    Constants taken from disassembled game source code:
    https://androidrepublic.org/threads/6181

    IV is used as both PBKDF2 key salt and AES IV.
    Its value was very likely chosen copying from an old SO answer
    https://stackoverflow.com/revisions/10177020/2
    '''

    SALT = IV
    PASSWORD = base64.b64encode(b'PlayerData')[:8]  # b'UGxheWVy'
    KEYSIZE  = 32

    # Method 1: PBKDF2() from pycrypto v2.5+
    import Crypto.Protocol.KDF as KDF
    return KDF.PBKDF2(PASSWORD, SALT, KEYSIZE)

    # Method 2: pbkdf2_hmac() from Standard Library
    import hashlib
    return hashlib.pbkdf2_hmac('sha1', PASSWORD, SALT, 1000, KEYSIZE)


def fs_decrypt(savedata):
    '''
    Decrypts a Fallout Shelter save game data

    @savedata: binary save game data (str in Python 2, bytes in Python 3)
    @output  : JSON text, one-liner  (str in both Python 2 and 3)
    '''

    # Decode and decrypt the save data
    data = CIPHER.decrypt(base64.b64decode(savedata))

    # Remove trailing padding (N bytes of value N) and convert to string
    data = data[:-data[-1]].decode('ascii')

    return data


def prettyjson(data):
    obj = json.loads(data, strict=False)
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',',':'))


# Print formatted output
# b64decode() on PY2 and 3 takes bytes on input, so need a binary stdin
print(prettyjson(fs_decrypt((sys.stdin.buffer).read())))
