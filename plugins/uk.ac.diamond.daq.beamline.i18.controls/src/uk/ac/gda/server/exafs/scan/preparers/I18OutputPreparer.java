package uk.ac.gda.server.exafs.scan.preparers;

import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.data.scan.datawriter.AsciiMetadataConfig;
import gda.device.DeviceException;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.QEXAFSParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;

public class I18OutputPreparer extends OutputPreparerBase {

	private I18SampleParameters sampleParameters;

	public I18OutputPreparer(AsciiDataWriterConfiguration datawriterconfig, NXMetaDataProvider metashop) {
		super(datawriterconfig, metashop);
	}


	@Override
	public void configure(IOutputParameters outputParameters, IScanParameters scanBean, IDetectorParameters detectorBean, ISampleParameters sampleParameters)
			throws DeviceException {
		super.configure(outputParameters, scanBean, detectorBean, sampleParameters);
		this.sampleParameters = (I18SampleParameters) sampleParameters;
	}

	@Override
	public AsciiDataWriterConfiguration getAsciiDataWriterConfig(IScanParameters scanBean) {
		// get the basic one from super
		AsciiDataWriterConfiguration datawriterconfig = super.getAsciiDataWriterConfig(scanBean).clone();

		// TODO if its xas, xanes, quick-xanes, then add the sample stage motor positions to the header
		if (scanBean instanceof XasScanParameters || scanBean instanceof XanesScanParameters || scanBean instanceof QEXAFSParameters){
			AsciiMetadataConfig xPosition = new AsciiMetadataConfig();
			xPosition.setLabel("X stage: " + sampleParameters.getSampleStageParameters().getX());
			datawriterconfig.getHeader().add(xPosition);

			AsciiMetadataConfig yPosition = new AsciiMetadataConfig();
			yPosition.setLabel("Y stage: " + sampleParameters.getSampleStageParameters().getY());
			datawriterconfig.getHeader().add(yPosition);

			AsciiMetadataConfig zPosition = new AsciiMetadataConfig();
			zPosition.setLabel("Z stage: " + sampleParameters.getSampleStageParameters().getZ());
			datawriterconfig.getHeader().add(zPosition);
		}



		return datawriterconfig;
	}
}