from collections import Counter
import string

def guess_delimiters(iterable, skip=0, exclude=string.letters+string.digits):
    iterable = list(iterable)[skip:]
    line = iterable.pop(0)
    # equal frequencies of characters:
    delims = set(Counter(line).items())
    for line in iterable:
        delims &= set(Counter(line).items())
        if not delims: return []
    delims = [ (c, n) for (c, n) in delims if c not in exclude ]
    return [ c for c, n in sorted(delims, key=lambda (c, n): n) ]
