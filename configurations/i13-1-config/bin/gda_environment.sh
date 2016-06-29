#!/bin/sh
export BEAMLINE=i13-1

export GDA_FOLDER=/dls_sw/$BEAMLINE/software/gda
export GDA_VAR=/dls_sw/$BEAMLINE/software/gda_versions/var
export GDA_LOGS=/dls_sw/$BEAMLINE/software/logs
export GDA_MODE=live

export PATH=${GDA_FOLDER}/config/bin:${GDA_FOLDER}/workspace_git/gda-diamond.git/dls-config/bin:${PATH}
