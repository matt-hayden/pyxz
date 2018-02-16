#! /usr/bin/env python3
"""
Generate code to parallelize xz. File arguments are compressed and concatenated.
"""
import bisect
import os, os.path
import shlex
import subprocess


nproc = int(subprocess.check_output(['nproc'])) or \
        int(subprocess.check_output(['parallel', '--number-of-cores'])) or \
        1
# see also multiprocessing
xz_levels = [ 256<<10, 1<<20, 2<<20, 4<<20, 4<<20, 8<<20, 8<<20, 16<<20, 32<<20, 64<<20 ]


def get_compression_level(buffer_size):
    place = bisect.bisect_left(xz_levels, buffer_size)
    return min(place, len(xz_levels)-1)


def get_pipeline_args(level):
    return { 'xz': ['-%d' % level, '--block-size=%d' % xz_levels[level]],
             'parallel': ['--block-size', '%d' % xz_levels[level]] }

    
def generate_commands(*file_args, parallel_args=[], verbose=None, **kwargs):
    lines = []
    y = lines.append
    if not any((a in parallel_args) for a in '--output-as-files --outputasfiles --files'.split()):
        y( 'if [ -t 1 ]; then echo "Refusing to dump binary to terminal"; exit 1; fi' )
    def apply_parallel_args(command):
        return command+parallel_args
    if any(file_args):
        for f in file_args:
            level = get_compression_level(os.path.getsize(f)//nproc)
            pipeline_args = get_pipeline_args(level)
            parallel_command = ['parallel', '-k', '--recend', '', '--pipepart']+pipeline_args['parallel']
            xz_command = [shlex.quote(s) for s in ['xz', '-c']+pipeline_args['xz']]
            y( ' '.join(shlex.quote(s) for s in apply_parallel_args(parallel_command))+' '+ \
               ' '.join(shlex.quote(s) for s in [' '.join(xz_command), '::::']+[f]) )
    else:
        level = 6 # the xz default
        pipeline_args = get_pipeline_args(level)
        parallel_command = ['parallel', '-k', '--recend', '', '--pipe']+pipeline_args['parallel']
        xz_command = [shlex.quote(s) for s in ['xz', '-c']+pipeline_args['xz']]
        y( ' '.join(shlex.quote(s) for s in apply_parallel_args(parallel_command))+' ' + \
           ' '.join(shlex.quote(s) for s in [' '.join(xz_command)]) )
    return lines


if __name__ == '__main__':
    import sys
    execname, *args = sys.argv

    # TODO: cli parsing
    options = { 'dry-run': False, 'verbose': (sys.stderr.isatty() or __debug__) }
    if '--' in args:
        i = args.index('--')
        options['parallel_args'] = args[:i]
        file_args = args[i+1:]
    else:
        file_args = args
    syntax = generate_commands(*file_args, **options)
    code = None
    if options['verbose']:
        print('  '+'\n  '.join(syntax), file=sys.stderr)
    if options['dry-run']:
        if (not sys.stdin.isatty()):
            print('# stdin is lost')
        print('\n'.join(syntax))
    else:
        with subprocess.Popen('; '.join(syntax), shell=True) as proc:
            code = proc.returncode
    sys.exit(code)

