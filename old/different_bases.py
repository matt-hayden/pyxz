###
import string

def str_base(i, symbols=string.digits+' '):
	base = len(symbols)
	backwards = ''
	while i:
		i, place = divmod(i, base)
		backwards += symbols[place]
	return backwards[::-1]
