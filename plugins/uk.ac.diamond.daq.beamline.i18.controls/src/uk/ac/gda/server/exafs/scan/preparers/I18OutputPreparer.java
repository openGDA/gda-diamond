package uk.ac.gda.server.exafs.scan.preparers;

import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.data.scan.datawriter.AsciiMetadataConfig;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.QEXAFSParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;

public class I18OutputPreparer extends OutputPreparerBase {

	public I18OutputPreparer(AsciiDataWriterConfiguration datawriterconfig, NXMetaDataProvider metashop) {
		super(datawriterconfig, metashop);
	}

	@Override
	public AsciiDataWriterConfiguration getAsciiDataWriterConfig(IScanParameters scanBean) {
		// get the basic one from super
		AsciiDataWriterConfiguration datawriterconfig = super.getAsciiDataWriterConfig(scanBean).clone();

		// if its xas, xanes, quick-xanes, then add the sample stage motor positions to the header
		if (scanBean instanceof XasScanParameters || scanBean instanceof XanesScanParameters || scanBean instanceof QEXAFSParameters){
			var xPosition = new AsciiMetadataConfig();
			xPosition.setLabel("X stage");
			datawriterconfig.getHeader().add(xPosition);

			var yPosition = new AsciiMetadataConfig();
			yPosition.setLabel("Y stage");
			datawriterconfig.getHeader().add(yPosition);
		}

		// always add the Z position
		var zPosition = new AsciiMetadataConfig();
		zPosition.setLabel("Z stage");
		datawriterconfig.getHeader().add(zPosition);

		return datawriterconfig;
	}
}