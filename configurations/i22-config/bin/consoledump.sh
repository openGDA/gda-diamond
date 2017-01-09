#!/bin/bash

PIP=/tmp/`basename $0`-$$
mknod $PIP p
tail -n 1 -f $1 >  $PIP &
awk '{
        if (!/DEBUG/) print ;
        if (/uk.ac.diamond.daq.server.GDAServerApplication - main object server started/) {
            print "\nAll done, you can start the client now\n" ;
            exit ;
        }
}' < $PIP
rm $PIP

sleep 6