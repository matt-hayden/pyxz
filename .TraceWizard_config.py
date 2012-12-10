#!/bin/head
### Config file for TraceWizard testing

# IndoorFixutures is a list of fixture names that are included in Indoor totals:
IndoorFixtures = 'Bathtub Clotheswasher Dishwasher Faucet Other Shower Toilet Treatment'.split()

# FirstCycleFixtures is a list of fixture names for which the FirstCycle flag is respected:
FirstCycleFixtures = 'Clotheswasher Dishwasher'.split()

# OutdoorFixtures is a list of fixture names that are included in Outdoor totals:
OutdoorFixtures = 'Cooler Irrigation'.split()

# LeakFixtures is a special case when leaks are not considered Indoor or Outdoor:
LeakFixtures = 'Leak'.split()

# Number of hours for a sliding average
window_size = 3

### Below here shouldn't be touched ###

fixture_type_lookup = {k:'Indoor' for k in IndoorFixtures}
fixture_type_lookup.update({k:'Outdoor' for k in OutdoorFixtures})
fixture_type_lookup.update({k:'Leak' for k in LeakFixtures})

# AllFixtures is a list of fixture names 
AllFixtures = fixture_type_lookup.keys()
