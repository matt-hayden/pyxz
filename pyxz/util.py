#! /usr/bin/env python3

import subprocess


NPROC = 1 # number of processors
proc = subprocess.run(['nproc'], stdout=subprocess.PIPE)
if (0==proc.returncode):
    NPROC = int(proc.stdout.decode())
else:
    proc = subprocess.run(['parallel', '--number-of-cores'], stdout=subprocess.PIPE)
    if (0==proc.returncode):
        NPROC = int(proc.stdout.decode())
# see also multiprocessing


def safe_index(self, *args):
    try:
        return self.index(*args)
    except ValueError:
        return -1
