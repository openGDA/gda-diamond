package uk.ac.gda.server.exafs.b18.scan.preparers;

import gda.device.Scannable;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.b18.B18SampleParameters;
import uk.ac.gda.server.exafs.scan.SampleEnvironmentPreparer;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class B18SamplePreparer implements SampleEnvironmentPreparer {

	private final Scannable sxcryo_scannable;
	private final Scannable xytheta_scannable;
	private final Scannable ln2cryo_scannable;
	private final Scannable lakeshore_scannable;
	private final Scannable furnace_scannable;
	private final Scannable pulsetube_scannable;
	private final Scannable samplewheel_scannable;
	private final Scannable user_scannable;

	private B18SampleParameters parameters;
	private B18SampleEnvironmentIterator sampleEnvironmentIterator;

	public B18SamplePreparer(Scannable sxcryo_scannable, Scannable xytheta_scannable, Scannable ln2cryo_scannable,
			Scannable lakeshore_scannable, Scannable furnace_scannable, Scannable pulsetube_scannable,
			Scannable samplewheel_scannable, Scannable user_scannable) {

		this.sxcryo_scannable = sxcryo_scannable;
		this.xytheta_scannable = xytheta_scannable;
		this.ln2cryo_scannable = ln2cryo_scannable;
		this.lakeshore_scannable = lakeshore_scannable;
		this.furnace_scannable = furnace_scannable;
		this.pulsetube_scannable = pulsetube_scannable;
		this.samplewheel_scannable = samplewheel_scannable;
		this.user_scannable = user_scannable;
	}

	@Override
	public void configure(IScanParameters scanParameters, ISampleParameters parameters) throws Exception {
		this.parameters = (B18SampleParameters) parameters;
	}

	@Override
	public SampleEnvironmentIterator createIterator(String experimentType) {
		sampleEnvironmentIterator = new B18SampleEnvironmentIterator(parameters, sxcryo_scannable, xytheta_scannable, ln2cryo_scannable,
				lakeshore_scannable, furnace_scannable, pulsetube_scannable, samplewheel_scannable, user_scannable);
		return sampleEnvironmentIterator;
//		return new B18SampleEnvironmentIterator(parameters, sxcryo_scannable, xytheta_scannable, ln2cryo_scannable,
//				lakeshore_scannable, furnace_scannable, pulsetube_scannable, samplewheel_scannable, user_scannable);
	}

	public B18SampleEnvironmentIterator getCurrentSampleEnvironmentIterator() {
		return sampleEnvironmentIterator;
	}
}