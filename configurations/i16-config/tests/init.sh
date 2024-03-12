#!/bin/sh

pathprepend_ifnotpresent ()
{ 
    if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
        PATH="$1:$PATH";
    fi
}

export TEST_SCRIPTS=$(readlink -f $(dirname $BASH_SOURCE[0]))
export DEPLOYMENT=$(readlink -f $TEST_SCRIPTS/../../../../..)
export VISIT=$DEPLOYMENT/gda_data_non_live

module load msmapper/1.7 --no-pager
pushd $VISIT

echo -e "\nDEPLOYMENT=  $DEPLOYMENT\nVISIT=       $VISIT\nTEST_SCRIPTS=$TEST_SCRIPTS\n"

pathprepend_ifnotpresent $TEST_SCRIPTS
for f in [ $TEST_SCRIPTS/* ] ; do test -x $f && echo $(basename $f) ; done

