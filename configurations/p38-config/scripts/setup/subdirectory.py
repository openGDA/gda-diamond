import re as _re
from gda.jython import InterfaceProvider
from gdaserver import GDAMetadata as metadata

_sane = _re.compile("[^a-zA-Z0-9-_:]")

def pwd():
        print gda.jython.InterfaceProvider.getPathConstructor().createFromDefaultProperty()

alias("pwd")

def cwd(subdir=None):
	if subdir is None:
		metadata["subdirectory"] = ""
	else:
		subdir=_sane.sub("",subdir)
		metadata["subdirectory"] = subdir
        print InterfaceProvider.getPathConstructor().createFromDefaultProperty()
	
alias("cwd")
