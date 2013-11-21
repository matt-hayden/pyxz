from FileLikeHierarchy import Hierarchy

import yaml

seuss = {'red': 'blue', 1:2}
empty = []

def read_config(path):
	with Hierarchy(path) as h:
		if 'seuss' in h:
			print yaml.load(h.open('seuss'))
		if 'empty' in h:
			print yaml.load(h.open('empty'))
def write_config(path):
	with Hierarchy(path, mode='a') as h:
		h.write_member('seuss', yaml.dump(seuss))
		h.write_member('empty', yaml.dump(empty))

write_config('asdf.zip')
write_config('asdf.d')

read_config('asdf.zip')
read_config('asdf.d')

