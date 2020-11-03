#!/bin/bash
# This should be run as b18user (the ssh keys for accessing b18-xspress1 are in /home/b18user/.ssh)
nohup xterm -e "ssh b18detector@b18-xspress1 < /dls_sw/b18/software/gda/bin/restart_script.sh" &
