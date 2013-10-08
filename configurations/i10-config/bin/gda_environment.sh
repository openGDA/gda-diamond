#!/bin/bash
# This script assumes that $BEAMLINE is set (e.g. i02, i18, b16) if not exit...

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

GDA_ROOT=/dls_sw/$BEAMLINE/software/gda
GDA_CONFIG=$GDA_ROOT/workspace_git/gda-mt.git/configurations/$BEAMLINE-config

export GDA_MODE=live
export PATH=$GDA_CONFIG/bin:${PATH}

export GDA_SW=/$SOFTWAREFOLDER/$BEAMLINE/software
export GDA_ROOT=$GDA_SW/gda
export GDA_CONFIG=$GDA_ROOT/${BEAMLINE}-config

export GDA_USERS=/dls/$BEAMLINE

export PATH=/$SOFTWAREFOLDER/$BEAMLINE/software/gda/${BEAMLINE}-config/bin:/$SOFTWAREFOLDER/$BEAMLINE/bin:${PATH}

DESKTOP=$HOME/Desktop
BL_LAUNCHERS=$DESKTOP/${BEAMLINE}_Launchers
DLS_LAUNCHERS=$DESKTOP/DLS_Launchers

LAUNCH_LOG_LOCAL=/dev/null
LAUNCH_LOG_REMOT=/dev/null
#LAUNCH_LOG_LOCAL=$GDA_USERS/var/gda_environment.sh.run.local.`date +%H%M%S`
#LAUNCH_LOG_REMOT=$GDA_USERS/var/gda_environment.sh.run.remote.`date +%H%M%S`

case $DISPLAY in
  :0.0|${BEAMLINE}*:0)
    echo ${BEAMLINE} gda_environment.sh local $DISPLAY  > $LAUNCH_LOG_LOCAL
    (cd $DESKTOP || mkdir $DESKTOP)                    >> $LAUNCH_LOG_LOCAL 2>&1
    echo ls -la $DESKTOP                               >> $LAUNCH_LOG_LOCAL 2>&1
    ls -la $DESKTOP                                    >> $LAUNCH_LOG_LOCAL 2>&1
    rm                             $BL_LAUNCHERS       >> $LAUNCH_LOG_LOCAL 2>&1
    ln -s /scratch/i10_Launchers   $BL_LAUNCHERS       >> $LAUNCH_LOG_LOCAL 2>&1
    rm                             $DLS_LAUNCHERS      >> $LAUNCH_LOG_LOCAL 2>&1
    ln -s /scratch/DLS_Launchers   $DLS_LAUNCHERS      >> $LAUNCH_LOG_LOCAL 2>&1
    ;;
  *)
    :
    echo ${BEAMLINE} gda_environment.sh local $DISPLAY  > $LAUNCH_LOG_REMOT
    (cd $DESKTOP || mkdir $DESKTOP)                    >> $LAUNCH_LOG_REMOT 2>&1
    echo ls -la $DESKTOP                               >> $LAUNCH_LOG_REMOT 2>&1
    ls -la $DESKTOP                                    >> $LAUNCH_LOG_REMOT 2>&1
    rm                             $BL_LAUNCHERS       >> $LAUNCH_LOG_REMOT 2>&1
    ln -s /scratch/i10_Launchers   $BL_LAUNCHERS       >> $LAUNCH_LOG_REMOT 2>&1
    rm                             $DLS_LAUNCHERS      >> $LAUNCH_LOG_REMOT 2>&1
    ln -s /scratch/DLS_Launchers   $DLS_LAUNCHERS      >> $LAUNCH_LOG_REMOT 2>&1
    ;;
esac
