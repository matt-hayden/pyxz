import os.path
import sys

from jinja2 import Template
# MarkupSafe module is recommended, but escaping is not used here

template = Template(u'''
// AviSynth script to merge the following files:
{% for order, arg in numbered_args -%}
	c{{ order }} = {{ source }}({{ arg }})
{% endfor %}
{% for order, arg in numbered_args %}c{{ order }}{% if not loop.last %} ++ {% endif %}{% endfor %}

''')

input_filenames = sys.argv[1:]
if not input_filenames:
	print >>sys.stderr, "No filenames specified"
	sys.exit(-1)
prefix = os.path.commonprefix(input_filenames)
if prefix:
	output_filename = prefix+".avs"
else:
	try:
		f = os.path.splitext(input_filenames[0])[0]
		output_filename = f+".avs"
	except:
		output_filename = "unknown.avs"
source = "AviSource" # "DirectShowSource"

s=template.stream(source = source,
				  numbered_args = list(enumerate(input_filenames)))
s.dump(output_filename)