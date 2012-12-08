import logging
import os
import os.path
import sys

from datetime import datetime, date, time, timedelta
from glob import glob
from itertools import groupby, izip
from logging import debug, info, warning, error, critical
import numpy as np
import yaml

from TraceWizard5 import TraceWizard5_File, load_config, volume_t

# Config:
config = load_config("TraceWizard_config.py")
fixture_type_lookup = config.fixture_type_lookup
fixtures = config.AllFixtures
cyclers = config.FirstCycleFixtures
ftypes = set(fixture_type_lookup.values())

def load_dir(data, **kwargs):
	if os.path.isdir(data):
		folder = data
	elif os.path.isfile(data):
		search_folders = os.path.extsep.join((filename,"d")),
	search_folders = filter(os.path.isdir, set(search_folders))
	if search_folders:
		folder = search_folders[0]
	else:
		return None
	
	file_label = os.path.commonprefix(os.listdir(folder))
	if file_label:
		file_label = file_label.rstrip(' _.-[(')
	
	files = glob(os.path.join(folder, "*log_attributes.yaml"))
	with open(files[0]) as fi:
		log_attributes = yaml.load(fi)
	files = glob(os.path.join(folder, "*total_volume_by_hour.npy"))
	total_volume_by_hour = np.load(files[0])
	hod_total_volume = total_volume_by_hour.sum(axis=0)
	#
	files = glob(os.path.join(folder, "*hourly_count_by_fixture.npz"))
	hourly_count_by_fixture = dict(np.load(files[0]).iteritems())
	hod_count_by_fixture = {k:m.sum(axis=0) for k, m in hourly_count_by_fixture.iteritems()}
	#
	files = glob(os.path.join(folder, "*hourly_volume_by_fixture.npz"))
	hourly_volume_by_fixture = dict(np.load(files[0]).iteritems())
	hod_volume_by_fixture = {k:m.sum(axis=0) for k, m in hourly_volume_by_fixture.iteritems()}
	fixture_totals = {k:a.sum() for k, a in hod_volume_by_fixture.iteritems()}
	indoor_fixture_totals = {k:a for k,a in fixture_totals.iteritems() if fixture_type_lookup[k] == 'Indoor'}
	#
	files = glob(os.path.join(folder, "*hourly_volume_by_type.npz"))
	hourly_volume_by_type = dict(np.load(files[0]).iteritems())
	hod_volume_by_type = {k:m.sum(axis=0) for k, m in hourly_volume_by_type.iteritems()}
	indoor_total = hod_volume_by_type['Indoor'].sum()
	leak_total = hod_volume_by_type['Leak'].sum()
	outdoor_total = hod_volume_by_type['Outdoor'].sum()
	#
	indoor_fixture_proportions = {k:a/indoor_total for k,a in indoor_fixture_totals.iteritems()}
	#
	# Loop across days:
	window_size = 3
	windices = window_size - 1
	window_max_by_day = []
	for cl in hourly_volume_by_type['Indoor'].cumsum(axis=1):
		v_be = []
		for eh in range(windices, 24):
			bh = eh-(windices)
			v_be.append( (cl[eh] - cl[bh], (bh, eh)) )
		wmax = max([v for v, (b,e) in v_be])
		v_be = filter(lambda vw: vw[0] >= wmax, v_be)
		if len(v_be) > 1:
			earliest = min([b for v, (b,e) in v_be])
			latest = max([e for v, (b,e) in v_be])
			v_be = (wmax, (earliest, latest))
		window_max_by_day.append(v_be)
	print window_max_by_day

def save_dir(filename, folder = None, **kwargs):
	trace = TraceWizard5_File(filename)
	#
	hour_keyer = lambda ef: ef.StartTime.hour
	fixture_keyer = trace.fixture_keyer
	first_cycle_fixture_keyer = trace.first_cycle_fixture_keyer
	label = trace.label or os.path.split(filename)[-1]
	#filenamer = lambda s: os.path.join(folder,os.path.extsep.join((label,s)) )
	filenamer = lambda s: os.path.join(folder,s)
	#
	if not folder:
		folder = os.path.extsep.join((filename, "d"))
	if not os.path.isdir(folder):
		os.mkdir(folder)
	assert os.path.isdir(folder)
	#with open(filenamer('attributes.yaml'),'w') as fo:
	#	yaml.dump(trace.attributes, fo)
	#with open(filenamer('fixture_profiles.yaml'),'w') as fo:
	#	yaml.dump(trace.fixture_profiles, fo)
	with open(filenamer('log_attributes.yaml'),'w') as fo:
		yaml.dump(trace.log_attributes, fo)
	
	# Initialize:
	begin_date, end_date = trace.get_complete_days()
	days = (end_date-begin_date).days
	hourly_volume_by_fixture = { k:np.zeros((days, 24)) for k in fixtures } # fixture total by hour
	hourly_count_by_fixture = { k:np.zeros((days, 24), dtype=np.int) for k in fixtures }
	total_volume_by_hour = np.zeros((days, 24)) # trace total by hour, over days*24 bins
	
	# Loop 1: day's events
	for d, efs1 in trace.get_events_by_day(logical = True):
		dn = (d-begin_date).days
		# Loop 2: hour's events
		for h, efs2 in groupby(efs1, hour_keyer):
			hl = sorted(list(efs2), key = fixture_keyer)
			daily_total = 0.0
			# Loop 3: fixture's events that hour
			for fixture_name, efs3 in groupby(hl, key = fixture_keyer):
				if fixture_name in cyclers:
					c, s = 0, 0.0
					for e in efs3:
						s += e.Volume
						n, fs = first_cycle_fixture_keyer(e)
						if fs:
							c += 1
				else:
					sa = list(e.Volume for e in efs3)
					hourly_count_by_fixture[fixture_name][dn][h] = len(sa)
					s = sum(sa)
				daily_total += s
				hourly_volume_by_fixture[fixture_name][dn][h] = s
			total_volume_by_hour[dn][h] = daily_total
	
	# Combine fixtures into groups based on their location:
	hourly_volume_by_type = { ft:np.zeros((days, 24)) for ft in ftypes }
	for fixture_name in fixtures:
		try:
			ftype = fixture_type_lookup[fixture_name]
			hourly_volume_by_type[ftype] += hourly_volume_by_fixture[fixture_name]
		except KeyError:
			info("Fixture '%s' not found, ignoring" % fixture_name)
	
	# Save the tables that are hard to generate:
	np.savez(filenamer("hourly_volume_by_type"), **hourly_volume_by_type)
	np.savez(filenamer("hourly_count_by_fixture"), **hourly_count_by_fixture)
	np.savez(filenamer("hourly_volume_by_fixture"), **hourly_volume_by_fixture)
	np.save(filenamer("total_volume_by_hour"), total_volume_by_hour)
	#
if __name__ == '__main__':
	#for fn in sys.argv[1:]:
	#	summarizer(fn)
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	filename = os.path.join(tempdir, '12S704.twdb')
	save_dir(filename)
	load_dir(filename)