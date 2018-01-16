#!/bin/bash
## 9 element :
xterm -e ssh b18detector@b18-xspress0 'pkill -9 da.server; echo killing da.server process will now sleep for 65 seconds for port 1972 to become available; sleep 65; echo starting da.server process on port 1972; cd xspress2_9element/; da.server -port=1972 -log' &

## 36 element :
#xterm -e ssh b18detector@b18-xspress1 'pkill -9 da.server; echo killing da.server process will now sleep for 65 seconds for port 1972 to become available; sleep 65; echo starting da.server process on port 1972; cd xspress2_36element/; da.server -port=1972 -log' &
