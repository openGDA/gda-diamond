#!/bin/bash
source /etc/profile.d/beamline.sh

SLEEPTIME=21600  # time in seconds between checks
FULLVISNO=/dls/${BEAMLINE}/data/ #path to backup.
BACKUPPATH=/dls/sci-scratch/${BEAMLINE}-data/
 
echo "===================================================================="
echo
echo "This program will rsync your data to $BACKUPPATH"
echo "Everything within $FULLVISNO will be backed up"
echo


while true; do
  echo `date`" starting backup" >> backup.log
  rsync -tr $FULLVISNO $BACKUPPATH > /dev/null 2>&1
  echo `date`" ending backup" >> backup.log
  sleep $SLEEPTIME
done
