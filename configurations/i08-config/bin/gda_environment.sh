#!/bin/sh
export BEAMLINE=i08
export GDAFOLDER=/dls_sw/$BEAMLINE/software/gda
export GDAVAR=/dls_sw/$BEAMLINE/software/gda_versions/var
export GDALOGS=/dls_sw/$BEAMLINE/logs
export GDAMODE=live

export PATH=$GDAFOLDER/bin:/dls_sw/$BEAMLINE/software/gda_git/gda-diamond.git/dls-config/bin:${PATH}
