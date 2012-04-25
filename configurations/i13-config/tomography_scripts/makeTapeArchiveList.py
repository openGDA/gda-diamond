
'''
Created on 14 Nov 2009
Modified on 24 Feb 2012: Specific for i12: echo the processed directorys and ignored ones. Robert Atwood
Modified on 24 Feb 2012: Encapsulated in a function definintion for easy importing
Modified on 23 Feb 2012: removed some ignored subdirs
Modified on 20 Oct 2011: fixed missing description tag for datafile
Modified on 18 May 2011: removed parenthesis from list of illegal characters as now allowed by SRB
Modified on 11 Apr 2011: visitId and invNb in uppercase
Modified on 06 Jul 2010: fixed extra slash in datafile location
20 Oct 2010: added size information
@author: ghita
'''

'''
Script for creating drop files for a set of visits in a /beamline/year/ directory or a visit directory
'''

import os, time, datetime, sys, glob, stat
from os import listdir, sep
from os.path import isdir
import xml.dom.minidom
#import xml.dom.ext
import random, decimal
import shutil


fileList = []

# function to convert floating point number of seconds to
# hh:mm:ss.sss
def secondsToStr( t ):
    return "%02d:%02d:%02d.%03d" % \
        reduce( lambda ll, b : divmod( ll[0], b ) + ll[1:],
            [( t * 1000, ), 1000, 60, 60] )


def validVisit( visit_id ):
    valid = False

    if ( visit_id.find( '-' ) > -1 ) :
        split = visit_id.split( "-" )

        part1 = split[0]
        part2 = split[1]

        if ( visit_id.find( '-' ) > -1 ) and not( '0-0' in visit_id ) and not( 'in' in visit_id ) and part2.isdigit() and isinstance( visit_id[:2], str ) and part1[2:].isdigit():
            valid = True

    return valid

def validFileName( filenamepath ):# needs improvement by doing second validation only if precedent is true
    """
    check for invalid characters, e.g. '('
    """
    
    noIllegalchar = True
    #noWhitespacechar = True
    #rightPlace = True
    
    #String illegal = "\"M\"\\a/ry/ h**ad:>> a\\/:*?\"| li*tt|le|| la\"mb.?";

    # 18-05-2011 removed parenthesis from list of illegal characters as now accepted by SRB
    illegal = "\\";#"()\\,'\/:*?<>|()"
    for letter in str( filenamepath ):
        if ( letter in illegal ):
            noIllegalchar = False
            #print '\n' + str( filenamepath ) + ' contains invalid characters, rejected.'
    """
    check for white spaces
    """
    # check the presence of white spaces
    #p = re.compile( '(%s)' % ( '|'.join( [c for c in ws] ) ) )
    #result = p.sub( '', filenamepath )

    #if not( os.path.exists( result ) ):
        #noWhitespacechar = False
        ##print '\n' + str( filenamepath ) + ' contains white spaces, rejected.'

    """
    check for files in ignored subdirectories
    """
    list = ( str( filenamepath ).lower() ).split( '/' )
    # remove file name
    list.remove( list[-1] )
    #print 'list: ' + str( list )
    #noIgnoredsubdirs = not( 'xml' in list or '.workspace' in list or 'spool' in list or 'processing' in list or 'processed' in list or 'jpegs' in list )
    noIgnoredsubdirs = not( 'xml' in list or '.workspace' in list or 'spool' in list or 'tmp' in list )
    
    
    """
    check for files in the wrong year directory
    """
    #datafile_creation_time = getCreation_date( filenamepath )
    ##inserting a 'T' between date and time
    #datafile_creation_time = str( datafile_creation_time ).replace( ' ', 'T' )

    #stripped_date = str( datafile_creation_time ).strip()
    #year = stripped_date[0:4]
    
    #if year != currentYear:
        #rightPlace = False
    
    ################
    #return ( noIllegalchar and noWhitespacechar and noIgnoredsubdirs and rightPlace )
    
    #if not(noIllegalchar):
        #countInvalidCharacters += 1
    #if not(noIgnoredsubdirs):
        #countInvalidSubdirs += 1
    #if not(rightPlace):
        #countInvalidYear += 1
    
    #return ( noIllegalchar and noIgnoredsubdirs and rightPlace )
    return ( noIllegalchar and noIgnoredsubdirs )

