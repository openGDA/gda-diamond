#!/bin/bash
gnome-terminal -x ssh -i /dls_sw/i20/software/gda/config/daserver.key i20detector@i20-xspress0 'pkill -9 da.server; echo killing da.server process will now sleep for 65 seconds for port 1972 to become available; sleep 65; echo starting da.server process on port 1972, you may close this window now.; cd xspress2_36element/; da.server -port=1972 -log' &
