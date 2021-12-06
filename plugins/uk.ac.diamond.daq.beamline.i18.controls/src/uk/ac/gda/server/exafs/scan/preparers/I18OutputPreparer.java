package uk.ac.gda.server.exafs.scan.preparers;

import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.data.scan.datawriter.AsciiMetadataConfig;
import gda.device.DeviceException;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.ScannableConfiguration;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;

public class I18OutputPreparer extends OutputPreparerBase {

	private I18SampleParameters sampleParameters;

	public I18OutputPreparer(AsciiDataWriterConfiguration datawriterconfig, NXMetaDataProvider metashop) {
		super(datawriterconfig, metashop);
	}

	@Override
	public void configure(IOutputParameters outputParameters, IScanParameters scanBean,
			IDetectorParameters detectorBean, ISampleParameters sampleParameters) throws DeviceException {
		super.configure(outputParameters, scanBean, detectorBean, sampleParameters);
		this.sampleParameters = (I18SampleParameters) sampleParameters;
	}

	@Override
	public AsciiDataWriterConfiguration getAsciiDataWriterConfig(IScanParameters scanBean) {
		// get the basic one from super
		AsciiDataWriterConfiguration datawriterconfig = super.getAsciiDataWriterConfig(scanBean).clone();

		// print scannable configurations
		sampleParameters.getScannableConfigurations().stream()
			.map(this::toAsciiMetadataConfig).forEach(datawriterconfig.getHeader()::add);

		return datawriterconfig;
	}

	private AsciiMetadataConfig toAsciiMetadataConfig(ScannableConfiguration configuration) {
		var metadata = new AsciiMetadataConfig();
		metadata.setLabel(configuration.getScannableName() + ": " + configuration.getPosition());
		return metadata;
	}
}