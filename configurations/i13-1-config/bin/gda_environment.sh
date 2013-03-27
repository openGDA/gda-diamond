#!/bin/sh
# This script assumes that $BEAMLINE is set (e.g. i02, i18, b16) if not exit...

# **** DO NOT EDIT THIS SCRIPT AS IT MAY BE AUTOMATICALLY OVERWRITTEN *****

if [ ! -n "$BEAMLINE" ]; 
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi
if [ ! -n "$GDAFOLDER" ]; 
then
  echo "Please set GDAFOLDER environment variable."
  exit 1
fi
GDA_CLIENT=${GDAFOLDER}/client/gda-i13j; export GDA_CLIENT

export PATH=${GDAFOLDER}/config/bin:${GDAFOLDER}/workspace_git/gda-diamond.git/dls-config/bin:${PATH}

