import re
from gda.jython import InterfaceProvider
from gda.factory import Finder

metadata=Finder.find("GDAMetadata")

def pwd():
        print gda.jython.InterfaceProvider.getPathConstructor().createFromDefaultProperty()

alias("pwd")

def cwd(subdir=None):
	if subdir==None:
		metadata.setMetadataValue("subdirectory","")
	else:
		sane=re.compile("[^a-zA-Z0-9-_:]")
		subdir=sane.sub("",subdir)
		metadata.setMetadataValue("subdirectory",subdir)
        print InterfaceProvider.getPathConstructor().createFromDefaultProperty()
	
alias("cwd")
