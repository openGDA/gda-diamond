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

package uk.ac.gda.server.exafs.scan.preparers;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.Vector;

import org.junit.Before;
import org.junit.Test;

import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.scannable.DummyScannable;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServer;
import gda.jython.JythonServerFacade;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.Xspress3FFoverI0BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.fullCalculations.Xspress3WithFullCalculationsDetector;

public class I18DetectorPreparerTest {

	private Scannable[] sensitivities;
	private Scannable[] sensitivityUnits;
	private Xspress3WithFullCalculationsDetector xspress3;
	private TfgScalerWithFrames ionchambers;
	private I18DetectorPreparer thePreparer;
	private BufferedDetector qexafs_counterTimer01;
	private Xspress3BufferedDetector qexafs_xspress3;
	private Xspress3FFoverI0BufferedDetector qexafs_FFI0_xspress3;

	@Before
	public void setup() {

		JythonServerFacade jythonserverfacade = mock(JythonServerFacade.class);
		InterfaceProvider.setTerminalPrinterForTesting(jythonserverfacade);
		InterfaceProvider.setAuthorisationHolderForTesting(jythonserverfacade);

		JythonServer jythonserver = mock(JythonServer.class);
		InterfaceProvider.setDefaultScannableProviderForTesting(jythonserver);
		InterfaceProvider.setCurrentScanInformationHolderForTesting(jythonserver);
		InterfaceProvider.setJythonServerNotiferForTesting(jythonserver);
		when(jythonserver.getDefaultScannables()).thenReturn(new Vector<Scannable>());

		xspress3 = createMock(Xspress3WithFullCalculationsDetector.class, "xspress3");
		ionchambers = createMock(TfgScalerWithFrames.class, "ionchambers");
		qexafs_counterTimer01 = createMock(BufferedDetector.class, "qexafs_counterTimer01");
		qexafs_xspress3 = createMock(Xspress3BufferedDetector.class, "qexafs_xspress3");
		qexafs_FFI0_xspress3 = createMock(Xspress3FFoverI0BufferedDetector.class, "qexafs_FFI0_xspress3");

		sensitivities = new Scannable[3];
		sensitivities[0] = createMockScannable("i0_keithley_gain");
		sensitivities[1] = createMockScannable("it_keithley_gain");
		sensitivityUnits = new Scannable[] {createMockScannable("i0units"), createMockScannable("itunits")};

		thePreparer = new I18DetectorPreparer(sensitivities, sensitivityUnits, ionchambers,
				xspress3, qexafs_counterTimer01, qexafs_xspress3, qexafs_FFI0_xspress3);
	}

	private Scannable createMockScannable(String string) {
		return createMock(DummyScannable.class, string);
	}

	private <T extends Scannable> T createMock(Class<T> clazz, String name) {
		T newMock = mock(clazz);
		when(newMock.getName()).thenReturn(name);
		return newMock;
	}

	@Test
	public void testFluoDetectors() throws Exception {
		Set<IonChamberParameters> ionParamsSet = makeIonChamberParameters();

		FluorescenceParameters fluoParams = new FluorescenceParameters();
		fluoParams.setCollectDiffractionImages(false);
		for (IonChamberParameters params : ionParamsSet) {
			fluoParams.addIonChamberParameter(params);
		}

		fluoParams.setConfigFileName("Fluo_config.xml");
		fluoParams.setDetectorType(FluorescenceParameters.GERMANIUM_DET_TYPE);

		DetectorParameters detParams = new DetectorParameters();
		detParams.setFluorescenceParameters(fluoParams);
		detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

		thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");

		verifyNoInteractions(xspress3);

		fluoParams.setDetectorType(FluorescenceParameters.XSPRESS3_DET_TYPE);
		thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");
		verify(xspress3).setConfigFileName(
				"/scratch/test/xml/path/Fluo_config.xml");
		verify(xspress3).loadConfigurationFromFile();
	}

	@Test
	public void testFluoTimes() throws Exception {
		Region region = new Region();
		region.setEnergy(7000.0);
		region.setStep(3.0);
		region.setTime(1.0);

		XanesScanParameters xanesParams = new XanesScanParameters();
		xanesParams.setEdge("K");
		xanesParams.setElement("Fe");
		xanesParams.addRegion(region);
		xanesParams.setFinalEnergy(7021.0);

		Set<IonChamberParameters> ionParamsSet = makeIonChamberParameters();

		TransmissionParameters transParams = new TransmissionParameters();
		transParams.setCollectDiffractionImages(false);
		for (IonChamberParameters params : ionParamsSet) {
			transParams.addIonChamberParameter(params);
		}

		DetectorParameters detParams = new DetectorParameters();
		detParams.setTransmissionParameters(transParams);
		detParams.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

		thePreparer.configure(xanesParams, detParams, null,
				"/scratch/test/xml/path");
		thePreparer.beforeEachRepetition();

		verify(ionchambers).setTimes(new Double[] { 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0 });
	}

	private Set<IonChamberParameters> makeIonChamberParameters() {
		IonChamberParameters ionParams = new IonChamberParameters();
		ionParams.setChangeSensitivity(true);
		ionParams.setAutoFillGas(true);
		ionParams.setName("I0");
		ionParams.setDeviceName("counterTimer01");
		ionParams.setGain("1 nA/V");
		ionParams.setOffset("1 pA");
		ionParams.setGasType("Ar");
		ionParams.setPercentAbsorption(15.0);
		ionParams.setTotalPressure(1.1);
		ionParams.setPressure(99.63);
		ionParams.setGas_fill1_period_box(200.0);
		ionParams.setGas_fill2_period_box(200.0);

		IonChamberParameters ionParamsOff = new IonChamberParameters();
		ionParamsOff.setChangeSensitivity(false);
		ionParamsOff.setAutoFillGas(false);

		LinkedHashSet<IonChamberParameters> set = new LinkedHashSet<IonChamberParameters>();
		set.add(ionParams);
		set.add(ionParamsOff);

		return set;

	}

	@Test
	public void testIonChambers() throws Exception {
		Set<IonChamberParameters> ionParamsSet = makeIonChamberParameters();

		TransmissionParameters transParams = new TransmissionParameters();
		transParams.setCollectDiffractionImages(false);
		for (IonChamberParameters params : ionParamsSet) {
			transParams.addIonChamberParameter(params);
		}

		DetectorParameters detParams = new DetectorParameters();
		detParams.setTransmissionParameters(transParams);
		detParams.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

		thePreparer.configure(null, detParams, null, "/scratch/test/xml/path");

		verify(sensitivities[0]).moveTo("1");
		verify(sensitivityUnits[0]).moveTo("nA/V");
	}

}
