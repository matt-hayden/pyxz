#! /usr/bin/env python
"""mkodc - create an Excel ODC for an Access database

Usage:
    mkodc.py [options] [--] <filename> <table>...

Options:
    -l, --local     Put files in current directory rather than the same
                    directory as database

This script will run on platforms other than Windows, but the paths must be
valid Windows absolute path names. This is ensured by running it on a Windows
machine.
"""
from datetime import datetime
import os
import os.path
import string

import local.sanitize

connection_string_template_file = 'ConnectionString.template'
odc_template_file = 'ODC.template'
#
def get_odc(**params):
    """Form the content of a MS Office ODC file, which is an XML wrapper around
    a usual connection string.
    """
    with open(connection_string_template_file) as fi:
        t = string.Template(fi.read())
    params['ConnectionString'] = t.substitute(params)
    with open(odc_template_file) as fi:
        t = string.Template(fi.read())
    return t.substitute(params)
#
def make_odc(datasource, odc_filename, **kwargs):
    """Create a MS Office ODC file
    """
    options = { 'Now': datetime.now(),
                'PWD': os.path.abspath(os.curdir),
                'DataSource': os.path.abspath(datasource) }
    """Table is used for both tables and views (queries).
    """
    table = kwargs.pop('table', '')
    if table:
        options['CommandType'] = 'Table'
        options['CommandText'] = table
    else:
        raise NotImplementedError("Command for {} not understood".format(datasource))
    dirname, basename = os.path.split(datasource)
    name, ext = os.path.splitext(basename)
    name, ext = kwargs.pop('name', name), ext.upper()
    options['Name'] = name
    if ext in ('.MDB'):
        options['Jet_Engine_Type'] = 5
    elif ext in ('.ACCDB'):
        options['Jet_Engine_Type'] = 6
    else:
        raise NotImplementedError("Jet type for {} not understood".format(datasource))
    options.update(kwargs)
    #
    src_st = os.stat(datasource)
    try:
        dest_st = os.stat(odc_filename)
        raise IOError()
    except:
        dest_st = ()
    with open(odc_filename, 'w') as fo:
        fo.write(get_odc(**options))
    return odc_filename
#
if __name__ == '__main__':
    import docopt
    args = docopt.docopt(__doc__)
    
    ifn = args['<filename>']
    dirname, basename = os.path.split(ifn)
    name, ext = os.path.splitext(basename if args['--local'] else ifn)
    for tn in args['<table>']:
        ofn = local.sanitize.path_sanitize(name)
        ofn += '_'+local.sanitize.path_sanitize(tn)
        make_odc(ifn, ofn+'.ODC', table=tn)