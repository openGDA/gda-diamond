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

import static org.junit.Assert.assertThrows;

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
	private Scannable xesEnergyBoth;
	private Scannable xesEnergyGroup;
	private Scannable braggrGroup;

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
		xesEnergyBoth = Mockito.mock(Scannable.class);
		xesEnergyGroup = Mockito.mock(Scannable.class);
		braggrGroup = Mockito.mock(Scannable.class);
		metashop = Mockito.mock(NXMetaDataProvider.class);

	}

	private XesScanFactory createScanFactory() {
		XesScanFactory factory = new XesScanFactory();
		factory.setBeamlinePreparer(beamlinePreparer);
		factory.setDetectorPreparer(detectorPreparer);
		factory.setSamplePreparer(samplePreparer);
		factory.setOutputPreparer(outputPreparer);
		factory.setLoggingScriptController(loggingScriptController);
		factory.setMetashop(metashop);
		factory.setIncludeSampleNameInNexusName(true);
		factory.setScanName("xesscan");
		factory.setEnergyScannable(energyScannable);
		factory.setXesEnergyBoth(xesEnergyBoth);
		factory.setXesEnergyGroup(xesEnergyGroup);
		factory.setXesBraggGroup(braggrGroup);
		return factory;
	}

	@Test
	public void testCanCreateEnergyScan() {

		XesScanFactory theFactory = createScanFactory();

		EnergyScan energyScan = theFactory.createEnergyScan();
		Assert.assertNotNull("Null returned from createEnergyScan", energyScan);

		XesScan xesscan = theFactory.createXesScan();
		Assert.assertNotNull("Null returned from createXesScan", xesscan);
	}

	@Test
	public void testXesScanMissingEnergy() {
		XesScanFactory theFactory = createScanFactory();
		theFactory.setXesEnergyGroup(null); // set to null, so createXesScan fails

		EnergyScan energyScan = theFactory.createEnergyScan();
		Assert.assertNotNull("Null returned from createEnergyScan", energyScan);

		assertThrows(IllegalArgumentException.class, () -> theFactory.createXesScan());
	}

	@Test
	public void testXesScanMissingAnalyser() {
		XesScanFactory theFactory = createScanFactory();
		theFactory.setXesBraggGroup(null); // set to null, so createXesScan fails

		EnergyScan energyScan = theFactory.createEnergyScan();
		Assert.assertNotNull("Null returned from createEnergyScan", energyScan);

		assertThrows(IllegalArgumentException.class, () -> theFactory.createXesScan());
	}

}
