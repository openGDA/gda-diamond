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

package gda.device.scannable;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.Assert.assertEquals;

import org.eclipse.dawnsci.nexus.appender.INexusFileAppenderService;
import org.eclipse.dawnsci.nexus.appender.impl.NexusFileAppenderService;
import org.eclipse.dawnsci.nexus.template.NexusTemplateService;
import org.eclipse.dawnsci.nexus.template.impl.NexusTemplateServiceImpl;
import org.eclipse.january.dataset.Dataset;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.mockito.InOrder;
import org.mockito.Mockito;

import gda.MockFactory;
import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.MotorException;
import gda.device.MotorStatus;
import gda.device.Scannable;
import gda.device.enumpositioner.ValvePosition;
import uk.ac.diamond.osgi.services.ServiceProvider;
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian;
import uk.ac.gda.beamline.i20.scannable.MonoMoveWithOffsetScannable;
import uk.ac.gda.beamline.i20.scannable.MonoOptimisation;
import uk.ac.gda.beamline.i20.scannable.ScannableGaussian;

/**
 * Unit tests for {@link MonoOptimisation} class.
 */
public class MonoOptimisationTest {

	private MonoOptimisation optimisation;
	private DummyScannableMotorWithExceptions offsetMotor;
	private Scannable braggMotor;
	private double area = 1.0;
	private final double centrePos = 0.1;
	private final double fwhm = 0.3;
	private double numericalTolerance = 1e-5;
	private final double lowMonoEnergy = 0;
	private final double highMonoEnergy = 5;
	private EnumPositioner photonShutter;
	private EnumPositioner diodePositioner;

	private static final String IN = "In";
	private static final String OUT = "Out";

	public void prepareScannables() {
		offsetMotor = new DummyScannableMotorWithExceptions();
		offsetMotor.setName("braggOffsetMotor");

		braggMotor = new DummyScannableMotor();
		braggMotor.setName("braggMotor");

		ScannableGaussian gaussianFunc = new ScannableGaussian("gauss1", centrePos, fwhm, area);
		gaussianFunc.setScannableToMonitorForPosition(offsetMotor);

		optimisation = new MonoOptimisation(offsetMotor, gaussianFunc);
		optimisation.setOffsetStart(-1);
		optimisation.setOffsetEnd(1);
		optimisation.setOffsetNumPoints(21);
		optimisation.setFitToPeakPointsOnly(true);
		optimisation.setBraggScannable(braggMotor);
		optimisation.setZeroBraggOffsetAfterFailure(false);

		photonShutter = createMock(EnumPositioner.class, "photonShutter");
		diodePositioner = createMock(EnumPositioner.class, "diodePositioner");

		optimisation.setPhotonShutter(photonShutter);
		optimisation.setDiagnosticPositioner(diodePositioner);
		optimisation.setUseDiagnosticDetector(false);
	}

	/**
	 * Dummy scannable that throws an exception a certain number of steps into a scan.
	 */
	private class DummyScannableMotorWithExceptions extends DummyScannableMotor {
		private int stepsBeforeThrowing;
		private int currentStepNumber;

		@Override
		public void asynchronousMoveTo(Object position) throws DeviceException {
			if (stepsBeforeThrowing > 0 && currentStepNumber > stepsBeforeThrowing) {
				throw new MotorException(MotorStatus.FAULT, "Random dummy motor fault");
			}
			currentStepNumber++;
			super.rawAsynchronousMoveTo(position);
		}

		@Override
		public void atScanStart() {
			currentStepNumber = 0;
		}

		@Override
		public void atCommandFailure() {
			currentStepNumber = 0;
		}

		@Override
		public void atScanEnd() {
			currentStepNumber = 0;
		}

		public void setStepsBeforeThrowing(int stepsBeforeThrowing) {
			this.stepsBeforeThrowing = stepsBeforeThrowing;
		}
	}

	private <T extends Scannable> T createMock(Class<T> clazz, String name) {
		T newMock = Mockito.mock(clazz);
		Mockito.when(newMock.getName()).thenReturn(name);
		return newMock;
	}

	@After
	public void tearDown() {
		ServiceProvider.reset();
	}

	@Before
	public void setup() {
		prepareScannables();
		LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusDataWriter");
		LocalProperties.set(LocalProperties.GDA_SCAN_CONCURRENTSCAN_READOUT_CONCURRENTLY, "false"); // default as interpreted by ConcurrentScan

		ServiceProvider.setService(INexusFileAppenderService.class, new NexusFileAppenderService());
		ServiceProvider.setService(NexusTemplateService.class, new NexusTemplateServiceImpl());
	}

