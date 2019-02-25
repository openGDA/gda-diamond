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
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;

import org.eclipse.january.dataset.Dataset;
import org.junit.Before;
import org.junit.Test;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.Scannable;
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian;
import uk.ac.gda.beamline.i20.scannable.MonoMoveWithOffsetScannable;
import uk.ac.gda.beamline.i20.scannable.MonoOptimisation;
import uk.ac.gda.beamline.i20.scannable.ScannableGaussian;

/**
 * Unit tests for {@link MonoOptimisation} class.
 */
public class MonoOptimisationTest {

	private MonoOptimisation optimisation;
	private Scannable offsetMotor;
	private Scannable braggMotor;
	private double area = 1.0, centrePos = 0.1, fwhm = 0.3;
	private double numericalTolerance = 1e-5;

	public void prepareScannables() {
		offsetMotor = new DummyScannableMotor();
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
	}

	@Before
	public void setup() throws Exception {
		prepareScannables();
		LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusDataWriter");
		LocalProperties.set(LocalProperties.GDA_SCAN_CONCURRENTSCAN_READOUT_CONCURRENTLY, "false"); // default as interpreted by ConcurrentScan
	}

	@Test
	public void testMonoOptimisationCurveFittingIsAccurate() throws Exception {
		TestHelpers.setUpTest(MonoOptimisationTest.class, "testMonoOptimisationFitting", true);

		double lowEnergy = 0, highEnergy = 5;
		optimisation.setBraggScannable(braggMotor);
		optimisation.optimise(lowEnergy, highEnergy);

		// Check fitted width and position are within acceptable tolerance
		Gaussian gaussLow = optimisation.getFittedGaussianLowEnergy();
		Gaussian gaussHigh = optimisation.getFittedGaussianHighEnergy(); // should be same as gaussLow
		assertEquals(centrePos, gaussLow.getPosition(), numericalTolerance);
		assertEquals(fwhm, gaussLow.getFWHM(), 1e-2);
		assertEquals(centrePos, gaussHigh.getPosition(), numericalTolerance);
		assertEquals(fwhm, gaussHigh.getFWHM(), 1e-2);

		optimisation.setFitToPeakPointsOnly(true);
	}

	@Test
	public void testOffsetValuesAreCalculatedCorrectlyInMonoMoveScannable() throws Exception {
		TestHelpers.setUpTest(MonoOptimisationTest.class, "testOffsetValuesInMonoMoveScannable", true);

		// Run optimisation ...
		double lowEnergy = 0, highEnergy = 5;
		optimisation.setBraggScannable(braggMotor);
		optimisation.optimise(lowEnergy, highEnergy);

		Gaussian gaussLow = optimisation.getFittedGaussianLowEnergy();
		Gaussian gaussHigh = optimisation.getFittedGaussianHighEnergy();
		// adjust position of high energy offset peak (so gradient > 0)
		gaussHigh.getParameter(0).setValue(0.5);

		// Create combined bragg and and offset scannable
		MonoMoveWithOffsetScannable braggWithOffset = new MonoMoveWithOffsetScannable("braggWithOffset", braggMotor, offsetMotor);
		// config. the offset parameters
		optimisation.configureOffsetParameters(braggWithOffset);

		// Check offset calculation is working correctly
		double midPos = 0.5*(lowEnergy + highEnergy);
		double midOffset = 0.5*(gaussLow.getPosition() + gaussHigh.getPosition());

		assertEquals(braggWithOffset.getOffsetForEnergy(lowEnergy), gaussLow.getPosition(), numericalTolerance);
		assertEquals(braggWithOffset.getOffsetForEnergy(highEnergy), gaussHigh.getPosition(), numericalTolerance);
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
		double centre = 0, fwhm = 0.5, area = 1.0;

		gaussianFunc.setParams(centre, fwhm, area);
		double bestX = MonoOptimisation.goldenSectionSearch(offsetMotor, gaussianFunc, centre-1.0, centre+1.0, 1e-10);
		assertEquals(centre, bestX, numericalTolerance);

		centre = 0.234; fwhm = 0.1;
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



}
