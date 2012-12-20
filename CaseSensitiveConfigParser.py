import ConfigParser

class CaseSensitiveConfigParser(ConfigParser.ConfigParser):
	optionxform = str