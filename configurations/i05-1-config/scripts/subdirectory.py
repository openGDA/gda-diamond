import re

metadata=finder.find("GDAMetadata")

def pwd():
        print gda.data.PathConstructor.createFromDefaultProperty()

alias("pwd")

def cwd(subdir=None):
	if subdir==None:
		metadata.setMetadataValue("subdirectory","")
	else:
		sane=re.compile("[^a-zA-Z0-9-_:]")
		subdir=sane.sub("",subdir)
		metadata.setMetadataValue("subdirectory",subdir)
        print gda.data.PathConstructor.createFromDefaultProperty()
	
alias("cwd")
