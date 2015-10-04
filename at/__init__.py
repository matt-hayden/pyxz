from collections import namedtuple
import string
import subprocess
import sys

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if __debug__ else logging.WARNING)
debug, info, warning, error, panic = logger.debug, logger.info, logger.warning, logger.error, logger.critical
__all__ = 'debug info warning error panic'.split()

try:
	import dateutil.parser
except ImportError:
	info("dateutil not imported")

if sys.platform.startswith('win'):
	AT='AT.EXE'
	BATCH='BATCH.EXE'
else:
	AT='at'
	BATCH='batch'
__all__ += ['AT', 'BATCH']

QUEUES = '='+string.ascii_lowercase+string.ascii_uppercase

class Job(namedtuple('Job', 'jid begins queue owner')):
	def get_script(self, command=[AT, '-c'], encoding='UTF-8'):
		# with redirect_stdout...
		proc = subprocess.Popen(command+[str(self.jid)], stdout=subprocess.PIPE)
		out, _ = proc.communicate()
		return out.decode(encoding).splitlines()
	if sys.platform.startswith('linux'):
		@staticmethod
		def from_line(line):
			jid, line = line.split('\t', 1)
			begins = line[:24]
			try:
				begins = dateutil.parser.parse(begins)
			except:
				debug("{} left as string".format(begins))
			queue = QUEUES.index(line[25])
			owner = line[27:].strip()
			return Job(int(jid), begins, queue, owner)
	elif sys.platform.startwith('darwin'):
		@staticmethod
		def from_line(line):
			jid, line = line.split('\t', 1)
			try:
				begins = dateutil.parser.parse(line)
			except:
				debug("{} left as string".format(begins))
				begins = line.strip()
			return Job(int(jid), begins, None, None)
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
	print("{:^8} {:^24} {:^2} {:<}".format(*'jid begins qn owner'.split()) )
	print('='*8, '='*24, '='*2, '='*8)
	for job in jobs:
		print("{:8d} {:>24} {:02d} {:<}".format(*job) )
#
def key(job):
	return job.begins, job.queue
jobs = sorted(_get_jobs(), key=key)
#
__all__ += [ 'jobs', 'print_jobs' ]

from .tools import atgrep
from .shtools import batch, submit

__all__ += [ 'atgrep', 'batch', 'submit' ]

