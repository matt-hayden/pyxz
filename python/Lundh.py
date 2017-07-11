#! /usr/bin/env python2
import re

def tokenize(text, pattern=re.compile("([idel])|(\d+):|(-?\d+)")):
    i = 0
    while i < len(text):
        m = pattern.match(text, i)
        s = m.group(m.lastindex)
        i = m.end()
        if m.lastindex == 2:
            yield "s"
            yield text[i:i+int(s)]
            i = i + int(s)
        else:
            yield s

def decode_item(callback, token):
    if token == "i":
        # integer: "i" value "e"
        data = int(callback())
        if callback() != "e":
            raise ValueError
    elif token == "s":
        # string: "s" value (virtual tokens)
        data = callback()
    elif token == "l" or token == "d":
        # container: "l" (or "d") values "e"
        data = []
        tok = callback()
        while tok != "e":
            data.append(decode_item(callback, tok))
            tok = callback()
        if token == "d":
            data = dict(zip(data[0::2], data[1::2]))
    else:
        raise ValueError
    return data

def decode(text):
    try:
        src = tokenize(text)
        data = decode_item(src.next, src.next())
        for token in src: # look for more tokens
            raise SyntaxError("trailing junk")
    except (AttributeError, ValueError, StopIteration):
        raise SyntaxError("syntax error")
    return data
