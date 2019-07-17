# bencoding
# http://www.bittorrent.org/beps/bep_0003.html

"""
Strings are length-prefixed base ten followed by a colon and the string.
For example 4:spam corresponds to 'spam'.

>>> encode(b'spam')
b'4:spam'

Integers are represented by an 'i' followed by the number in base 10 followed by an 'e'.
For example i3e corresponds to 3 and i-3e corresponds to -3.
Integers have no size limitation. i-0e is invalid.
All encodings with a leading zero, such as i03e, are invalid,
other than i0e, which of course corresponds to 0.

>>> decode(b'i3e')
3
>>> decode(b'i-3e')
-3
>>> decode(b'i0e')
0
>>> decode(b'i03e')
Traceback (most recent call last):
  ...
ValueError: invalid literal for int() with base 0: '03'


Lists are encoded as an 'l' followed by their elements (also bencoded) followed by an 'e'.
For example l4:spam4:eggse corresponds to ['spam', 'eggs'].

>>> decode(b'l4:spam4:eggse')
[b'spam', b'eggs']

Dictionaries are encoded as a 'd' followed by a list of alternating keys
and their corresponding values followed by an 'e'.
For example, d3:cow3:moo4:spam4:eggse corresponds to {'cow': 'moo', 'spam': 'eggs'}
Keys must be strings and appear in sorted order (sorted as raw strings, not alphanumerics).

>>> decode(b'd3:cow3:moo4:spam4:eggse')
OrderedDict([(b'cow', b'moo'), (b'spam', b'eggs')])

"""
from collections import OrderedDict

# --- PART OF DECODING ---
def decode_int(val, ind):
    ind += 1
    new_ind = val.index(b'e', ind)
    n = int(val[ind:new_ind])
    if val[ind] == ord('-'):
        if val[ind + 1] == ord('0'):
            raise ValueError()
    elif val[ind] == ord('0') and new_ind != ind + 1:
        raise ValueError()
    return n, new_ind + 1


def decode_string(val, ind):
    col = val.index(b':', ind)
    n = int(val[ind:col])
    if val[ind] == ord('0') and col != ind + 1:
        raise ValueError()
    col += 1
    return val[col:col + n], col + n


def decode_list(val, ind):
    r, ind = [], ind + 1
    while val[ind] != ord('e'):
        v, ind = decode_func[val[ind]](val, ind)
        r.append(v)
    return r, ind + 1


def decode_dict(val, ind):
    r, ind = OrderedDict(), ind + 1
    #r, ind = {}, ind + 1
    while val[ind] != ord('e'):
        k, ind = decode_string(val, ind)
        r[k], ind = decode_func[val[ind]](val, ind)
    return r, ind + 1

decode_func = {
    ord('l'): decode_list,
    ord('d'): decode_dict,
    ord('i'): decode_int,
    ord('1'): decode_string,
    ord('2'): decode_string,
    ord('3'): decode_string,
    ord('4'): decode_string,
    ord('5'): decode_string,
    ord('6'): decode_string,
    ord('7'): decode_string,
    ord('8'): decode_string,
    ord('9'): decode_string,
    ord('0'): decode_string,
    }

def decode(val):
    try:
        r, l = decode_func[val[0]](val, 0)
    except (IndexError, KeyError, ValueError):
        raise ValueError("invalid input data")
    if l != len(val):
        raise ValueError("invalid input data after valid prefix")
    return r

# --- PART OF ENCODING ---
def encode_int(val, r):
    r.extend((b'i', str(val).encode(), b'e'))

def encode_string(val, r):
    #r.extend((str(len(val)).encode(), b':', val))
    r.extend((str(len(val)).encode(), b':', val))

def encode_list(val, r):
    r.append(b'l')
    for i in val:
        encode_func[type(i)](i, r)
    r.append(b'e')

def encode_dict(val, r):
    r.append(b'd')
    item_list = list(val.items())
    item_list.sort()
    for k, v in item_list:
        r.extend((str(len(k)).encode(), b':', k))
        encode_func[type(v)](v, r)
    r.append(b'e')

encode_func = {
    int: encode_int,
    str: encode_string,
    bytes: encode_string,
    list: encode_list,
    tuple: encode_list,
    dict: encode_dict,
    }

def encode(val):
    r = []
    encode_func[type(val)](val, r)
    return b''.join(r)

# ---- RUN TEST -----
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.IGNORE_EXCEPTION_DETAIL)
    print(doctest.testmod(optionflags=doctest.IGNORE_EXCEPTION_DETAIL))