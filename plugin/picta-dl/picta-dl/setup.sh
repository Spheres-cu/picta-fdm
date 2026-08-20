#!/bin/bash
# Setup for PyInstaller ManyLinux 2.28 Docker Action
# https://github.com/oleksis/pyinstaller-manylinux

# Fail on errors.
set -e

# SSL: CERTIFICATE
pyenv exec pip install -r requirements/requirements.txt
