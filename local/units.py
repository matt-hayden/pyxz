#!env python

from math import sin, cos, pi, radians

def kelvin_to_celsius(k):
	return k-273.15
def celsius_to_fahrenheit(c):
	return 9*c/5+32
def kelvin_to_fahrenheit(k):
	return celsius_to_fahrenheit(kelvin_to_celsius(k))
def direction_name(angle, unit='degrees'):
	if unit == 'degrees':
		angle = radians(angle)
	angle %= 2*pi
	threshold = 0.975*(pi/8)
	#
	n_to_s, w_to_e = cos(angle), sin(angle)
	if abs(n_to_s) < threshold:
		n_part = ""
	elif (0 < n_to_s):
		n_part = "N"
	else:
		n_part = "S"
	#
	if abs(w_to_e) < threshold:
		w_part = ""
	elif (0 < w_to_e):
		w_part = "W"
	else:
		w_part = "E"
	return n_part+w_part