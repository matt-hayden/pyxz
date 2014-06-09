#! /usr/bin/env python
from collections import namedtuple
import string

import subprocess

import dateutil.parser

Job = namedtuple('Job', 'jid started queue owner')
queues = '='+string.lowercase+string.uppercase

def get_script(jid, command=['at', '-c']):
	proc = subprocess.Popen(command+[str(jid)], stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	return out.splitlines()
def _get_jobs(command=['at', '-l']):
	proc = subprocess.Popen(command, stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	for line in out.splitlines():
		jid, line = line.split('\t', 1)
		jid = int(jid)
		started = line[:24]
		started = dateutil.parser.parse(started)
		queue = queues.index(line[25])
		owner = line[27:]
		yield Job(jid, started, queue, owner)
def key(job):
	return job.started, job.queue
jobs = sorted(_get_jobs(), key=key)
