#!/usr/bin/env python

import ConfigParser

from xcollections import Namespace

class IniParser(ConfigParser.SafeConfigParser):
	def contents(self):
		for s in self.sections():
			yield s, Namespace(self.items(section=s))
class CaseSensitiveConfigParser(IniParser):
	optionxform = str