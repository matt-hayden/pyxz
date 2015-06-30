#!/usr/bin/env python3
import ipaddress
import subprocess

class dscacheutilException(Exception):
	pass

from .dscacheutil import dscacheutil

__all__ = [ 'dscacheutil' ]
