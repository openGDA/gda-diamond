#!/bin/bash

SLEEPTIME=10  # time in seconds between checks

## This bit catches Ctrl-C, does a bytecheck and prompts to unmount
## bytechecks never seem to exactly match, don't know why
trap 'unmount' SIGINT
unmount()
{
  echo "Ctrl-C detected..."
  if [ $PROCESSING == 0 ]; then
    BYTESINVISIT=$(du -sb  $FULLVISNO | awk ' {print $1} ')
    BYTESONUSB=$(du -sb /media/$USBNAME/$BACKUPPATH | awk ' {print $1} ')
  else
    BYTESINVISIT=$(du -sb --exclude=process* $FULLVISNO | awk ' {print $1} ')
    BYTESONUSB=$(du -sb --exclude=process* /media/$USBNAME/$BACKUPPATH | awk ' {print $1} ')
  fi
  echo "Total bytes in $FULLVISNO: $BYTESINVISIT"
  echo "Total bytes backed up to /media/$USBNAME/$BACKUPPATH: $BYTESONUSB"
  zenity --title "Unmount drive?" --question --text "Click OK to unmount the drive" --window-icon=question
  UNMOUNTNO=$?
  if [ $UNMOUNTNO == 0 ]; then
    umount -v /media/$USBNAME
    echo "Exiting..."
  else
    echo "Exiting without unmounting..."
  fi
  sleep 5
  exit
}
## Catches Ctrl-Z, does a bytecheck
trap 'bytecheck' SIGTSTP
bytecheck()
{
  echo "Ctrl-Z detected..."
  if [ $PROCESSING == 0 ]; then
    BYTESINVISIT=$(du -sb  $FULLVISNO | awk ' {print $1} ')
    BYTESONUSB=$(du -sb /media/$USBNAME/$BACKUPPATH | awk ' {print $1} ')
  else
    BYTESINVISIT=$(du -sb --exclude=process* $FULLVISNO | awk ' {print $1} ')
    BYTESONUSB=$(du -sb --exclude=process* /media/$USBNAME/$BACKUPPATH | awk ' {print $1} ')
  fi
  echo "Total bytes in $FULLVISNO: $BYTESINVISIT"
  echo "Total bytes backed up to /media/$USBNAME/$BACKUPPATH: $BYTESONUSB"
}

LSDRIVES=$(ls /media | sed -e '/floppy/d' -e '/cdrecorder/d' )
DRIVES=$(echo $LSDRIVES | wc -w)
if [ $DRIVES == 0 ]; then
  zenity --title "USB Drive Not Found" --error --text "USB drive not found.\n\nEnsure a USB drive is connected, and try again." --window-icon=error
  exit
elif [ $DRIVES == 1 ]; then
  USBNAME=$(echo $LSDRIVES | awk ' {print $1} ')
elif [ $DRIVES == 2 ]; then
  NAME1=$(echo $LSDRIVES | awk ' {print $1} ')
  NAME2=$(echo $LSDRIVES | awk ' {print $2} ')
  USBNAME=$(zenity --title "Pick a USB Drive" --list --text "Please choose the correct drive from those listed below" --radiolist\
    --column "" --column "Name of drive" \
    False $NAME1\
    False $NAME2)
elif [ $DRIVES == 3 ]; then
  NAME1=$(echo $LSDRIVES | awk ' {print $1} ')
  NAME2=$(echo $LSDRIVES | awk ' {print $2} ')
  NAME3=$(echo $LSDRIVES | awk ' {print $3} ')
  USBNAME=$(zenity --title "Pick a USB Drive" --list --text "Please choose the correct drive from those listed below" --radiolist\
    --column "" --column "Name of drive" \
    False $NAME1\
    False $NAME2\
    False $NAME3)
else
  zenity --title "Too many USB Drives!" --error --text "Too many USB drives are connected.\n\nEnsure one USB drive is connected, and try again." --window-icon=error
  exit
fi
SURE=$?
if [ $SURE != 0 ]; then
  echo "Exiting"
  sleep 1
  exit
fi
if [ ! -w /media/$USBNAME ]; then
  zenity --title "USB Drive Not Writable" --error --text "USB drive $USBNAME not writable.\n\nEnsure a writable USB drive is connected, and try again." --window-icon=error
  exit
fi
YEAR=$(date +%Y)
#VISNO=$(/dls_sw/dasc/bin/currentvisit)
VISNO=mx300-22/Glyn
FULLVISNO=/dls/$BEAMLINE/data/$YEAR/$VISNO/
if [ $VISNO == "0-0" -o ! -r $FULLVISNO ]; then
  DEFVISNO=$(grep ^gda.defVisit /dls/$BEAMLINE/software/gda/config/properties/java.properties | awk ' NR==1 ' | cut -c 14-)
  if [ $DEFVISNO ]; then
    VISNO=$DEFVISNO
    FULLVISNO=/dls/$BEAMLINE/data/$YEAR/$VISNO/
  fi
  until [ -r $FULLVISNO	]; do
    echo "No Visit Found"
    FULLVISNO=$(kdialog --getexistingdirectory /dls/$BEAMLINE/data/$YEAR/ --title "Please select your visit number" --caption "")
    SURE=$?
    if [ $SURE != 0 ]; then
      exit
    fi
    VISNO=$(echo $FULLVISNO | cut -c 20-)
  done
fi

echo "===================================================================="
echo
echo "This program will rsync your data to your USB drive"
echo "Everything within $FULLVISNO will be backed up"
echo

BACKUPPATH=$(zenity --title "Backup Data?" --entry --text "Back up everything within $FULLVISNO to \n\n/media/$USBNAME/..." --entry-text "dls/$VISNO" )
SURE=$?
if [ $SURE != 0 ]; then
  exit
fi

zenity --title "Backup Processing Directories?" --question --text "Do you want to back up your 'processing' and 'processed' directories as well?\n\nClick OK for Yes, Cancel for No" --window-icon=question
PROCESSING=$?
if [ -d /media/$USBNAME/$BACKUPPATH ]; then
  zenity --warning --title "Directory Already Exists" --text "/media/$USBNAME/$BACKUPPATH already exists, any data with the same name may be overwritten.\n\nAre you sure?" --window-icon=warning
  SURE=$?
  if [ $SURE != 0 ]; then
    exit
  fi
  echo "Writing to /media/$USBNAME/$BACKUPPATH..."
else
  echo "Creating /media/$USBNAME/$BACKUPPATH..."
  mkdir -p /media/$USBNAME/$BACKUPPATH
fi

while true; do
  if [ $PROCESSING == 0 ]; then
    rsync -trv $FULLVISNO /media/$USBNAME/$BACKUPPATH
  else
    rsync -trv --exclude=process* $FULLVISNO /media/$USBNAME/$BACKUPPATH
  fi
  echo
  SPACELEFT=$(df /media/$USBNAME | grep /media/$USBNAME | awk ' {print $4} ')
  SPACELEFTH=$(df -h /media/$USBNAME | grep /media/$USBNAME | awk ' {print $4} ')
  if [ $SPACELEFT -lt 50000 ]; then
    zenity --error --title "Out of Space" --text "USB Drive $USBNAME only has $SPACELEFTH space left." --window-icon=error
    exit
  fi
  echo "USB drive $USBNAME has $SPACELEFTH space left."
  echo "Waiting "$SLEEPTIME"s for new data..."
  echo
  sleep $SLEEPTIME
done
