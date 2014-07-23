#!/bin/bash

if [ ! -n "$BEAMLINE" ];
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi
# before running this: ssh ${BEAMLINE}-storage
#if [ `hostname` = "${BEAMLINE}-control.diamond.ac.uk" ] ; then
	#	echo "You have logged into `hostname`"
#else
	#	echo "You must log into ${BEAMLINE}-storage.diamond.ac.uk to run this script."
	#	exit 0
#fi

## set gda and config directory permissions
echo "gda and dls_dasc all permissions to /gda, otherwise rw only..."
sudo setfacl -R -m u::rwx,g::rwx,g:dls_dasc:rwx,g:gda:rwx,o::rx,d:u::rwx,d:g::rwx,d:g:dls_dasc:rwx,d:g:gda:rwx,d:o::rx /dls_sw/${BEAMLINE}/software/gda

echo "beamline staff edit perms to config..."
sudo setfacl -R -m g:${BEAMLINE}_staff:rwx,d:g:${BEAMLINE}_staff:rwx /dls_sw/${BEAMLINE}/software/gda/config/

echo "beamline staff edit perms to beamline bin..."
sudo setfacl -R -m g:${BEAMLINE}_staff:rwx,d:g:${BEAMLINE}_staff:rwx /dls_sw/${BEAMLINE}/bin/

#echo "everyone permissions to config/var and beamline var..."
#sudo setfacl -R -m o::rwx,d:o::rwx /dls_sw/${BEAMLINE}/software/gda/config/var
#sudo setfacl -R -m o::rwx,d:o::rwx /dls_sw/${BEAMLINE}/var

echo "ensure core gda launcher is executable"
sudo setfacl -R -m u::rwx,g::rwx,g:dls_dasc:rwx,g:gda:rwx,o::rx,d:u::rwx,d:g::rwx,d:g:dls_dasc:rwx,d:g:gda:rwx,d:o::rx /$SOFTWAREFOLDER/$BEAMLINE/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda
	
echo "everyone permissions write to command history file ..."
sudo setfacl -R -m o::rwx,d:o::rwx /dls_sw/${BEAMLINE}/scripts/.cmdHistory.txt

echo "GDA remote Server ${BEAMLINE}ssh.key must by owned by gda"
sudo chown gda:dls_dasc /dls_sw/${BEAMLINE}/software/gda/config/${BEAMLINE}ssh.key
sudo chown gda:dls_dasc /dls_sw/$BEAMLINE/${BEAMLINE}ssh.key

echo "set up i11user permissions to write data to commissioning dir 0-0, only run once at start of the new year"
sudo setfacl -R -m u:${BEAMLINE}user:rwx,d:u:${BEAMLINE}user:rwx /dls/${BEAMLINE}/data/`date +%Y`/0-0
sudo setfacl -R -m u:${BEAMLINE}user:rwx,d:u:${BEAMLINE}user:rwx /dls/${BEAMLINE}/data/`date +%Y`/ee0/processing

#setfacl -R -d -m u:gda:rwx /dls/${BEAMLINE}/software/gda/config/testing
#setfacl -R -m u:gda:rwx /dls/${BEAMLINE}/software/gda/config/testing
