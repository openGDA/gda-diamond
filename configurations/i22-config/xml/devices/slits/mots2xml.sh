#! /bin/sh

if [ "X$1" = "X" ] ; then 
	echo need name >&2
	exit 1
fi

xmlfile=$1.xml
if [ -f $xmlfile ] ; then
	echo $xmlfile exits >&2
	exit 1
fi

cat >> $xmlfile << EOF
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
           http://www.springframework.org/schema/beans/spring-beans-2.5.xsd">
EOF
scannables=""
while read axis pv ; do

motor=${1}_${axis}_motor
scannable=${1}_${axis}
pv=`echo $pv | sed 's/.VAL$//'`

case $axis in 
*i) 

cat >> $xmlfile << EOF

	<bean id="$scannable" class="gda.device.scannable.EpicsScannable">
		<property name="useNameAsExtraName" value="true" />
		<property name="hasUnits" value="false" />
		<property name="pvName" value="$pv" />
		<property name="local" value="true" />
	</bean>
EOF
	;;
*)

case $pv in
 *-*)
# is a PV
cat >> $xmlfile <<EOF

        <bean id="$motor" class="gda.device.motor.EpicsMotor">
                <property name="pvName" value="$pv" />
                <property name="local" value="true" />
        </bean>
EOF
	;;
 *)
# is an XML device name
cat >> $xmlfile <<EOF

        <bean id="$motor" class="gda.device.motor.EpicsMotor">
		<property name="deviceName" value="$pv" />
                <property name="local" value="true" />
        </bean>
EOF
	;;
esac

cat >> $xmlfile <<EOF
        <bean id="$scannable" class="gda.device.scannable.ScannableMotor">
                <property name="motor" ref="$motor" />
                <property name="local" value="true" />
        </bean>
EOF

	;;
esac

scannables="$scannables $scannable"

done

cat >> $xmlfile <<EOF

        <bean id="$1" class="gda.device.scannable.scannablegroup.ScannableGroup">
                <property name="groupMembers">
                        <list>
EOF

for s in $scannables ; do 
cat >> $xmlfile <<EOF
                                <ref bean="$s" />
EOF
done

cat >> $xmlfile <<EOF
                        </list>
                </property>
                <property name="local" value="true" />
        </bean>
</beans>
EOF

exit 0
