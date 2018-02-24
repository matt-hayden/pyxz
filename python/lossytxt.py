#! /usr/bin/env python3
import base64
import string
import subprocess

lookup = ['.']*128
for c in string.whitespace+'_':
    lookup[ord(c)] = '_'
for c in string.ascii_letters+string.digits:
    lookup[ord(c)] = c
lookup = ''.join(lookup)
def xlate(word, lookup=lookup):
    return ''.join(lookup[ord(c)] for c in word)

def lossy_decode(binary):
    assert isinstance(binary, bytes)
    return base64.b64encode(binary, b'_.')

def lossy_encode(text):
    encoded = '_'.join(xlate(w) for w in text.split() if w)
    while encoded and not encoded.endswith('..'):
        encoded += '.'
    offset = len(encoded) % 4
    if offset:
        encoded += [ '', '_==', '==', '=' ][offset]
    return base64.b64decode(encoded, '_.')

def lossy_decode_files(*args):
    for arg in args:
        if isinstance(arg, str):
            with open(arg, 'rb') as fi:
                content = fi.read()
        else:
            content = arg.read()
        yield lossy_decode(content).decode()


if __name__ == '__main__':
    import sys
    execname, *args = sys.argv
    if sys.stdout.isatty():
        print( '\n'.join( lossy_decode_files(*(args or [sys.stdin.buffer])) ) )
    else:
        p = subprocess.run(['iconv', '-t', 'ascii//TRANSLIT']+args, stdout=subprocess.PIPE)
        assert p
        assert (p.returncode == 0)
        sys.stdout.buffer.write(lossy_encode(p.stdout.decode()))
