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

import static org.junit.Assert.fail;
import gda.device.Scannable;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.DummyScannable;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServer;
import gda.jython.JythonServerFacade;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.Vector;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;

import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;

public class I18DetectorPreparerTest {

	private Scannable[] sensitivities;
	private Scannable[] sensitivity_units;
	private Scannable[] offsets;
	private Scannable[] offsets_units;
	private Xspress2Detector xspressSystem;
	private Xmap xmpaMca;
	private TfgScalerWithFrames ionchambers;
	private I18DetectorPreparer thePreparer;

	@Before
	public void setup() {

		JythonServerFacade jythonserverfacade = Mockito.mock(JythonServerFacade.class);
		InterfaceProvider.setTerminalPrinterForTesting(jythonserverfacade);
		InterfaceProvider.setAuthorisationHolderForTesting(jythonserverfacade);

		JythonServer jythonserver = Mockito.mock(JythonServer.class);
		InterfaceProvider.setDefaultScannableProviderForTesting(jythonserver);
		InterfaceProvider.setCurrentScanInformationHolderForTesting(jythonserver);
		InterfaceProvider.setJythonServerNotiferForTesting(jythonserver);
		Mockito.when(jythonserver.getDefaultScannables()).thenReturn(new Vector<Scannable>());

		xspressSystem = (Xspress2Detector) createMock(Xspress2Detector.class, "xspressSystem");
		xmpaMca = (Xmap) createMock(Xmap.class, "xmpaMca");
		ionchambers = (TfgScalerWithFrames) createMock(TfgScalerWithFrames.class, "ionchambers");

		sensitivities = new Scannable[3];
		sensitivities[0] = createMockScannable("I0_sensitivity");
		sensitivities[1] = createMockScannable("It_sensitivity");
		sensitivities[2] = createMockScannable("Iref_sensitivity");

		sensitivity_units = new Scannable[3];
		sensitivity_units[0] = createMockScannable("I0_sensitivity_units");
		sensitivity_units[1] = createMockScannable("It_sensitivity_units");
		sensitivity_units[2] = createMockScannable("Iref_sensitivity_units");

		offsets = new Scannable[3];
		offsets[0] = createMockScannable("I0_offsets");
		offsets[1] = createMockScannable("It_offsets");
		offsets[2] = createMockScannable("Iref_offsets");

		offsets_units = new Scannable[3];
		offsets_units[0] = createMockScannable("I0_offsets_units");
		offsets_units[1] = createMockScannable("It_offsets_units");
		offsets_units[2] = createMockScannable("Iref_offsets_units");

		thePreparer = new I18DetectorPreparer(sensitivities, sensitivity_units, offsets, offsets_units, ionchambers,
				xspressSystem, xmpaMca);
	}

	private Scannable createMockScannable(String string) {
		// Scannable newMock = PowerMockito.mock(DummyScannable.class);
		// Mockito.when(newMock.getName()).thenReturn(string);
		// return newMock;
		return createMock(DummyScannable.class, string);
	}

	private Scannable createMock(Class<? extends Scannable> clazz, String name) {
		Scannable newMock = PowerMockito.mock(clazz);
		Mockito.when(newMock.getName()).thenReturn(name);
		return newMock;
	}

	@Test
	public void testFluoDetectors() {
		try {
			Set<IonChamberParameters> ionParamsSet = makeIonChamberParameters();

			FluorescenceParameters fluoParams = new FluorescenceParameters();
			fluoParams.setCollectDiffractionImages(false);
			for (IonChamberParameters params : ionParamsSet) {
				fluoParams.addIonChamberParameter(params);
			}

			fluoParams.setConfigFileName("Fluo_config.xml");
			fluoParams.setDetectorType("Germanium");

			DetectorParameters detParams = new DetectorParameters();
			detParams.setFluorescenceParameters(fluoParams);
			detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

			thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");

			Mockito.verify(xspressSystem).setConfigFileName("/scratch/test/xml/path/Fluo_config.xml");
			Mockito.verify(xspressSystem).configure();
			Mockito.verifyZeroInteractions(xmpaMca);

			fluoParams.setDetectorType("Silicon");
			thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");
			Mockito.verify(xmpaMca).setConfigFileName("/scratch/test/xml/path/Fluo_config.xml");
			Mockito.verify(xmpaMca).configure();

		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

	@Test
	public void testFluoTimes() {
		try {
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

			thePreparer.configure(xanesParams, detParams, null, "/scratch/test/xml/path");
			thePreparer.beforeEachRepetition();

			Mockito.verify(ionchambers).setTimes(new Double[] { 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0 });

		} catch (Exception e) {
			fail(e.getMessage());
		}
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
	public void testIonChambers() {
		try {
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

			Mockito.verify(sensitivities[0]).moveTo("1");
			Mockito.verify(sensitivity_units[0]).moveTo("nA/V");
			Mockito.verify(offsets[0]).moveTo("1");
			Mockito.verify(offsets_units[0]).moveTo("pA");
			Mockito.verifyZeroInteractions(sensitivities[1]);
			Mockito.verifyZeroInteractions(sensitivity_units[1]);
			Mockito.verifyZeroInteractions(offsets[1]);
			Mockito.verifyZeroInteractions(offsets_units[1]);
			Mockito.verifyZeroInteractions(sensitivities[2]);
			Mockito.verifyZeroInteractions(sensitivity_units[2]);
			Mockito.verifyZeroInteractions(offsets[2]);
			Mockito.verifyZeroInteractions(offsets_units[2]);

		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

}
