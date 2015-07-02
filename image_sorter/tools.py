#!/usr/bin/env python3
from io import BytesIO
import subprocess

def grayscale(*args):
	proc = subprocess.Popen(['jpegtran', '-copy', 'none', '-grayscale']+list(args), stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	return BytesIO(out)
