from cx_Freeze import setup, Executable

exe = Executable(
	script="../TraceWizard5/quick_MM4_fixer.py"
	)

setup(
	name = "MeterMaster v4 file fixer",
	version = "0.1",
	description = "Process bugs out of MeterMaster v4 CSV and ZIP files",
	author = "Aquacraft Inc.",
	author_email = "matt@aquacraft.com",
	executables = [exe],
	options = {
				'build_exe': {
					'includes': ['SelfNamedZipFile'],
					'excludes': ['calendar', 'difflib', 'distutils', 'doctest',
								 'inspect', 'locale', 'optparse', 'pdb', 
								 'pickle', 'random', 'tarfile', 'threading', 
								 'unittest']
				}
			  }
	)
