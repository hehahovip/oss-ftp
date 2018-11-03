#!/bin/bash
# export LC_ALL=en_US.UTF-8; export LANG="en_US.UTF-8"; locale
SCRIPTPATH=`dirname "${BASH_SOURCE[0]}"`
cd $SCRIPTPATH

if hash python2 2>/dev/null; then
    python2 launcher/start.py
else
    python launcher/start.py
fi
