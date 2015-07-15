package uk.ac.gda.server.exafs.scan.preparers;

import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.gui.RCPController;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.server.exafs.scan.SampleEnvironmentPreparer;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SamplePreparer implements SampleEnvironmentPreparer {

	private final RCPController rcpController;
	private final Scannable sc_MicroFocusSampleX;
	private final Scannable sc_MicroFocusSampleY;
	private final Scannable sc_sample_z;
	private final EnumPositioner d7a;
	private final EnumPositioner d7b;
	private final Scannable kb_vfm_x;

	private I18SampleParameters parameters;
	private IScanParameters scanParameters;

	public I18SamplePreparer(RCPController rcpController, Scannable sc_MicroFocusSampleX,
			Scannable sc_MicroFocusSampleY, Scannable sc_sample_z, EnumPositioner D7A, EnumPositioner D7B,
			Scannable kb_vfm_x) {
		this.rcpController = rcpController;
		this.sc_MicroFocusSampleX = sc_MicroFocusSampleX;
		this.sc_MicroFocusSampleY = sc_MicroFocusSampleY;
		this.sc_sample_z = sc_sample_z;
		d7a = D7A;
		d7b = D7B;
		this.kb_vfm_x = kb_vfm_x;
	}

	@Override
	public void configure(IScanParameters scanParameters, ISampleParameters parameters) throws Exception {
		this.scanParameters = scanParameters;
		this.parameters = (I18SampleParameters) parameters;
	}

	@Override
	public SampleEnvironmentIterator createIterator(String experimentType) {
		return new I18SampleEnvironmentIterator(scanParameters, parameters, rcpController, sc_MicroFocusSampleX,
				sc_MicroFocusSampleY, sc_sample_z, d7a, d7b,
				kb_vfm_x);
	}
}