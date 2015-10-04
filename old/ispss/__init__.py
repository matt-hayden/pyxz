__all__ = ['spssterm', 'get_cwd']

import os

import spssaux

from local.console import redirect_terminal

from _common import *

spssterm = "."

def get_cwd():
	with redirect_terminal(stdout=os.devnull):
		return spssaux.getShow('DIRECTORY')