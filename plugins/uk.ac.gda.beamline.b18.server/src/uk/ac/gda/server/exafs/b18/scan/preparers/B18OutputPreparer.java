package uk.ac.gda.server.exafs.b18.scan.preparers;

import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import uk.ac.gda.server.exafs.scan.preparers.OutputPreparerBase;

public class B18OutputPreparer extends OutputPreparerBase {

	public B18OutputPreparer(AsciiDataWriterConfiguration datawriterconfig, NXMetaDataProvider metashop) {
		super(datawriterconfig, metashop);
	}
}