def validDirectory( dir ):
    list = ( str( dir[0] ).lower() ).split( '/' )
    print "list = ", list
    st = not( 'spool' in list or 'tmp' in list or '0-0' in list or 'xml' in list or '.workspace' in list ) and list[5].find( '-' ) > -1
    print "st = ", st

    if st:
        print 'processing directory ' + dir[0]
        return True
    else:
        print 'ignoring directory ' + dir[0]

def getCreation_date( filename ):
    t = os.path.getctime( filename )
    return datetime.datetime.fromtimestamp( t )

def getModification_date( filename ):
    t = os.path.getmtime( filename )
    return datetime.datetime.fromtimestamp( t )

def insert( original, new, pos ):
    '''Inserts new inside original at pos.'''
    return original[:pos] + new + original[pos:]

def gen_random_decimal( i, d ):
    return decimal.Decimal( '%d.%d' % ( random.randint( 0, i ), random.randint( 0, d ) ) )

def populateFiles( root, dirList ):
    global fileList
    for file in dirList:
        #print str( os.path.join( root, file ) )
        fileList.append( os.path.join( root, file ) )

def populateDirectory( dirEntry ):
    #print dirEntry[0] #+ "/"
    populateFiles( dirEntry[0], dirEntry[2] )


def maketapearchivelist(arglist):
   # collecting drop directory name from standard input
   global fileList
   nbFiles = 0

   if( len( arglist ) != 3 ):
       print 'Usage:   python GenerateDarcServerXML searchDir dropDir'
       print 'Example: python GenerateDarcServerXML /dls/i16/data/2009/ /dls/bl-misc/dropfiles/icat/dropZone/'
       print 'Note:    use the dot ''.'' to use the current directory as a dropDir\n '
       print 'The current script ignores the following subdirectories: spool and processing, processed and jpegs'
       sys.exit()

   # counting begins from '0' in argv[] including the name of the module
   searchDir = arglist[1]
   dropDir = arglist[2]

   #print 'dropDir = ' + dropDir
   #print 'sys.path[0] = ' + sys.path[0]

   if ( dropDir == '.' ):
       dropDir = sys.path[0] + '/' # the current directory
       print '\nusing the current directory as a drop folder: ' + dropDir


   start = time.time()

   # retrieve the list of data files to process
   tree = os.walk( searchDir )

   for directory in tree:
       #print '\ndirectory: ' + str( directory )
       #
       # include only valid files from valid visitIds/sub-directories
       if validDirectory( directory ):
           populateDirectory( directory )

   print 'fileList length is ' + str( len( fileList ) )

   #
   # at this point only files from valid visits/sub-directories are contained in fileList
   #
   for file in fileList:

       fullpath = str( file )
       #print '\n*****'
       #print '\nfullpath= ' + str( fullpath )
       #print '\n*****'

       if os.path.isfile( fullpath ):
           nbFiles = nbFiles + 1

           #print fullpath

           # retrieve visitID
           aList = fullpath.split( '/' )
           visitID = str( aList[5] ).upper()
           #print 'visitID= ' + visitID

           #get dataset_name
           if len( aList ) == 7:
               dataset_name = 'topdir'

           if len( aList ) > 7:
               dataset_name = aList[6]
               for i in range( 7, len( aList ) - 1 ):
                   dataset_name = dataset_name + '/' + str( aList[i] )
                   #print dataset_name


           instrument = aList[2]
           #print 'instrument: ' + instrument

           title = 'some title'
           #title = title.strip()

           bList = ( visitID ).split( '-' )
           inv_number = str (bList[0]).upper()
           #print 'inv_number: ' + inv_number

           visit_id = visitID
           #print 'visit_id: ' + visit_id

           inv_type = 'experiment'
           #print 'inv_type: '+ inv_type

           dataset_type = 'EXPERIMENT_RAW'
           dataset_description = 'unknown'

           datafile_name = aList[-1] # last element of a list
           #print 'datafile_name: ' + datafile_name

           datafile_location = fullpath
                   
           datafile_description = 'unknown'
           #print 'datafile_description: ' + datafile_description

           datafile_version = '1.0'
           #print 'datafile_version: ' + datafile_version

           datafile_creation_time = getCreation_date( fullpath )
           #inserting a 'T' between date and time
           datafile_creation_time = str( datafile_creation_time ).replace( ' ', 'T' )
           #print 'datafile_creation_time: ' + str( datafile_creation_time ).replace( ' ', 'T' )

           #inserting a 'T' between date and time
           datafile_modification_time = getModification_date( fullpath )
           datafile_modification_time = str( datafile_modification_time ).replace( ' ', 'T' )
           
           # get the size of the current file
           datafile_stats = os.stat( fullpath )
           datafile_size = datafile_stats [stat.ST_SIZE] 
           
           current_year = aList[4]
           #print 'current_year: ' + current_year

           #dropFileName = instrument + '-' + current_year + '-' + visit_id + '-' + dataset_name + str( time.localtime() ) + '.xml'
           ni = 9
           nd = 4
           uniqueFileName = "%d.%0*d" % ( random.randint( 0, 10 ** ni - 1 ), nd, random.randint( 0, 10 ** nd - 1 ) );
           #str( gen_random_decimal( 10 ** 9 - 1, 10 ** 4 - 1 ) )
           uniqueFileName = uniqueFileName.replace( '.', '' )
           dropFileName = str( current_year ) + '-' + str( instrument ) + '-' + uniqueFileName + '.xml'

           #check if the file exists
           dropfilePath = os.path.join(dropDir, dropFileName)

           #print 'Creating the drop file ...'

           # create a new xml document
           newXml = xml.dom.minidom.Document()

           ####### dataset info ######
           icatAttribute = 'version="1.0 RC6" xsi:noNamespaceSchemaLocation="icatXSD.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
           icatElement = newXml.createElement( "icat" )
           icatElement.setAttribute( 'version', "1.0 RC6" )
           icatElement.setAttribute( 'xsi:noNamespaceSchemaLocation', "icatXSD.xsd" )
           icatElement.setAttribute( 'xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance" )
           studyElement = newXml.createElement( "study" )
           investigationElement = newXml.createElement( "investigation" )

           invNumberElement = newXml.createElement( "inv_number" )
           invNumberContent = newXml.createTextNode( str( inv_number ) )
           invNumberElement.appendChild( invNumberContent )


           visitIDElement = newXml.createElement( "visit_id" )
           visitIdContent = newXml.createTextNode( str( visit_id ) )
           visitIDElement.appendChild( visitIdContent )

           instrumentElement = newXml.createElement( "instrument" )
           instrumentContent = newXml.createTextNode( str( instrument ) )
           instrumentElement.appendChild( instrumentContent )

           titleElement = newXml.createElement( "title" )
           titleContent = newXml.createTextNode( str( title ) )
           titleElement.appendChild( titleContent )

           invTypeElement = newXml.createElement( "inv_type" )
           invTypeContent = newXml.createTextNode( str( inv_type ) )
           invTypeElement.appendChild( invTypeContent )

           datasetElement = newXml.createElement( "dataset" )

           datasetNameElement = newXml.createElement( "name" )
           datasetNameContent = newXml.createTextNode( str( dataset_name ) )
           datasetNameElement.appendChild( datasetNameContent )

           datasetTypeElement = newXml.createElement( "dataset_type" )
           datasetNameContent = newXml.createTextNode( str( dataset_type ) )
           datasetTypeElement.appendChild( datasetNameContent )

           datasetDescriptionElement = newXml.createElement( "description" )
           datasetDescriptionContent = newXml.createTextNode( str( dataset_description ) )
           datasetDescriptionElement.appendChild( datasetDescriptionContent )

           ####### datafile info ######
           datafileElement = newXml.createElement( "datafile" )

           datafileNameElement = newXml.createElement( "name" )
           datafileNameContent = newXml.createTextNode( str( datafile_name ) )
           datafileNameElement.appendChild( datafileNameContent )

           locationElement = newXml.createElement( "location" )
           #print '\n================================'
           locationContent = newXml.createTextNode( str( datafile_location ) )
           print str( datafile_location )
           #print '\n================================'
           locationElement.appendChild( locationContent )

           datafileDescriptionElement = newXml.createElement( "description" )
           datafileDescriptionContent = newXml.createTextNode( str( datafile_description ) )
           datafileDescriptionElement.appendChild( datafileDescriptionContent )

           datafileVersionElement = newXml.createElement( "datafile_version" )
           datafileVersionContent = newXml.createTextNode( str( datafile_version ) )
           datafileVersionElement.appendChild( datafileVersionContent )

           datafileCreationTimeElement = newXml.createElement( "datafile_create_time" )
           datafileCreationTimeContent = newXml.createTextNode( str( datafile_creation_time ) )
           datafileCreationTimeElement.appendChild( datafileCreationTimeContent )

           datafileModifyTimeElement = newXml.createElement( "datafile_modify_time" )
           datafileModifyTimeContent = newXml.createTextNode( str( datafile_modification_time ) )
           datafileModifyTimeElement.appendChild( datafileModifyTimeContent )
           
           datafileSizeElement = newXml.createElement( "file_size" )
           datafileSizeContent = newXml.createTextNode( str( datafile_size ) )
           datafileSizeElement.appendChild( datafileSizeContent )

           # appending the elements to each other
           datafileElement.appendChild( datafileNameElement )
           datafileElement.appendChild( locationElement )
           datafileElement.appendChild( datafileDescriptionElement )
           datafileElement.appendChild( datafileVersionElement )
           datafileElement.appendChild( datafileCreationTimeElement )
           datafileElement.appendChild( datafileModifyTimeElement )
           datafileElement.appendChild( datafileSizeElement )

           datasetElement.appendChild( datasetNameElement )
           datasetElement.appendChild( datasetTypeElement )
           datasetElement.appendChild( datasetDescriptionElement )
           datasetElement.appendChild( datafileElement )

           investigationElement.appendChild( invNumberElement )
           investigationElement.appendChild( visitIDElement )
           investigationElement.appendChild( instrumentElement )
           investigationElement.appendChild( titleElement )
           investigationElement.appendChild( invTypeElement )
           investigationElement.appendChild( datasetElement )

           studyElement.appendChild( investigationElement )
           icatElement.appendChild( studyElement )

           newXml.appendChild( icatElement )

           try:
               # first save the output xml in a temporary location before being formatted and saved to the final location
               tmpfilepath = dropfilePath + '.tmp'
               fileHandle = open ( tmpfilepath, 'w' )

               #newXml.normalize()
               newXml = newXml.toxml()

               fileHandle.write( newXml )
               fileHandle.close()

               # use xml_pp command to pretty print xml output
               #print dropfilePath
               os.system('xml_pp '+tmpfilepath+ ' > '+dropfilePath)
               
               if (os.path.getsize(dropfilePath) == 0):
                   print '\nsize of '+str(dropfilePath)+' is ZERO'
                   print '\nfullpath= '+str(fullpath)
               
               # remove the temporary file *.tmp
               os.system( 'rm ' + tmpfilepath )

               #if ( dataset_name <> 'topdir' ):
                   #print dataset_name
                   #print datafile_location
                   #print dropFileName
                   #print(\n)
           except:
               print 'problem saving xml data into ' + str( dropFileName )
       else: # not a file
           print fullpath + ' is not a file.'


   end = time.time()
   print '\nExecution time for generating ' + str( nbFiles ) + ' files is: ' + secondsToStr( end - start )
    
if __name__=="__main__":
    maketapearchivelist(sys.argv)


