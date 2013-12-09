#! /usr/bin/env
"""mkodc - create an Excel ODC for an Access database

Usage:
    mkodc.py [options] [--] <filename> <table>...

Options:
    -l, --local     Put files in current directory rather than the same
                    directory as database
"""
from datetime import datetime
import os
import os.path
import string

import local.sanitize

template_file = 'ODC.template'

#
def get_odc(**params):
    with open(template_file) as fi:
        t = string.Template(fi.read())
    return t.substitute(params)
#
def make_odc(datasource, odc_filename, **kwargs):
    options = { 'Now': datetime.now(),
                'DataSource': os.path.abspath(datasource) }
    table = kwargs.pop('table', '')
    if table:
        options['CommandType'] = 'Table'
        options['CommandText'] = table
    name = kwargs.pop('name', '')
    if not name:
        dirname, basename = os.path.split(datasource)
        name, ext = os.path.splitext(basename)
    options['Name'] = name
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