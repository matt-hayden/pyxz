#! env python
import datetime
from math import floor
import os.path
import sys

commands = 'blkid df free mount swaps uptime'.split()

try:
	import wmi
except:
	print >>sys.stderr, "Error: WMI module not installed"
	print >>sys.stderr, "pip install WMI"
	sys.exit(-1)
#
# Unused:?
DriveType_desc = {	0: "Unknown",
					1: "No Root Directory",
					2: "Removable Disk",
					3: "Local Disk",
					4: "Network Drive",
					5: "Compact Disc",
					6: "RAM Disk" }
#
class wmi_utils_Error(Exception):
	pass
def wmi_show_mounts(*args, **kwargs):
	c = wmi.WMI(kwargs.pop('machine', None) )
	print >> sys.stderr,  "Warning: logical partitions within a MSDOS extended partition appear to share DeviceID"
	for pl in c.Win32_LogicalDiskToPartition():
		Antecedent, Dependent = pl.Antecedent, pl.Dependent
		flags = []
		if Antecedent.BootPartition:
			flags += "boot",
		if Dependent.Compressed:
			flags += "compressed",
		if Antecedent.PrimaryPartition:
			flags += "primary",
		if Dependent.SupportsDiskQuotas and not Dependent.QuotasDisabled:
			flags += "quota",
		label = Dependent.VolumeName
		print Antecedent.DeviceID, "["+label+"]" if label else "", "on", Dependent.DeviceID, "type", Dependent.FileSystem, "("+" ".join(flags)+")"
def wmi_swaps(*args, **kwargs):
	c = wmi.WMI(kwargs.pop('machine', None) )
	pfu = c.Win32_PageFileUsage()
	for inst in pfu:
		print inst.AllocatedBaseSize, inst.CurrentUsage, inst.Name
def wmi_blkid(*args, **kwargs):
	c = wmi.WMI(kwargs.pop('machine', None) )
	print >> sys.stderr,  "Warning: logical partitions within a MSDOS extended partition appear to share DeviceID"
	for pl in c.Win32_LogicalDiskToPartition():
		Antecedent, Dependent = pl.Antecedent, pl.Dependent
		label = Dependent.VolumeName
		print Antecedent.DeviceID, "["+label+"]" if label else "",":","Serial="+Dependent.VolumeSerialNumber if Dependent.VolumeSerialNumber else "", "Type="+Dependent.FileSystem if Dependent.FileSystem else ""
def wmi_df(*args, **kwargs):
	block_divisor = kwargs.pop('block_divisor', 1024L)
	c = wmi.WMI(kwargs.pop('machine', None) )
	print >> sys.stderr, "Warning: logical partitions within a MSDOS extended partition appear to share DeviceID"
	print "Filesystem".ljust(40), \
		   "blocks".rjust(11), \
		   "Used".rjust(11), \
		   "Available".rjust(11), \
		   "Capacity".rjust(8), \
		   "Mounted on".ljust(10)
	for pl in c.Win32_LogicalDiskToPartition():
		Antecedent, Dependent = pl.Antecedent, pl.Dependent
		# part_size = float(Antecedent.Size)/block_divisor # reports size of extended partition
		fs_size, avail = float(Dependent.Size or 0)/block_divisor, float(Dependent.FreeSpace or 0)/block_divisor
		used = fs_size - avail
		capacity = 100.0*used/fs_size if fs_size else 100
		label = Dependent.VolumeName
		name = Antecedent.DeviceID + " ["+label+"]" if label else "(unknown)"
		print  name.ljust(40), \
			  ("%d" % fs_size).rjust(11), \
			  ("%d" % used).rjust(11), \
			  ("%d" % avail).rjust(11), \
			  ("%d%%" % capacity).rjust(8), \
			  Dependent.DeviceID.ljust(10)
#
def wmi_free(*args, **kwargs):
	width=12
	c = wmi.WMI(kwargs.pop('machine', None) )
	for inst in c.Win32_OperatingSystem():
		if inst.Primary:
			os = inst
			break
	print "".ljust(width), \
	      "total".rjust(width), \
	      "used".rjust(width), \
		  "free".rjust(width)
	
	mtotal, mfree = int(os.TotalVisibleMemorySize), int(os.FreePhysicalMemory)
	mused = mtotal-mfree
	print "Mem".ljust(width), \
	      str(mtotal).rjust(width), \
		  str(mused).rjust(width), \
		  str(mfree).rjust(width)
	stotal, sfree = int(os.SizeStoredInPagingFiles), int(os.FreeSpaceInPagingFiles)
	sused = stotal-sfree
	print "Swap".ljust(width), \
	      str(stotal).rjust(width), \
		  str(sused).rjust(width), \
		  str(sfree).rjust(width)
def wmi_uptime(*args, **kwargs):
	c = wmi.WMI(kwargs.pop('machine', None) )
	perf = c.Win32_PerfFormattedData_PerfOS_System()
	uptime = perf[-1].SystemUpTime
	print datetime.timedelta(seconds=int(uptime))
#
if __name__ == '__main__':
	def print_shell_aliases(boxer, shell = "bash"):
		if shell.title() in ['Bash', 'Bourne']:
			for c in commands:
				print """alias {0}='{1} {0}'""".format(c, boxer)
	def command_switchboard(command_name, args = () ):
		if command_name == 'wmi_utils' or command_name is None:
			if args:
				command_switchboard(args[0], args[1:])
			else:
				raise wmi_utils_Error("{}: command not found".format(command_name) )
		elif command_name == 'blkid':
			wmi_blkid()
		elif command_name == 'df':
			wmi_df()
		elif command_name == 'free':
			wmi_free()
		elif command_name == 'mount':
			wmi_show_mounts()
		elif command_name == 'swaps':
			wmi_swaps()
		elif command_name == 'uptime':
			wmi_uptime()
		elif command_name in commands:
			raise wmi_utils_Error("Internal error: {}: command not found".format(command_name) )
	#
	called_dirname, called_basename = os.path.split(sys.argv[0])
	called_filepart, script_extension = os.path.splitext(called_basename)
	try:
		args = sys.argv[1:]
	except IndexError:
		args = ()
	if args:
		command_switchboard(called_filepart, args)
	else:
		print_shell_aliases("python -m {}".format(called_filepart) )