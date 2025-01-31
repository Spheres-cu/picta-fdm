#!/usr/bin/env python
from __future__ import unicode_literals

# Execute with
# $ python picta_dl/__main__.py (2.6+)
# $ python -m picta_dl          (2.7+)

import os, sys

if not __package__ and not hasattr(sys, 'frozen'):
    # direct call of __main__.py
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))
else:
    # PyInstaller, see https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
    env = dict(os.environ)
    lp_key = 'LD_LIBRARY_PATH'  # for GNU/Linux and *BSD.
    lp_orig = env.get(lp_key + '_ORIG')
    
    if lp_orig is not None:
        env[lp_key] = lp_orig
        os.environ[lp_key] = env[lp_key]
    else:
        env.pop(lp_key, None)

import picta_dl

if __name__ == '__main__':
    picta_dl.main()
