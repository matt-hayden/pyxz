#! /usr/bin/env python2
from collections import namedtuple
import string
import subprocess
import sys

try:
	import dateutil.parser
except ImportError:
	pass

if sys.platform.startswith('win'):
	AT='AT.EXE'
else:
	AT='at'

QUEUES = { v:c for c, v in enumerate('='+string.ascii_lowercase+string.ascii_uppercase) }

class Job(namedtuple('Job', 'jid started queue owner')):
	def get_script(self, command=[AT, '-c'], encoding='UTF-8'):
		# with redirect_stdout...
		proc = subprocess.Popen(command+[str(self.jid)], stdout=subprocess.PIPE)
		out, _ = proc.communicate()
		return out.decode(encoding).splitlines()
	if sys.platform.startswith('linux'):
		@staticmethod
		def from_line(line):
			jid, line = line.split('\t', 1)
			jid = int(jid)
			started = line[:24]
			try:
				started = dateutil.parser.parse(started)
			except:
				started = started
			#queue = QUEUES.index(line[25])
			queue = QUEUES[line[25]]
			owner = line[27:].strip()
			return Job(jid, started, queue, owner)
	elif sys.platform.startwith('darwin'):
		@staticmethod
		def from_line(line):
			jid, line = line.split('\t', 1)
			try:
				started = dateutil.parser.parse(line)
			except:
				started = line.strip()
			return Job(int(jid), started, None, None)
def _get_jobs(command=[AT, '-l'], encoding='UTF-8'):
	# with redirect_stdout...
	proc = subprocess.Popen(command, stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	for line in out.decode(encoding).splitlines():
		yield Job.from_line(line)
#
def print_jobs(jobs=None):
	if not jobs:
		jobs = sorted(_get_jobs(), key=key)
	print("{:^8} {:^24} {:^2} {:<}".format(*'jid started qn owner'.split()) )
	print('='*8, '='*24, '='*2, '='*8)
	for job in jobs:
		print("{:8d} {:>24} {:02d} {:<}".format(*job) )
#
def key(job):
	return job.started, job.queue
jobs = sorted(_get_jobs(), key=key)
#
if __name__ == '__main__':
	print_jobs()
