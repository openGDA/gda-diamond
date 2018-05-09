How to Connect to Zebra Test Equipment

The IOC runs on Tom Cobb's PC pc0013.cs.
1. Start IOC
>ssh pc0013.cs
>cd /dls_sw/work/R3.14.11/support/zebra/iocs/example/bin/linux-x86/
>./stexample.sh

2. Start EDM
>ssh pc0013.cs
>/dls_sw/work/R3.14.11/support/zebra/iocs/example/bin/linux-x86/stexample-gui



GDA JCA Setting
com.cosylab.epics.caj.CAJContext.addr_list           = pc0013.cs.diamond.ac.uk
com.cosylab.epics.caj.CAJContext.repeater_port       = 5065
com.cosylab.epics.caj.CAJContext.server_port         = 5064

4. GDA I13 Dummy Client
client.xml
<!-- 	<import resource="../../../devices/dummy/pco1_ndplugins.xml"/>
 -->	<import resource="../../../devices/zebra/pco1_ndplugins.xml"/>
