#!env python
from collections import defaultdict
from itertools import groupby

indoor_outdoor_by_fixture = defaultdict(lambda:'')
indoor_outdoor_by_fixture['Bathtub']		=	'Indoor'
indoor_outdoor_by_fixture['Clothes washer']	=	'Indoor'
indoor_outdoor_by_fixture['Clotheswasher']	=	'Indoor'
indoor_outdoor_by_fixture['Cooler']			=	'Indoor'
indoor_outdoor_by_fixture['Dishwasher']		=	'Indoor'
indoor_outdoor_by_fixture['Faucet']			=	'Indoor'
indoor_outdoor_by_fixture['Leak']			=	'Indoor'
indoor_outdoor_by_fixture['Other']			=	'Indoor'
indoor_outdoor_by_fixture['Shower']			=	'Indoor'
indoor_outdoor_by_fixture['Toilet']			=	'Indoor'
indoor_outdoor_by_fixture['Treatment']		=	'Indoor'
indoor_outdoor_by_fixture['Irrigation']		=	'Outdoor'
indoor_outdoor_by_fixture['Pool']			=	'Outdoor'

def split_events_by_indoor_outdoor(events):
	indooroutdoor_key = lambda row: indoor_outdoor_by_fixture[row.Fixture]
	events = sorted(events, key=indooroutdoor_key)
	events_by_category = {category:list(events) for category, events in groupby(events, key=indooroutdoor_key)}
	indoors		=	events_by_category.pop('Indoor', [])
	outdoors	=	events_by_category.pop('Outdoor', [])
	unspecified	=	events_by_category.pop('', [])
	if events_by_category:
		error("split_events_by_indoor_outdoor() produced {} extra categories. These events are ignored!".len(events_by_category))
	return indoors, outdoors, unspecified