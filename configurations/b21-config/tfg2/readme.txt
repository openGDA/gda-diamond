How to setup procServ on tfg2 - as user on i13-ws001
(Copied from i22-rapid-mem-gig)

0. cd here (/dls_sw/i13/software/gda/config/tfg2
1. 	scp daq_servers root@bl13i-ea-tfg2-01:/etc/init.d/
2. 	scp server_list root@bl13i-ea-tfg2-01:/mnt/client/etc/
3. 	scp da.server.rapidprocServ root@bl13i-ea-tfg2-01:/etc/init.d/
4. 	scp procServ root@bl13i-ea-tfg2-01:/usr/local/bin/
5. 	ssh root@bl13i-ea-tfg2-01
6. 	su i13detector
7.	mkdir ~/.ssh
8.	cd ~/.ssh
9.	ssh-keygen -t dsa
10.	cat id_dsa.pub > authorized_keys
11.	exit
12. exit ( back to i13-ws001)
13.	scp root@bl13i-ea-tfg2-01:/home/i13detector/.ssh/id_dsa tfg2_id_dsa
14. Edit ../bin/tfg2View to point bl13i-ea-tfg2-01
15. Edit ../bin/tfg2ForceRestart to point to bl13i-ea-tfg2-01 using identify file tfg2_id_dsa from step 6.

16. Add a link in /etc/rc2.d to run daq_servers:
b13i-ea-tfg2-01:/etc/rc2.d# ln -s ../init.d/daq_servers S99daq_servers
