#! /bin/sh

if [ "X$1" == "X" ] ; then 
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

cat >> $xmlfile <<EOF

        <bean id="$motor" class="gda.device.motor.EpicsMotor">
                <property name="pvName" value="$pv" />
		<property name="local" value="true" />
        </bean>
        <bean id="$scannable" class="gda.device.scannable.ScannableMotor">
                <property name="motor" ref="$motor" />
		<property name="local" value="true" />
        </bean>
EOF

scannables="$scannables $scannable"

done

cat >> $xmlfile <<EOF

        <bean id="$1" class="gda.device.scannable.scannablegroup.ScannableGroup">
		<property name="local" value="true" />
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
        </bean>
</beans>
EOF

exit 0
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
           http://www.springframework.org/schema/beans/spring-beans-2.5.xsd">

        <bean id="mfstage_x_motor" class="gda.device.motor.EpicsMotor">
                <property name="pvName" value="BL22I-MO-TABLE-07:X" />
        </bean>
        <bean id="mfstage_y_motor" class="gda.device.motor.EpicsMotor">
                <property name="pvName" value="BL22I-MO-TABLE-07:Y" />
        </bean>
        <bean id="mfstage_z_motor" class="gda.device.motor.EpicsMotor">
                <property name="pvName" value="BL22I-MO-TABLE-07:Z" />
        </bean>
        
        <bean id="mfstage_x" class="gda.device.scannable.ScannableMotor">
                <property name="motor" ref="mfstage_x_motor" />
        </bean>
        <bean id="mfstage_y" class="gda.device.scannable.ScannableMotor">
                <property name="motor" ref="mfstage_y_motor" />
        </bean>
        <bean id="mfstage_z" class="gda.device.scannable.ScannableMotor">
                <property name="motor" ref="mfstage_z_motor" />
        </bean>

        <bean id="mfstage" class="gda.device.scannable.scannablegroup.ScannableGroup">
                <property name="groupMembers">
                        <list>
                                <ref bean="mfstage_x" />
                                <ref bean="mfstage_y" />
                                <ref bean="mfstage_z" />
                        </list>
                </property>
        </bean>
</beans>

