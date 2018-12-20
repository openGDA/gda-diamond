#! /bin/sh

if [ ! -n "$BEAMLINE" ]; 
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi

# for Mythen II
export ROOTSYS=/dls/i11/software/mythen/root
export QTDIR=/dls/i11/software/mythen/qt
export MYTHENDIR=/dls/i11/software/mythen/NewMythenMCS

export PATH=$QTDIR/bin:$ROOTSYS/bin:$MYTHENDIR/bin:$PATH
export LD_LIBRARY_PATH=$QTDIR/lib:$ROOTSYS/lib:$LD_LIBRARY_PATH
export MANPATH=$QTDIR/doc/man/usr/local/man:$MANPATH

# for Mythen 3.0
#module load mythen/3.0
