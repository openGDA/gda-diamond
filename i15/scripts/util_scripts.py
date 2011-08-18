"""
Collection of functions and classes that do not rely on any other scripts in this folder
"""
from gdascripts.messages.handle_messages import simpleLog
import glob
def updateFileOverwriteFlag(fullFileName, overwriteFlag):
	"""
	If file already exists update overwrite flag to y, n, ya or na
	"""
	if (doesFileExist(fullFileName)):
		if (overwriteFlag != 'ya' and overwriteFlag != 'na'):
			simpleLog ( "File " + fullFileName + " already exists." )
			overwriteFlag = InputCommands.requestInput("Overwrite? (y / n / ya=yes to all / na=no to all): ")
		if (overwriteFlag == 'n' or overwriteFlag == 'na'):
			simpleLog ( "Existing file not overwritten" )
			simpleLog ( "=============================" )
			
	return overwriteFlag

def doesFileExist(filename):
	"""
	Returns true if file exists, else false
	"""
	pathList = glob.glob(filename)
	return (len(pathList) > 0)