/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package gda.scan;

import static org.junit.Assert.assertEquals;

import org.junit.Before;
import org.junit.Test;

import gda.device.DeviceException;
import gda.device.detector.BufferedDetector;
import gda.device.detector.DummyDAServer;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.memory.Scaler;
import gda.device.motor.DummyMotor;
import gda.device.scannable.TurboXasScannable;
import gda.device.timer.Etfg;
import gda.device.zebra.controller.Zebra;
import gda.device.zebra.controller.impl.ZebraDummy;

public class TurboXasScanTest extends EdeTestBase {

	private DummyDAServer daserver;
	private Etfg tfg;
	private Scaler memory;
	private BufferedScaler bufferedScaler;
	private TurboXasScannable turboXasScannable;

	@Before
	public void setupEnvironment() throws Exception {
		daserver = new DummyDAServer();
		daserver.configure();

		tfg = new Etfg();
		tfg.setDaServer(daserver);
		tfg.configure();

		memory = new Scaler();
		memory.setDaServer(daserver);
		memory.setHeight(1);
		memory.setWidth(4);
		memory.setOpenCommand("tfg open-cc");
		memory.configure();

		bufferedScaler = new BufferedScaler();
		bufferedScaler.setName("bufferedScaler");
		bufferedScaler.setScaler(memory);
		bufferedScaler.setTimer(tfg);
		bufferedScaler.setDaserver(daserver);
		bufferedScaler.setTFGv2(true);
		bufferedScaler.setOutputLogValues(false);
		bufferedScaler.setTimeChannelRequired(true);
		bufferedScaler.setExtraNames(new String[] { "time", "I0", "It", "Iref" });
		bufferedScaler.setFirstDataChannel(0);
		bufferedScaler.setNumChannelsToRead(3);
		bufferedScaler.setOutputFormat(new String[] { "%.5g", "%.5g", "%.5g", "%.5g", "%.5g" });
		bufferedScaler.configure();

		Zebra dummyZebra = new ZebraDummy();
		DummyMotor dummyMotor = new DummyMotor();
		dummyMotor.setName("dummyMotor");
		dummyMotor.setMinPosition(-10000);
		dummyMotor.setMaxPosition(10000);
		dummyMotor.setPosition(0);
		dummyMotor.configure();

		turboXasScannable = new TurboXasScannable();
		turboXasScannable.setName("turboXasScannable");
		turboXasScannable.setMotor(dummyMotor);
		turboXasScannable.setZebraDevice(dummyZebra);
	}

	@Test
	public void testScalerReadoutLength() throws DeviceException, InterruptedException {
		bufferedScaler.setCollectionTime(1.0);
		bufferedScaler.collectData();
		bufferedScaler.waitWhileBusy();
		double[] readoutValues = bufferedScaler.readout();
		int numChannels = bufferedScaler.getNumChannelsToRead();
		numChannels += bufferedScaler.isTimeChannelRequired() ? 1 : 0;
		assertEquals(readoutValues.length, numChannels);
	}

	@Test
	public void testTurboXasSingleSpectraContinuousScan() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasSingleSpectraContinuousScan");

		double startPos = 0;
		double endPos = 10;
		int numReadouts = 20;
		double timeForScan = 1;

		TurboXasScan scan = new TurboXasScan( turboXasScannable, startPos, endPos, numReadouts, timeForScan, new BufferedDetector[] {bufferedScaler} );
		scan.runScan();

		String nxsFile = scan.getDataWriter().getCurrentFileName();
		int[] expectedDims = new int[]{1, numReadouts};
		for(String name : bufferedScaler.getExtraNames()) {
			assertDimensions(nxsFile, bufferedScaler.getName(), name, expectedDims);
			checkDataValidRange(nxsFile, bufferedScaler.getName(), name, new RangeValidator(0, 1, true, false) );
		}
		assertDimensions(nxsFile, bufferedScaler.getName(), "frame_index", new int[]{numReadouts});
		assertDimensions(nxsFile, bufferedScaler.getName(), "energy", new int[]{numReadouts});
	}

	@Test
	public void testTurboXasScanMultipleSpectra() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasScanMultipleSpectra");

		TurboXasParameters parameters = new TurboXasParameters();
		parameters.setSampleName( "sample name" );
		parameters.setStartEnergy(0);
		parameters.setEndEnergy(10);
		parameters.setEnergyStep(0.01);
		// parameters.setEnergyCalibrationPolynomial("");
		// Set energy calibration polynomial to "" or null, so that position == energy

		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 0.10, 0.0, 5));
		parameters.addTimingGroup(new TurboSlitTimingGroup("group2", 0.10, 0.0, 7));

		int numPointsPerSpectrum = 1000;
		int numSpectra = 12;

		TurboXasMotorParameters motorParameters = parameters.getMotorParameters();
		motorParameters.setMotorParametersForTimingGroup(0);
		turboXasScannable.setMotorParameters(motorParameters);
		TurboXasScan scan = new TurboXasScan(turboXasScannable, motorParameters, new BufferedDetector[]{bufferedScaler});
		scan.runScan();

		String nxsFile = scan.getDataWriter().getCurrentFileName();

		// Check shape and content of scaler output (should be all >0 when not also producing lnI0It values)
		int[] expectedDims = new int[]{numSpectra, numPointsPerSpectrum};
		for(String name : bufferedScaler.getExtraNames()) {
			assertDimensions(nxsFile, bufferedScaler.getName(), name, expectedDims);
			checkDataValidRange(nxsFile, bufferedScaler.getName(), name, new RangeValidator(0, 1, true, false) );
		}
		// Test frame index and energy datasets
		assertDimensions(nxsFile, bufferedScaler.getName(), "frame_index", new int[]{numPointsPerSpectrum});
		assertDimensions(nxsFile, bufferedScaler.getName(), "energy", new int[]{numPointsPerSpectrum});
	}
}
