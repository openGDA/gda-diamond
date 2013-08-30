#!/bin/bash

SELF=$(readlink -f $0)
MT_CONFIGURATIONS=$(readlink -f $(dirname $SELF)/../..)

$MT_CONFIGURATIONS/mt-config/bin/remotestartupscript.sh