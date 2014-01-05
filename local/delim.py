from collections import Counter

def guess_delimiters(iterable, skip=0):
    iterable = list(iterable)[skip:]
    line = iterable.pop(0)
    delims = set(Counter(line).items())
    for line in iterable:
        delims &= set(Counter(line).items())
        if not delims: return []
    return [ c for c, n in sorted(delims, key=lambda (c, n): n) ]
