
import csv

DataBeginsKey='DateTimeStamp'
def readCsvHeader(filename):
	with open(filename) as fhi:
		headerMetadata = {}
		ci = csv.reader(fhi, delimiter=',')
		#for row in ci:
		#	print(row)
		headerKey = ""
		while (headerKey != DataBeginsKey):
			headerKey, headerValue = next(ci)
			headerMetadata[headerKey] = headerValue
	return(headerMetadata)
#print(readCsvHeader("12s264.csv"))

if __name__ == '__main__':
	from sys import argv
	if argv:
		print("Filename, Register Volume, MeterMaster Volume, ConvFactor Code")
	for fn in argv[1:]:
		header=readCsvHeader(fn)
		print(", ".join((fn, header['RegVolume'], header['MMVolume'], header['ConvFactor'])))