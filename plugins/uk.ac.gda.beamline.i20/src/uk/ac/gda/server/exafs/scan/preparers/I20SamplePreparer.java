package uk.ac.gda.server.exafs.scan.preparers;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.device.scannable.Lakeshore340Scannable;
import gda.gui.RCPController;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.server.exafs.scan.SampleEnvironmentPreparer;
import uk.ac.gda.server.exafs.scan.iterators.I20CryostatIterator;
import uk.ac.gda.server.exafs.scan.iterators.I20RoomTempIterator;
import uk.ac.gda.server.exafs.scan.iterators.I20SingleSampleIterator;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;
import uk.ac.gda.server.exafs.scan.iterators.XESRoomTempIterator;

public class I20SamplePreparer implements SampleEnvironmentPreparer {

	private Scannable sample_x;
	private Scannable sample_y;
	private Scannable sample_z;
	private Scannable sample_rot;
	private Scannable sample_fine_rot;
	private Scannable sample_roll;
	private Scannable sample_pitch;
	private EnumPositioner filterwheel;
	private Lakeshore340Scannable cryostat;
	private Scannable cryostick_pos;
	private RCPController rcp_controller;
	private I20SampleParameters i20SampleParams;

	public I20SamplePreparer(Scannable sample_x, Scannable sample_y, Scannable sample_z, Scannable sample_rot,
			Scannable sample_fine_rot, Scannable sample_roll, Scannable sample_pitch, EnumPositioner filterwheel,
			Lakeshore340Scannable cryostat, Scannable cryostick_pos, RCPController rcp_controller) {
		this.sample_x = sample_x;
		this.sample_y = sample_y;
		this.sample_z = sample_z;
		this.sample_rot = sample_rot;
		this.sample_fine_rot = sample_fine_rot;
		this.sample_roll = sample_roll;
		this.sample_pitch = sample_pitch;
		this.filterwheel = filterwheel;
		this.cryostat = cryostat;
		this.cryostick_pos = cryostick_pos;
		this.rcp_controller = rcp_controller;
	}

	@Override
	public void configure(IScanParameters scanParameters, ISampleParameters sampleParameters) throws Exception {
		// print "Opening Plotting Perspective"
		rcp_controller.openPerspective("org.diamond.exafs.ui.PlottingPerspective");

		i20SampleParams = (I20SampleParameters) sampleParameters;

		// TODO is it correct to perform this move at this point?
		if (i20SampleParams.getUseSampleWheel()) {
			_moveSampleWheel();
		}
	}

	@Override
	public SampleEnvironmentIterator createIterator(String experimentType) {

		// ?print "experiment type=", experiment_type
		String sample_environment = i20SampleParams.getSampleEnvironment();
		// print "sample environment",sample_environment
		if (!experimentType.equals("XES") && sample_environment.equals(I20SampleParameters.SAMPLE_ENV[1])) {
			SampleEnvironmentIterator iterator = new I20RoomTempIterator(i20SampleParams, sample_x, sample_y, sample_z,
					sample_rot, sample_roll, sample_pitch);
			return iterator;
		}
		// # XES room temp sample stage
		else if (experimentType.equals("XES") && sample_environment.equals(I20SampleParameters.SAMPLE_ENV[1])) {
			SampleEnvironmentIterator iterator = new XESRoomTempIterator(i20SampleParams, sample_x, sample_y, sample_z,
					sample_rot, sample_fine_rot);
			return iterator;
		}
		// #XAS/XANES cryostat
		else if (!experimentType.equals("XES") && sample_environment.equals(I20SampleParameters.SAMPLE_ENV[2])) {
			I20CryostatIterator iterator = new I20CryostatIterator(i20SampleParams, cryostat, cryostick_pos);
			return iterator;
		}
		SampleEnvironmentIterator iterator = new I20SingleSampleIterator(i20SampleParams);
		return iterator;

	}

	private void _moveSampleWheel() throws DeviceException {
		String filter_position = i20SampleParams.getSampleWheelPosition();
		// String message = "Setting reference filter wheel to " + filter_position;
		// logger.info(message);
		// print message
		filterwheel.moveTo(filter_position);
	}
}
