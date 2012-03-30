#!/bin/sh
# Remove GDA Launchers from user's Desktop on user logout
# to be copied to .logout at user's $HOME on user login 
# to be run on user logout
#
if [ -h "$HOME/Desktop/GDA_Launchers" ]; then
	rm -f $HOME/Desktop/GDA_Launchers
fi
