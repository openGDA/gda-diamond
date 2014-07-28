#!/bin/sh
# This script assumes that $BEAMLINE is set (e.g. i02, i18, b16) if not exit...

# **** DO NOT EDIT THIS SCRIPT AS IT MAY BE AUTOMATICALLY OVERWRITTEN *****

if [ ! -n "$BEAMLINE" ]; 
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi
export SOFTWAREFOLDER=dls_sw
export GDA_ROOT=/$SOFTWAREFOLDER/$BEAMLINE/software/gda
export GDA_CONFIG=${GDA_ROOT}/config
export GDA_DATADIR=/dls/$BEAMLINE/data

export PATH=/$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/bin:/$SOFTWAREFOLDER/$BEAMLINE/software/gda/config/pytools/src:/dls_sw/dasc/bin/dicat_scripts:/$SOFTWAREFOLDER/$BEAMLINE/bin:$PATH

