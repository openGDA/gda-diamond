package uk.ac.gda.server.exafs.scan.preparers;

import uk.ac.diamond.daq.server.rcpcontroller.RCPController;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.server.exafs.scan.SampleEnvironmentPreparer;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SamplePreparer implements SampleEnvironmentPreparer {

	private final RCPController rcpController;

	private I18SampleParameters parameters;
	private IScanParameters scanParameters;

	public I18SamplePreparer(RCPController rcpController) {
		this.rcpController = rcpController;
	}

	@Override
	public void configure(IScanParameters scanParameters, ISampleParameters parameters) throws Exception {
		this.scanParameters = scanParameters;
		this.parameters = (I18SampleParameters) parameters;
	}

	@Override
	public SampleEnvironmentIterator createIterator(String experimentType) {
		return new I18SampleEnvironmentIterator(scanParameters, parameters, rcpController);
	}
}