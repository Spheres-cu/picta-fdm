#!/usr/bin/env python3
from __future__ import unicode_literals

# Execute with
# $ python3 picta_dl/__main__.py (3.9+)
# $ python3 -m picta_dl          (3.9+)

import sys

if __package__ is None and not getattr(sys, 'frozen', False):
    # direct call of __main__.py
    import os.path
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
