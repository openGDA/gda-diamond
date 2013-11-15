# No Shebang since this will always be sourced.

# This file is sourced from /dls_sw/$BEAMLINE/etc/$BEAMLINE_profile.sh
# which is sourced from /etc/profile.d/gda_environment.sh

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

GDA_ROOT=/dls_sw/$BEAMLINE/software/gda
GDA_CONFIG=$GDA_ROOT/workspace_git/gda-mt.git/configurations/$BEAMLINE-config
MT_CONFIG=$GDA_ROOT/workspace_git/gda-mt.git/configurations/mt-config

export PATH=$GDA_CONFIG/bin:$MT_CONFIG/bin:/dls_sw/$BEAMLINE/bin:${PATH}
export GDA_MODE=live

DESKTOP=$HOME/Desktop
LAUNCH_LOG_LOCAL=/dev/null
LAUNCH_LOG_REMOT=/dev/null
#LAUNCH_LOG_LOCAL=$GDA_USERS/var/gda_environment.sh.run.local.`date +%H%M%S`
#LAUNCH_LOG_REMOT=$GDA_USERS/var/gda_environment.sh.run.remote.`date +%H%M%S`

case $DISPLAY in 
  :0.0|${BEAMLINE}*:0)
    echo i15 gda_environment.sh local $DISPLAY           > $LAUNCH_LOG_LOCAL
    (cd $DESKTOP || mkdir $DESKTOP)                     >> $LAUNCH_LOG_LOCAL 2>&1
    echo ls -la $DESKTOP                                >> $LAUNCH_LOG_LOCAL 2>&1
    ls -la $DESKTOP                                     >> $LAUNCH_LOG_LOCAL 2>&1
    rm                           $DESKTOP/i15_Launchers >> $LAUNCH_LOG_LOCAL 2>&1
    ln -s /scratch/i15_Launchers $DESKTOP/i15_Launchers >> $LAUNCH_LOG_LOCAL 2>&1
    rm                           $DESKTOP/DLS_Launchers >> $LAUNCH_LOG_LOCAL 2>&1
    ln -s /scratch/DLS_Launchers $DESKTOP/DLS_Launchers >> $LAUNCH_LOG_LOCAL 2>&1
    ;;
  *)
    :
    echo i15 gda_environment.sh local $DISPLAY           > $LAUNCH_LOG_REMOT
    (cd $DESKTOP || mkdir $DESKTOP)                     >> $LAUNCH_LOG_REMOT 2>&1
    echo ls -la $DESKTOP                                >> $LAUNCH_LOG_REMOT 2>&1
    ls -la $DESKTOP                                     >> $LAUNCH_LOG_REMOT 2>&1
    rm                           $DESKTOP/i15_Launchers >> $LAUNCH_LOG_REMOT 2>&1
    ln -s /scratch/i15_Launchers $DESKTOP/i15_Launchers >> $LAUNCH_LOG_REMOT 2>&1
    rm                           $DESKTOP/DLS_Launchers >> $LAUNCH_LOG_REMOT 2>&1
    ln -s /scratch/DLS_Launchers $DESKTOP/DLS_Launchers >> $LAUNCH_LOG_REMOT 2>&1
    ;;
esac
