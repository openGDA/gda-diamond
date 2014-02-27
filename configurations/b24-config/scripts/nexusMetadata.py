import gda.data.scan.datawriter.NexusDataWriterMetadataTree

class NexusMetaData():
    def __init__( self ):
        self.NTree = gda.data.scan.datawriter.NexusDataWriterMetadataTree()
        self.metadataScannables = self.NTree.getMetadatascannables()
        self.metadataPaths = self.NTree.getLocationmap()

    def __str__( self ):
        output = []
        for scannableName in self.metadataScannables:
            line = scannableName.ljust( 15, ' ' )
            firstLine = True
            for path in self.metadataPaths[ scannableName ].getPaths():
                line += (' ' * 15 if not firstLine else '') + ' : ' + path
                firstLine = False
                output.append( line )
                line = ""
        return '\n'.join( output )

    def __repr__( self ):
        output = {}
        for scannableName in self.metadataScannables:
            output[ scannableName ] = [ x for x in self.metadataPaths[ scannableName ].getPaths() ]
        return output.__repr__()

    def addScannablePaths( self, scannable, paths, units ):
        scannableWriter = constructScannableWriter( paths, units )
        self.addScannableWriter( scannable, scannableWriter )

    def addScannableWriter( self, scannable, scannableWriter ):
        self.metadataScannables.add( scannable.name )
        self.metadataPaths.put( scannable.name, scannableWriter )

    def removeScannable( self, scannable ):
        scannableName = scannable.name if hasattr( scannable, 'name' ) else scannable
        self.metadataPaths.remove( scannableName )
        self.metadataScannables.remove( scannableName )


def constructScannableWriter( paths, units ):
    entry = gda.data.scan.datawriter.scannablewriter.SingleScannableWriter()
    entry.setPaths( paths )
    entry.setUnits( units )
    return entry
