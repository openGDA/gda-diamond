#!/bin/sh
# This script assumes that $BEAMLINE is set (e.g. i02, i18, b16) if not exit...

# **** DO NOT EDIT THIS SCRIPT AS IT MAY BE AUTOMATICALLY OVERWRITTEN *****

if [ ! -n "$BEAMLINE" ]; 
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi
if [ ! -n "$SOFTWAREFOLDER" ]; 
then
  echo "Please set SOFTWAREFOLDER environment variable."
  exit 1
fi
unset ANT_HOME
unset JAVA_HOME
unset JYTHON_HOME
unset SVN_HOME

source /$SOFTWAREFOLDER/$BEAMLINE/software/gda/builder/set_tools.sh  > ~/.dasc_sw_setup.log

export PATH=/$SOFTWAREFOLDER/$BEAMLINE/software/gda/bin:/$SOFTWAREFOLDER/$BEAMLINE/software/gda/$BEAMLINE-config/bin:/$SOFTWAREFOLDER/$BEAMLINE/bin:${PATH}
