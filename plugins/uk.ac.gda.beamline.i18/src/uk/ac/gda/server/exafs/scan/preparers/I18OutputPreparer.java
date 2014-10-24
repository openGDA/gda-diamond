package uk.ac.gda.server.exafs.scan.preparers;

import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import uk.ac.gda.server.exafs.scan.OutputPreparer;

public class I18OutputPreparer extends OutputPreparerBase implements OutputPreparer {

	public I18OutputPreparer(AsciiDataWriterConfiguration datawriterconfig, NXMetaDataProvider metashop) {
		super(datawriterconfig, metashop);
	}
}