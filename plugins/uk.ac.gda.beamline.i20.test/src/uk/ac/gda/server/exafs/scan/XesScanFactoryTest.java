/*-
 * Copyright © 2014 Diamond Light Source Ltd.
 *
 * This file is part of GDA.
 *
 * GDA is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License version 3 as published by the Free
 * Software Foundation.
 *
 * GDA is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along
 * with GDA. If not, see <http://www.gnu.org/licenses/>.
 */

package uk.ac.gda.server.exafs.scan;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import gda.data.metadata.NXMetaDataProvider;
import gda.device.Scannable;
import gda.jython.scriptcontroller.logging.LoggingScriptController;

public class XesScanFactoryTest {

	private BeamlinePreparer beamlinePreparer;
	private DetectorPreparer detectorPreparer;
	private OutputPreparer outputPreparer;
	private SampleEnvironmentPreparer samplePreparer;
	private LoggingScriptController loggingScriptController;
	private Scannable energyScannable;
	private NXMetaDataProvider metashop;
	private Scannable xesEnergyScannable;
	private Scannable analyserAngle;

	@Before
	public void setup() {
		// mock all the objects which would be used to create the XasScan objects

		// have not mocked ArrayList<AsciiMetadataConfig> original_header
		beamlinePreparer = Mockito.mock(BeamlinePreparer.class);
		detectorPreparer = Mockito.mock(DetectorPreparer.class);
		samplePreparer = Mockito.mock(SampleEnvironmentPreparer.class);
		outputPreparer = Mockito.mock(OutputPreparer.class);
		loggingScriptController = Mockito.mock(LoggingScriptController.class);
		energyScannable = Mockito.mock(Scannable.class);
		xesEnergyScannable = Mockito.mock(Scannable.class);
		analyserAngle = Mockito.mock(Scannable.class);
		metashop = Mockito.mock(NXMetaDataProvider.class);

	}

	@Test
	public void testCanCreateEnergyScan() {

		XesScanFactory theFactory = new XesScanFactory();

		theFactory.setBeamlinePreparer(beamlinePreparer);
		theFactory.setDetectorPreparer(detectorPreparer);
		theFactory.setSamplePreparer(samplePreparer);
		theFactory.setOutputPreparer(outputPreparer);
		theFactory.setLoggingScriptController(loggingScriptController);
		theFactory.setEnergyScannable(energyScannable);
		theFactory.setMetashop(metashop);
		theFactory.setIncludeSampleNameInNexusName(true);
		theFactory.setScanName("xesscan");
		theFactory.setXes_energy(xesEnergyScannable);
		theFactory.setAnalyserAngle(analyserAngle);

		EnergyScan energyScan = theFactory.createEnergyScan();

		if (energyScan == null) {
			Assert.fail("Null returned from factory");
		}

		XesScan xesscan = theFactory.createXesScan();

		if (xesscan == null) {
			Assert.fail("Null returned from factory");
		}

	}

	@Test
	public void testXesScanMissingEnergy() {
		XesScanFactory theFactory = new XesScanFactory();

		theFactory.setBeamlinePreparer(beamlinePreparer);
		theFactory.setDetectorPreparer(detectorPreparer);
		theFactory.setSamplePreparer(samplePreparer);
		theFactory.setOutputPreparer(outputPreparer);
		theFactory.setLoggingScriptController(loggingScriptController);
		theFactory.setEnergyScannable(energyScannable);
		theFactory.setMetashop(metashop);
		theFactory.setIncludeSampleNameInNexusName(true);
		theFactory.setScanName("xesscan");
		theFactory.setAnalyserAngle(analyserAngle);

		EnergyScan energyScan = theFactory.createEnergyScan();

		if (energyScan == null) {
			Assert.fail("Null returned from factory");
		}

		try {
			/* XesScan xesscan = */theFactory.createXesScan();
		} catch (Exception e1) {
			return;
		}
		Assert.fail("Expected exception was not caught.");
	}

	@Test
	public void testXesScanMissingAnalyser() {
		XesScanFactory theFactory = new XesScanFactory();

		theFactory.setBeamlinePreparer(beamlinePreparer);
		theFactory.setDetectorPreparer(detectorPreparer);
		theFactory.setSamplePreparer(samplePreparer);
		theFactory.setOutputPreparer(outputPreparer);
		theFactory.setLoggingScriptController(loggingScriptController);
		theFactory.setEnergyScannable(energyScannable);
		theFactory.setMetashop(metashop);
		theFactory.setIncludeSampleNameInNexusName(true);
		theFactory.setScanName("xesscan");
		theFactory.setXes_energy(xesEnergyScannable);

		EnergyScan energyScan = theFactory.createEnergyScan();

		if (energyScan == null) {
			Assert.fail("Null returned from factory");
		}

		try {
			/* XesScan xesscan = */theFactory.createXesScan();
		} catch (Exception e1) {
			return;
		}
		Assert.fail("Expected exception was not caught.");
	}

}
