import csv
import os
import os.path
import sys
#from winshell import delete_file

sep='\t'
filename='labels.tab'
ignore_filenames = [filename,]
ignore_filenames = [f.upper() for f in ignore_filenames]

for arg in sys.argv[1:]:
	print "Processing", arg
	if not os.path.isdir(arg):
		continue
	table_filename = os.path.join(arg,filename)
	if os.path.exists(table_filename) and (os.path.getsize(table_filename)>0):
		print "Not overwriting", table_filename
		continue
	with open(table_filename,'wb') as fo:
		wo = csv.writer(fo, dialect='excel-tab')
		for r, ds, fs in os.walk(arg):
			if fs:
				label = r.split(os.path.sep)[1:]
				if label:
					#label.reverse()
					for f in fs:
						if f.upper() not in ignore_filenames:
							wo.writerow([f,
										 os.path.getsize(os.path.join(r,f))]+label)
	if (os.path.getsize(table_filename) == 0):
		os.remove(table_filename)