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
        name = scannable.name if hasattr( scannable, 'name' ) else scannable
        self.metadataScannables.add( name )
        self.metadataPaths.put( name, scannableWriter )

    def removeScannable( self, scannable ):
        scannableName = scannable.name if hasattr( scannable, 'name' ) else scannable
        self.metadataPaths.remove( scannableName )
        self.metadataScannables.remove( scannableName )

    def clear( self ):
        self.metadataPaths.clear()
        self.metadataScannables.clear()

    def resetToDefault( self ):
        self.clear()
        paths = [ 'instrument:NXinstrument/FEM:NXcollection/femX',
            'instrument:NXinstrument/FEM:NXcollection/femY',
            'instrument:NXinstrument/FEM:NXcollection/femYaw',
            'instrument:NXinstrument/FEM:NXcollection/femRoll',
            'instrument:NXinstrument/FEM:NXcollection/femPitch' ]
        units = [ 'mm', 'mm', 'deg', 'deg', 'deg' ]
        writer = gda.data.scan.datawriter.scannablewriter.SingleScannableWriter()
        writer.setPaths( paths )
        writer.setUnits( units )
        self.addScannableWriter( 'fem', writer )

def constructScannableWriter( paths, units ):
    entry = gda.data.scan.datawriter.scannablewriter.SingleScannableWriter()
    entry.setPaths( paths )
    entry.setUnits( units )
    return entry
