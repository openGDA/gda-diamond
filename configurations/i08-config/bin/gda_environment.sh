#!/bin/sh
# This script assumes that $BEAMLINE is set (e.g. i02, i08, b16) if not exit...

if [ ! -n "$BEAMLINE" ];
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi
# echo Beamline Name: $BEAMLINE


module load java/gda830

export DASC_SOFTWARE=/dls_sw/$BEAMLINE/software
export GDA_CORE=$DASC_SOFTWARE/gda_git/gda-core.git/uk.ac.gda.core
export GDA_LIBRARY_SUBDIR=`uname`-`uname -i`

export LD_LIBRARY_PATH=$GDA_CORE/lib/$GDA_LIBRARY_SUBDIR:$DASC_SOFTWARE/gda/client/plugins/uk.ac.gda.nexus_1.0.0/lib/$GDA_LIBRARY_SUBDIR:/dls_sw/dasc/jprofiler5/bin/linux-x64:${LD_LIBRARY_PATH}
export PATH=$DASC_SOFTWARE/gda/bin:/dls_sw/$BEAMLINE/bin:${PATH}
