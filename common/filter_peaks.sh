#!/bin/sh

KEEP='[RKP][0-9]*CG|I[0-9]*CG1'


help="""\
small script for filtering only relevant peaks
edit the \$KEEP variable to select your peaks
    separate different peak groups by |
run it on Sparky list provided as argument

usage: $0 peaklist.list > peaklist_filtered.list
"""

if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]
then
    printf "%s" "$help"
    exit 0
fi

awk -v keep="$KEEP" '$0 ~ keep' $1
