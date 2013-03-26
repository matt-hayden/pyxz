from cx_Freeze import setup, Executable

exe = Executable(
	script="../TraceWizard5/quick_MM4_fixer.py"
	)

setup(
	name = "MeterMaster v4 file fixer",
	version = "0.1",
	description = "",
	executables = [exe],
	options = {
				'build_exe': {
					'includes': ['SelfNamedZipFile']
				}
			  }
	)
