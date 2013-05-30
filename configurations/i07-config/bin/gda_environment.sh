#!/bin/sh
# This script assumes that $BEAMLINE is set (e.g. i07, i18, b16) if not exit...

# **** DO NOT EDIT THIS SCRIPT AS IT MAY BE AUTOMATICALLY OVERWRITTEN *****

if [ ! -n "$BEAMLINE" ];
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi

# echo Beamline Name: $BEAMLINE

## Getting access to the tools used by DASC
#if [ -f /dls_sw/dasc/tools_versions/set_tools.sh ];
#then
#	OLDDIR=`pwd`
#	cd /dls_sw/dasc/tools_versions
##	source set_tools.sh > ~/.set_tools_report.txt
#	module load java/gda826
#	cd $OLDDIR
#fi

module load java/gda830

export DASC_SOFTWARE=/dls_sw/$BEAMLINE/software

#export GDA_CORE=$DASC_SOFTWARE/gda/plugins/uk.ac.gda.core
export GDA_CORE=$DASC_SOFTWARE/gda_git/gda-core.git/uk.ac.gda.core

export NEXUS=$DASC_SOFTWARE/gda/plugins/uk.ac.gda.nexus

export GDA_LIBRARY_SUBDIR=`uname`-`uname -i`

export LD_LIBRARY_PATH=$GDA_CORE/lib/$GDA_LIBRARY_SUBDIR:$NEXUS/lib/$GDA_LIBRARY_SUBDIR:${LD_LIBRARY_PATH}

export PATH=$DASC_SOFTWARE/gda/bin:/dls/$BEAMLINE/bin:${PATH}
