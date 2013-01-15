How to setup procServ on tfg2 - as user on i12-ws001
(Copied from i22-rapid-mem-gig)

0. cd here (/dls_sw/i12/software/gda/i12-config/tfg2
1. 	scp daq_servers root@i12-tfg2-10ge:/etc/init.d/
2. 	scp server_list root@i12-tfg2-10ge:/mnt/client/etc/
3a  Edit da.server.rapidprocServ to use account i12detector
3. 	scp da.server.rapidprocServ root@i12-tfg2-10ge:/etc/init.d/
4. 	scp procServ root@i12-tfg2-10ge:/usr/local/bin/
5. 	ssh root@i12-tfg2-10ge
6. 	su i12detector
7.	mkdir ~/.ssh
8.	cd ~/.ssh
9.	ssh-keygen -t dsa
10.	cat id_dsa.pub > authorized_keys
11.	exit
12. exit ( back to i12-ws001)
13.	scp root@i12-tfg2-10ge:/home/i12detector/.ssh/id_dsa tfg2_id_dsa
14. Edit ../bin/tfg2View to point bl12i-ea-tfg2-01
15. Edit ../bin/tfg2ForceRestart to point to i12-tfg2-10ge using identify file tfg2_id_dsa from step 6.

16. Add a link in /etc/rc2.d to run daq_servers:
b13i-ea-tfg2-01:/etc/rc2.d# ln -s ../init.d/daq_servers S99daq_servers
