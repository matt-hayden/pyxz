#! /usr/bin/env python2
import collections
import subprocess

import dateutil.parser
to_timestamp = dateutil.parser.parse


class LastRow(collections.namedtuple('LastRow', 'login, tty, timestamp_part, duration, host')):
	output_format = "{:<8} {:<12} {:<41} {:^20} {}"
	@property
	def begins(self):
		return to_timestamp(self.timestamp_part[0])
	@property
	def ends(self):
		if not self.timestamp_part[-1]:
			return
		t2 = self.timestamp_part[-1].strip()
		if (t2.lower() == 'down'):
			# maybe parse self.duration and add to self.begins
			return
		else:
			return to_timestamp(t2)
class LoginRow(LastRow):
	def get_duration(self):
		if self.ends:
			return self.ends - self.begins
	def __repr__(self):
		ts = "{} - {}".format(self.begins, self.ends or "down")
		dur = self.get_duration()
		if dur:
			ds = '('+str(self.get_duration())+')'
		else:
			ds = ''
		return self.output_format.format(self.login, self.tty, ts, ds, self.host or '0.0.0.0')
class RebootRow(LoginRow):
	pass
class StillLoggedInRow(LastRow):
	@property
	def ends(self):
		return
	def __repr__(self):
		ts = "{}   still logged in".format(self.begins, self.ends or "down")
		return self.output_format.format(self.login, self.tty, ts, '', self.host or '0.0.0.0')


def parse_line(line):
	# expects last -Fai
	pline, source = line.rsplit(None, 1)
	if source == '0.0.0.0':
		source = None
	login, pline = pline[:8].strip(), pline[8:]
	tty, pline = pline[:14].strip(), pline[14:].strip()
	if not pline:
		return LoginRow(login, tty, (None, None), None, source)
	if pline.upper().endswith('STILL LOGGED IN'):
		timestamp_in = pline[:-len('STILL LOGGED IN')].strip()
		return StillLoggedInRow(login, tty, (timestamp_in, None), None, source)
	else:
		timestamp_in, pline = pline.split(' - ')
		timestamp_out, dur = pline.rsplit(None, 1)
		if 'reboot' == login:
			return RebootRow(login, tty, (timestamp_in, timestamp_out), dur, source)
		else:
			return LoginRow(login, tty, (timestamp_in, timestamp_out), dur, source)
def parse_last(lines):
	# consumes lines
	output = {}
	current = output['current'] = []
	history = output['history'] = []
	reboots = output['reboots'] = []
	while not lines[-1].strip():
		lines.pop(-1)
	assert lines
	if lines[-1].startswith('wtmp') or lines[-1].startswith('btmp'):
		timestamp = output['timestamp'] = to_timestamp(lines.pop(-1)[len('_TMP BEGINS '):])
		while not lines[-1].strip():
			lines.pop(-1)
	for line in lines:
		p = parse_line(line)
		if isinstance(p, StillLoggedInRow):
			current.append(p)
		elif isinstance(p, RebootRow):
			reboots.append(p)
		else:
			history.append(p)
	return output


def get_last(*args, **kwargs):
	command = [ 'last', '-Fai' ]
	command = ['ssh', 'tor.valenceo.com']+command
#	if args:
#		logins = args
#	if 'hostname' in kwargs:
#		hostnames = [ kwargs.pop('hostname') ]
#	if 'hostnames' in kwargs:
#		hostnames = kwargs.pop('hostnames')
	proc = subprocess.Popen(command, stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	assert (proc.code == 0)
	return parse_last(out.split('\n'))

def print_last(*args, **kwargs):
	last = get_last(*args, **kwargs) # dict
	ts = last.pop('timestamp')
	for k, v in last.iteritems():
		print
		print k
		for line in v:
			print line
	print
	print ts
if __name__ == '__main__':
	print_last()
