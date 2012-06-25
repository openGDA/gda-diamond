#!/bin/sh
# This script assumes that $BEAMLINE is set (e.g. i02, i18, b16) if not exit...

# **** DO NOT EDIT THIS SCRIPT AS IT MAY BE AUTOMATICALLY OVERWRITTEN *****

if [ ! -n "$BEAMLINE" ]; 
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi
if [ ! -n "$GDAFOLDER" ]; 
then
  echo "Please set GDAFOLDER environment variable."
  exit 1
fi


export PATH=${GDAFOLDER}/${BEAMLINE}-config/bin:${PATH}

( cd $HOME/Desktop && test -e "${BEAMLINE}_Launchers" || ln -s /usr/local/etc/"${BEAMLINE}_Launchers" . ) > /dev/null 2>&1
( cd $HOME/Desktop && test -e "DLS_Launchers" || ln -s /usr/local/etc/"DLS_Launchers" . ) > /dev/null 2>&1

export VISNO=`/dls_sw/apps/mx-scripts/visit_tools/currentvisit`
export YEAR=`date +%Y`

if [[ ! `groups` =~ "dls_staff" && -r /dls/${BEAMLINE}/data/${YEAR}/${VISNO} ]]; then
  ( cd $HOME && test -e "${VISNO}" || ln -s /dls/${BEAMLINE}/data/${YEAR}/"${VISNO}" . ) > /dev/null 2>&1
fi
source $GDAFOLDER/workspace/builder/set_tools.sh > ~/.dasc_sw_setup.log
