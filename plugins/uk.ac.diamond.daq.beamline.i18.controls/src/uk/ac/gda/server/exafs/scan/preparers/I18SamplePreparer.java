package uk.ac.gda.server.exafs.scan.preparers;

import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.server.exafs.scan.SampleEnvironmentPreparer;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SamplePreparer implements SampleEnvironmentPreparer {

	private I18SampleParameters parameters;

	@Override
	public void configure(IScanParameters scanParameters, ISampleParameters parameters) throws Exception {
		this.parameters = (I18SampleParameters) parameters;
	}

	@Override
	public SampleEnvironmentIterator createIterator(String experimentType) {
		return new I18SampleEnvironmentIterator(parameters);
	}
}