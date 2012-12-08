#!/bin/head
### Config file for TraceWizard testing

IndoorFixtures = 'Bathtub Clotheswasher Dishwasher Faucet Other Shower Toilet Treatment'.split()
FirstCycleFixtures = 'Clotheswasher Dishwasher'.split()
OutdoorFixtures = 'Cooler Irrigation'.split()
LeakFixtures = 'Leak'.split()

### Below here shouldn't be touched

fixture_type_lookup = {k:'Indoor' for k in IndoorFixtures}
fixture_type_lookup.update({k:'Outdoor' for k in OutdoorFixtures})
fixture_type_lookup.update({k:'Leak' for k in LeakFixtures})

AllFixtures = fixture_type_lookup.keys()
