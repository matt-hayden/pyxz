"""
This is a config file driver for TraceWizard file processing. It works with an
accompanying .INI file (it simply looks for analysis.ini). This script will not
likely need any adjustment; the .INI file offers more flexibility.

It is read by the load_config facility, which is part of the TraceWizard
module.
"""
from collections import defaultdict

from CaseSensitiveConfigParser import CaseSensitiveConfigParser

config = CaseSensitiveConfigParser()
# substitute your favorite config file name here:
with open('analysis.ini') as fi:
	config.readfp(fi)
assert config is not None

# tags_by_fixture['Dishwasher'] should give a list of tags for that fixture
tags_by_fixture = {k:v.split(",") for k, v in config.items('VirtualFixture tags')}

# fixtures_by_tag['Indoor'] should give a list of fixture names
# note that set() objects are not preserved ConfigObj
fixtures_by_tag = defaultdict(set) 

if tags_by_fixture:
	for vf, tl in tags_by_fixture.iteritems():
		for t in tl:
			fixtures_by_tag[t].add(vf)
virtualfixture_lookup = {vf: vf for vf in tags_by_fixture.keys()}
virtualfixture_lookup.update(config.items('Fixture switchboard'))

window_size = config.getint('Hourly statistics', 'Window hours')

# EOF
