
from collections import defaultdict, namedtuple
from logging import debug, info, warning, error, critical
import os.path
import re
import cPickle as pickle

import spssaux

missing_values_none = (0, None, None, None)