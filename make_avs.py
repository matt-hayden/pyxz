import os.path
import sys

from jinja2 import Template
# MarkupSafe module is recommended, but escaping is not used here

source = "AviSource" # "DirectShowSource" "DGDecode_mpeg2source"

template = Template(u'''
{% for order, arg in numbered_args -%}
	c{{ order }} = {{ source }}("{{ arg }}")
{% endfor %}
{% for order, arg in numbered_args %}c{{ order }}{% if not loop.last %} ++ {% endif %}{% endfor %}

''')

input_filenames = sys.argv[1:]
if not input_filenames:
	print >>sys.stderr, "No filenames specified"
	sys.exit(-1)
prefix = os.path.commonprefix(input_filenames)
if prefix:
	if prefix.endswith(os.path.sep) or os.path.isdir(prefix):
		input_filenames = [ s.replace(prefix, '', 1).lstrip('/\\') for s in input_filenames ]
		output_filename = os.path.join(prefix, "unknown.avs")
	else:
		output_filename = prefix.rstrip(" +-_.,")+".avs"
else:
	try:
		f = os.path.splitext(input_filenames[0])[0]
		output_filename = f+".avs"
	except:
		output_filename = "unknown.avs"


s=template.stream(source = source,
				  numbered_args = list(enumerate(input_filenames)))
s.dump(output_filename)