# Script to start da.server using procServ, first killing any previously old running procServ command
# This should be run on remote machine e.g. b18-xspress1
# imh 4/6/2020

# Kill any previously running procServ da.server commmand :
pid=$(pgrep -f 'procServ -n daserver')
if [ -n "$pid" ]; then
        echo "Killing procServ process $pid";
        kill -9 $pid
        echo "Sleeping for 65 seconds for port 1972 to become available"
	sleep 65
fi

echo "Starting da.server using procServ" 

echo "Starting da.server using procServ. Use tfg2View.sh to view log output"
cd /home/b18detector/xspress2_36element
procServ -n daserver -l 8921 --noautorestart -L log.txt 8920 /usr/local/bin/da.server -port=1972 -log
tail -F log.txt