	private void intialShutterPositions() throws DeviceException {
		photonShutter.moveTo(ValvePosition.CLOSE);
		diodePositioner.moveTo(IN);
	}

	@Test
	public void testMonoOptimisationCurveFittingIsAccurate() throws Exception {
		TestHelpers.setUpTest(MonoOptimisationTest.class, "testMonoOptimisationFitting", true);

		intialShutterPositions();

		optimisation.optimise(lowMonoEnergy, highMonoEnergy);

		// Check fitted width and position are within acceptable tolerance
		Gaussian gaussLow = optimisation.getFittedGaussianLowEnergy();
		Gaussian gaussHigh = optimisation.getFittedGaussianHighEnergy(); // should be same as gaussLow
		assertEquals(centrePos, gaussLow.getPosition(), numericalTolerance);
		assertEquals(fwhm, gaussLow.getFWHM(), 1e-2);
		assertEquals(centrePos, gaussHigh.getPosition(), numericalTolerance);
		assertEquals(fwhm, gaussHigh.getFWHM(), 1e-2);
	}

	@Test
	public void testMonoMovesInCorrectOrder() throws Exception {
		TestHelpers.setUpTest(MonoOptimisationTest.class, "testMonoMovesInCorrectOrder", true);
		Scannable mockBraggMotor = MockFactory.createMockScannable("mockBraggMotor");

		optimisation.setBraggScannable(mockBraggMotor);

		optimisation.optimise(lowMonoEnergy, highMonoEnergy);
		InOrder inorder = Mockito.inOrder(mockBraggMotor);
		// mono to the high energy position for offset scan
		inorder.verify(mockBraggMotor).moveTo(highMonoEnergy);
		// mono to the low energy position for the offset scan
		inorder.verify(mockBraggMotor).moveTo(lowMonoEnergy);
	}

	@Test
	public void testOffsetValuesAreCalculatedCorrectlyInMonoMoveScannable() throws Exception {
		TestHelpers.setUpTest(MonoOptimisationTest.class, "testOffsetValuesInMonoMoveScannable", true);

		// Run optimisation ...
		optimisation.optimise(lowMonoEnergy, highMonoEnergy);

		Gaussian gaussLow = optimisation.getFittedGaussianLowEnergy();
		Gaussian gaussHigh = optimisation.getFittedGaussianHighEnergy();
		// adjust position of high energy offset peak (so gradient > 0)
		gaussHigh.getParameter(0).setValue(0.5);

		// Create combined bragg and and offset scannable
		MonoMoveWithOffsetScannable braggWithOffset = new MonoMoveWithOffsetScannable("braggWithOffset", braggMotor, offsetMotor);
		// config. the offset parameters
		optimisation.configureOffsetParameters(braggWithOffset);

		// Check offset calculation is working correctly
		double midPos = 0.5*(lowMonoEnergy + highMonoEnergy);
		double midOffset = 0.5*(gaussLow.getPosition() + gaussHigh.getPosition());

		assertEquals(braggWithOffset.getOffsetForEnergy(lowMonoEnergy), gaussLow.getPosition(), numericalTolerance);
		assertEquals(braggWithOffset.getOffsetForEnergy(highMonoEnergy), gaussHigh.getPosition(), numericalTolerance);
		assertEquals(braggWithOffset.getOffsetForEnergy(midPos), midOffset, numericalTolerance);

		// Value of bragg and offset after motor move
		braggWithOffset.setAdjustBraggOffset(true);
		braggWithOffset.moveTo(midPos);
		braggWithOffset.setIncludeOffsetInPosition(true);
		Object[] pos = (Object [])braggWithOffset.getPosition();
		assertEquals(midPos, (double)pos[0], numericalTolerance);
		assertEquals(midOffset, (double)pos[1], numericalTolerance);
	}

	@Test
	public void testGoldenSectionSearchConvergesCorrectly() throws Exception {
		TestHelpers.setUpTest(MonoOptimisationTest.class, "testGoldenSectionSearchConvergesCorrectly", true);

		ScannableGaussian gaussianFunc = (ScannableGaussian) optimisation.getScannableToMonitor();
		double centre = 0;

		gaussianFunc.setParams(centre, fwhm, area);
		double bestX = MonoOptimisation.goldenSectionSearch(offsetMotor, gaussianFunc, centre-1.0, centre+1.0, 1e-10);
		assertEquals(centre, bestX, numericalTolerance);

		centre = 0.234;
		gaussianFunc.setParams(centre, fwhm, area);
		bestX = MonoOptimisation.goldenSectionSearch(offsetMotor, gaussianFunc, centre-1, centre+0.4, 1e-10);
		assertEquals(centre, bestX, numericalTolerance);
	}

