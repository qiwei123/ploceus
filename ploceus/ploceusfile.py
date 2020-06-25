# -*- coding: utf-8 -*-
import os
import types


def find_ploceusfile():
    for fn in ['Ploceusfile.py', 'ploceusfile.py',
               'Ploceusfile', 'ploceusfile']:
        if not os.path.isfile(fn):
            continue

        ploceusfile_from_pyfile(fn)
        return fn


def ploceusfile_from_pyfile(filename):
    d = types.ModuleType('ploceusfile')
    d.__file__ = filename

    with open(filename) as f:
        exec(compile(f.read(), filename, 'exec'), d.__dict__)
