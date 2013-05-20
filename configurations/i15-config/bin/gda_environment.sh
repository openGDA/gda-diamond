if [ ! -n "$BEAMLINE" ]; 
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi

export GDA_SW=/dls_sw/$BEAMLINE/software
export GDA_ROOT=$GDA_SW/gda
export GDA_CONFIG=$GDA_ROOT/config

export GDA_USERS=/dls/$BEAMLINE
export JAVA_HOME=/dls/$BEAMLINE/software/java/jre
export JYTHON_HOME=/dls/$BEAMLINE/software/jython

export CLASSPATH=$GDA_ROOT/src:$GDA_ROOT/jars/*:$JYTHON_HOME/jython.jar:${CLASSPATH}
export PATH=$JAVA_HOME/bin:$GDA_CONFIG/bin:$GDA_ROOT/lib:$JYTHON_HOME:/dls/$BEAMLINE/bin:${PATH}

DESKTOP=$HOME/Desktop
LAUNCH_LOG_LOCAL=/dev/null
LAUNCH_LOG_REMOT=/dev/null
#LAUNCH_LOG_LOCAL=$GDA_USERS/var/gda_environment.sh.run.local.`date +%H%M%S`
#LAUNCH_LOG_REMOT=$GDA_USERS/var/gda_environment.sh.run.remote.`date +%H%M%S`

case $DISPLAY in 
  :0.0|${BEAMLINE}*:0)
    echo i15 gda_environment.sh local $DISPLAY          > $LAUNCH_LOG_LOCAL
    (cd $DESKTOP || mkdir $DESKTOP)                    >> $LAUNCH_LOG_LOCAL 2>&1
    echo ls -la $DESKTOP                               >> $LAUNCH_LOG_LOCAL 2>&1
    ls -la $DESKTOP                                    >> $LAUNCH_LOG_LOCAL 2>&1
    rm                          $DESKTOP/i15_Launchers >> $LAUNCH_LOG_LOCAL 2>&1
    ln -s /scratch/i15_Launchers $DESKTOP/i15_Launchers >> $LAUNCH_LOG_LOCAL 2>&1
    rm                          $DESKTOP/DLS_Launchers >> $LAUNCH_LOG_LOCAL 2>&1
    ln -s /scratch/DLS_Launchers $DESKTOP/DLS_Launchers >> $LAUNCH_LOG_LOCAL 2>&1
    ;;
  *)
    :
    echo i15 gda_environment.sh local $DISPLAY          > $LAUNCH_LOG_REMOT
    (cd $DESKTOP || mkdir $DESKTOP)                    >> $LAUNCH_LOG_REMOT 2>&1
    echo ls -la $DESKTOP                               >> $LAUNCH_LOG_REMOT 2>&1
    ls -la $DESKTOP                                    >> $LAUNCH_LOG_REMOT 2>&1
    rm                          $DESKTOP/i15_Launchers >> $LAUNCH_LOG_REMOT 2>&1
    ln -s /scratch/i15_Launchers $DESKTOP/i15_Launchers >> $LAUNCH_LOG_REMOT 2>&1
    rm                          $DESKTOP/DLS_Launchers >> $LAUNCH_LOG_REMOT 2>&1
    ln -s /scratch/DLS_Launchers $DESKTOP/DLS_Launchers >> $LAUNCH_LOG_REMOT 2>&1
    ;;
esac
