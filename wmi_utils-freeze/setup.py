#
import os.path
import sys

from cx_Freeze import setup, Executable

scripts = ["../cal.py", "../wmi_utils.py"]
excludes = ["difflib", "distutils", "doctest", "logging", "optparse", "pdb", "tarfile", "unittest"]

# GUI applications require a different base on Windows (the default is for a
# console application).
base = "Win32GUI" if (sys.platform == "win32") else None

head = Executable(
	script="../wmi_utils.py",
	base=base
	)

setup(
	name = "No Name",
	version = "0.01",
	description = "No description",
	author = "No author",
	executables = [Executable(script=s, base=base) for s in scripts],
	options = { "build_exe": {"excludes": excludes}
			  }
	)
