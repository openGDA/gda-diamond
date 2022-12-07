#!/bin/bash
gnome-terminal -x sh -c 'ssh 172.23.90.204 -l i20-1detector -X "/home/i20-1detector/restart-xh.sh"; exec bash'