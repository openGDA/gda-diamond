
import java
import gda

class PdClass(gda.device.scannable.ScannableMotionBase):
	pass;


pd=PdClass()

pd.setExtraNames(['X'])

en=pd.getExtraNames()

>>>en
array(java.lang.String, [u'X'])
>>>len(en)
1
>>>java.lang.reflect.Array.getLength(en)
1

>>>en.append('Y')
>>>len(en)
2
>>>java.lang.reflect.Array.getLength(a)
3

>>>print a
array(java.lang.String, [u'X', u'Y'])

>>>b=java.lang.reflect.Array.get(en, 0); print b
X
>>>b=java.lang.reflect.Array.get(en, 1); print b
Y
>>>b=java.lang.reflect.Array.get(en, 2); print b
None
