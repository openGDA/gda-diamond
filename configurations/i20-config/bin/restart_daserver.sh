#!/bin/bash

SSH_KEY_FILE=/dls_sw/i20/software/gda/config/daserver.key

nohup xterm -e "ssh -i $SSH_KEY_FILE i20detector@i20-xspress0 < /dls_sw/i20/software/gda/bin/restart_script.sh" &
