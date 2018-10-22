from BeamlineI06.Users.ClassixSystem.ClassixSystem import ClassixSystemClass, ClassixCameraPseudoDeviceClass, ClassixFilterPseudoDeviceClass;


print "Note: Use Object name 'classix' for direct communication to the Classix System";
classix = ClassixSystemClass('classxi','172.23.106.152', 6342 );

print "Note: Use Pseudo Device name 'camera' for Classix camera";
camera = ClassixCameraPseudoDeviceClass('camera',classix);

print "Note: Use Pseudo Device name 'filter' for Classix filter";
filter = ClassixFilterPseudoDeviceClass('filter',classix);


