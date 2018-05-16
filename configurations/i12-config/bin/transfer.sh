#!/bin/bash

cd $1

HOST='i12-phantom01'
USER='anonymous'
PASSWD='pco.transfer'

ftp -n -i $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
bin
mget *.tiff
mdelete *.tiff
quit
END_SCRIPT
exit 0

