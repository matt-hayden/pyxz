import os.path

valid_characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-._'

def path_sanitize(arg, sep='_', valid_characters=valid_characters):
	if os.path.isdir(arg):
		return arg
	dirname, basename = os.path.split(arg)
	basename = ''.join(c if c in valid_characters else sep for c in basename)
	if dirname:
		return os.path.join(dirname, basename)
	else:
		return basename