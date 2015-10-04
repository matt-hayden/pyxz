from cx_Freeze import setup, Executable

### multiprocessing requires:
#	pickle
#	random
#	re
#	socket
#	threading
#	tempfile
###
net_excludes = 'email ftplib httplib _ssl ssl urllib xml xmllib xmlrpclib'.split()
dev_excludes = 'ctypes difflib distutils doctest inspect locale pdb unittest'.split()
other_excludes = 'calendar tarfile zipfile'.split()

exe = Executable(
	script="../_stub.py" # hopefully, you've renamed this
	)

setup(
	name = "",
	version = "0.0",
	description = "",
	author = "",
	author_email = "",
	executables = [exe],
	options = {
				'build_exe': {
					'includes': [],
					'excludes': net_excludes+dev_excludes+other_excludes
				}
			  }
	)
