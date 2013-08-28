import string

def calculate_per_capita(numerators, denominator, suffix='GPCD'):
	template = string.Template('''
if ($denominator > 0) ${numerator}${suffix}=${numerator}/$denominator.
''')
	syntax = [ template.substitute(locals()) for numerator in numerators ]
	return syntax+['execute.']

def save_residuals(independent_variables, dependent_variable):
	if not isinstance(independent_variables, basestring):
		independent_variables = ' '.join(independent_variables)
	template = string.Template('''
REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT $dependent_variable
  /METHOD=ENTER $independent_variables
  /SAVE RESID (${dependent_variable}Resid).
variable labels ${dependent_variable}Resid '$dependent_variable Unstandardized Residual'.
''')
	return template.substitute(locals())
###
if __name__ == '__main__':
	dvs = '''TraceindoorDaily TraceOutdoorDaily
BathtubDaily ClothesWasherDailyVolume DishwasherDaily FaucetDaily LeakDaily OtherDaily 
ShowerDailyVolume ToiletDailyVolume ClothesWasherUseVolume ClothesWasherDailyUses ShowerUseVolume 
ShowerMode ShowerDailyUses ShowerDailyMinutes'''.split()
	idvs = ['Residents']
	
	for idv in idvs:
		print '\n'.join(calculate_per_capita(dvs, idv, 'LPCD'))
	
	for dv in dvs:
		print save_residuals(idvs, dv)