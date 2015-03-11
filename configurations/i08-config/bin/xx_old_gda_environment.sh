#!/bin/sh
Rubbish
export BEAMLINE=i08
export GDAFOLDER=/dls_sw/$BEAMLINE/software
export GDAVAR=/dls_sw/$BEAMLINE/software/gda_versions/var
export GDALOGS=/dls_sw/$BEAMLINE/logs
export GDAMODE=live

export PATH=${GDAFOLDER}/gda/config/bin:${GDAFOLDER}/gda/workspace_git/gda-diamond.git/dls-config/bin:${PATH}
