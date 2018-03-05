#! /usr/bin/env python3
"""
Generate code to parallelize xz, taking into account file size and number of processors. File arguments are compressed and concatenated, outputting a (strictly ordered!) set of filenames.

Usage:
    pxz [options] [--] [FILE...]

Options:
    -h --help       Show this help
    -v --verbose    Show work [default: None]
    -n --dry-run    Don't do work

    --eta
    -j N --jobs N
    -P N --max-procs N
    --output-as-files
    --outputasfiles
    --files
    --progress

More functionality is exposed in Python
"""
__version__ = '0.1.0'

from pathlib import Path
import sys

import docopt

from . import *

def main(verbose=(sys.stderr.isatty() or __debug__)):
    execname, *args = sys.argv
    options = docopt.docopt(__doc__, version=__version__)
    file_paths = [ Path(p) for p in options.pop('FILE') ]
    del options['--']
    parallel_args = []
    for k, v in options.items():
        if v:
            parallel_args.append(k)
            if v is not True:
                parallel_args.append(v)
    syntax = generate_commands(*file_paths, parallel_args=parallel_args)
    if options['--verbose']:
        print('  '+'\n  '.join(syntax), file=sys.stderr)
    if options['--dry-run']:
        if (not sys.stdin.isatty()):
            print('# stdin is lost')
        print('\n'.join(syntax))
    else:
        proc = subprocess.run('; '.join(syntax), shell=True)
        return proc.returncode
