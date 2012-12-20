from collections import defaultdict

from CaseSensitiveConfigParser import CaseSensitiveConfigParser

config = CaseSensitiveConfigParser()
with open('foo.ini') as fi:
	config.readfp(fi)

#
tags_by_fixture = {k:v.split(",") for k, v in config.items('VirtualFixture tags')}
fixtures_by_tag = defaultdict(set) # note that set() objects are not preserved ConfigObj
if tags_by_fixture:
	for vf, tl in tags_by_fixture.iteritems():
		for t in tl:
			fixtures_by_tag[t].add(vf)
virtualfixture_lookup = {vf: vf for vf in tags_by_fixture.keys()}
virtualfixture_lookup.update(config.items('Fixture switchboard'))
#
window_size = config.getint('Hourly statistics', 'WindowHours')

from pprint import pprint
pprint(tags_by_fixture)
pprint({k:list(v) for k, v in fixtures_by_tag.iteritems()})
pprint(virtualfixture_lookup)

"""
fixture_type_lookup = fixtures_by_tag
# AllFixtures is a list of fixture names 
AllFixtures = fixture_type_lookup.keys()
"""