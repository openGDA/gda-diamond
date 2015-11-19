#!/bin/sh
export BEAMLINE=i13
export GDAFOLDER=/dls_sw/$BEAMLINE/software/gda
export GDAVAR=/dls_sw/$BEAMLINE/software/gda_versions/var
export GDALOGS=/dls_sw/$BEAMLINE/software/logs
export GDAMODE=live
export GDA_MODE=live

export PATH=${GDAFOLDER}/config/bin:${GDAFOLDER}/workspace_git/gda-diamond.git/dls-config/bin:${PATH}

