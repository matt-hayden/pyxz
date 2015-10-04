#! /usr/bin/env python
import multiprocessing
import subprocess

executable = 'primesieve'
#primesieve_max = (2**64 - 2**32 * 10)
primesieve_max = (1<<64) - (1<<32) * 10
cores = multiprocessing.cpu_count()-1
cmdline = [executable, '-p']
if cores > 1:
	cmdline += [ '-t', str(cores) ]

def primes(start=None, stop=primesieve_max, cmdline=cmdline):
	'''start and stop are OK as strings'''
	if start:
		cmdline += [str(start), str(stop)]
	else:
		cmdline += [str(stop)]
	proc = subprocess.Popen(cmdline,stdout=subprocess.PIPE)
	for line in proc.stdout:
		yield line.rstrip()

#