	private class ScannableGaussianForTest extends ScannableGaussian {

		public ScannableGaussianForTest(String name, double centrePos, double fwhm, double area) {
			super(name, centrePos, fwhm, area);
		}

		@Override
		public Object getPosition() throws DeviceException {
			if( scannableForPosition != null )
				rawAsynchronousMoveTo(scannableForPosition.getPosition());

			return new double[]{gaussian.val(currentPos), gaussian.val(currentPos) };
		}
	}

	@Test
	public void testManualScanWorksOk() throws Exception {
		TestHelpers.setUpTest(MonoOptimisationTest.class, "testManualScanWorksOk", true);

		ScannableGaussian gaussianFunc = new ScannableGaussianForTest("gauss1", centrePos, fwhm, area);
		gaussianFunc.setScannableToMonitorForPosition(offsetMotor);

		optimisation.setScannableToMonitor(gaussianFunc);

		Dataset dataset = optimisation.doManualScan();
		// Check data dimensions are correct
		int[] shape = dataset.getShape();
		int numSteps = optimisation.getOffsetNumPoints();
		assertThat(shape[0], is(equalTo(numSteps)));
		assertThat(shape[1], is(equalTo(2)));

		// Check values are correct for each position
		for(int i = 0; i<numSteps; i++) {
			offsetMotor.moveTo(dataset.getObject(i,0));
			double[] pos = (double[])gaussianFunc.getPosition();
			assertEquals(pos[0], (double)dataset.getObject(i,1), numericalTolerance);
		}
	}

	@Test
	public void testPositionersForIonchambers() throws Exception {

		TestHelpers.setUpTest(MonoOptimisationTest.class, "testShuttersIonchambers", true);

		intialShutterPositions();

		optimisation.setUseDiagnosticDetector(false);
		optimisation.optimise(lowMonoEnergy, lowMonoEnergy);

		InOrder inorder = Mockito.inOrder(photonShutter, diodePositioner);

		// offset scan with ionchambers : photon shutter should be 'open' and diode must be 'out' for the scan
		inorder.verify(photonShutter).moveTo(ValvePosition.OPEN);
		inorder.verify(diodePositioner).moveTo(OUT);

		// diode position must be 'out' after the scan
		inorder.verify(diodePositioner).moveTo(OUT);
	}

	@Test
	public void testPositionersForDiode() throws Exception {

		TestHelpers.setUpTest(MonoOptimisationTest.class, "testShuttersDiagnostic", true);

		intialShutterPositions();

		optimisation.setUseDiagnosticDetector(true);
		optimisation.optimise(lowMonoEnergy, lowMonoEnergy);

		InOrder inorder = Mockito.inOrder(photonShutter, diodePositioner);

		// offset scan with diagnostic : photon shutter should be 'open' and diode must be 'out' for the scan
		inorder.verify(photonShutter).moveTo(ValvePosition.OPEN);
		inorder.verify(diodePositioner).moveTo(IN);

		// diode position must be 'out' after the scan
		inorder.verify(diodePositioner).moveTo(OUT);
	}

	@Test
	public void testBraggOffsetSetToZeroAfterFailure() throws Exception {
		TestHelpers.setUpTest(MonoOptimisationTest.class, "testBraggOffsetSetToZeroAfterFailure", true);

		optimisation.setZeroBraggOffsetAfterFailure(false);
		offsetMotor.setStepsBeforeThrowing(5);

		// This tests that exception is thrown correctly by the dummy motor
		try {
			optimisation.optimise(lowMonoEnergy, lowMonoEnergy);
		} catch(Exception e) {
			// catch exception thrown by motor, Bragg offset should be in last place it was moved to in the scan (i.e. -0.5)
			Double offsetPosition = ScannableUtils.objectToArray(offsetMotor.getPosition())[0];
			assertEquals(-0.5, offsetPosition, 1e-3);
		}

		// This tests that the offset is restored correctly.
		optimisation.setZeroBraggOffsetAfterFailure(true);
		try {
			optimisation.optimise(lowMonoEnergy, lowMonoEnergy);
		} catch(Exception e) {
			// catch exception thrown by motor, Bragg offset should be moved to zero
			Double offsetPosition = ScannableUtils.objectToArray(offsetMotor.getPosition())[0];
			assertEquals("Bragg offset position not set correctly after failed scan", 0.0, offsetPosition, 1e-3);
		}
	}


}
