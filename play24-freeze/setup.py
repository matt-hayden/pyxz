# Commands to repeat:
# schtasks /create /tn "Agent Jack Bauer" /tr "%ProgramFiles%\Agent Jack Bauer\play24.exe" /sc HOURLY 
# schtasks /create /tn "Agent Jack Bauer" /tr "%ProgramFiles%\Agent Jack Bauer\play24.exe" /sc ONLOGON
#
import os.path
import sys

from cx_Freeze import setup, Executable

# GUI applications require a different base on Windows (the default is for a
# console application).
base = "Win32GUI" if (sys.platform == "win32") else None

soundsdirectory='sounds/24'
soundfiles=[ os.path.join(soundsdirectory, "%d.mp3") % x for x in range(23) ]

exe = Executable(
	script="../play24.pyw",
	base=base
	)

setup(
	name = "Agent Jack Bauer",
	version = "0.24",
	description = "Never miss an hour",
	executables = [exe],
	options = {
				'build_exe': {
					'include_files': soundfiles
				}
			  }
	)
