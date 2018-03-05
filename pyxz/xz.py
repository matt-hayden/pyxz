#! /usr/bin/env python3

import bisect
import shlex
import subprocess

from .util import *


# Block size (in binary bytes) for each compression level
xz_levels = [ 256<<10, 1<<20, 2<<20, 4<<20, 4<<20, 8<<20, 8<<20, 16<<20, 32<<20, 64<<20 ]


def get_compression_level(buffer_size, xz_levels=xz_levels):
    place = bisect.bisect_left(xz_levels, buffer_size)
    return min(place, len(xz_levels)-1)


def get_pipeline_args(level):
    return { 'xz': ['-%d' % level, '--block-size=%d' % xz_levels[level]],
             'parallel': ['--block-size', '%d' % xz_levels[level]] }


def generate_commands(*file_args, parallel_args=[], nproc=None, verbose=None, **kwargs):
    lines = []
    y = lines.append
    if not any((a in parallel_args) for a in '--output-as-files --outputasfiles --files'.split()):
        y( 'if [ -t 1 ]; then echo "Refusing to dump binary to terminal"; exit 1; fi' )
    if nproc is None:
        i = max(safe_index(parallel_args, a) for a in '-j --jobs -P --max-procs'.split())
        if (0 <= i):
            n = parallel_args[i+1]
            nproc = NPROC*float(n.replace('%', 'E-2')) if ('%' in n) else int(n)
        else:
            nproc = NPROC
    def apply_parallel_args(command):
        return command+parallel_args
    if file_args:
        for f in file_args:
            assert f
            level = get_compression_level(f.stat().st_size//nproc)
            pipeline_args = get_pipeline_args(level)
            parallel_command = ['parallel', '-k', '--recend', '', '--pipepart']+pipeline_args['parallel']
            xz_command = [shlex.quote(s) for s in ['xz', '-c']+pipeline_args['xz']]
            y( ' '.join(shlex.quote(s) for s in apply_parallel_args(parallel_command))+' '+ \
               ' '.join(shlex.quote(s) for s in [' '.join(xz_command), '::::']+[str(f)]) )
    else:
        level = 6 # the xz default
        pipeline_args = get_pipeline_args(level)
        parallel_command = ['parallel', '-k', '--recend', '', '--pipe']+pipeline_args['parallel']
        xz_command = [shlex.quote(s) for s in ['xz', '-c']+pipeline_args['xz']]
        y( ' '.join(shlex.quote(s) for s in apply_parallel_args(parallel_command))+' ' + \
           ' '.join(shlex.quote(s) for s in [' '.join(xz_command)]) )
    return lines
