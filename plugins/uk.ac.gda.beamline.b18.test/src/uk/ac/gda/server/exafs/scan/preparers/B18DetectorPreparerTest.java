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

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.Vector;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.mythen.MythenDetectorImpl;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.DummyScannable;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServer;
import gda.jython.JythonServerFacade;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.OutputParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.devices.detector.xspress3.Xspress3Detector;
import uk.ac.gda.devices.detector.xspress3.controllerimpl.DummyXspress3Controller;
import uk.ac.gda.server.exafs.b18.scan.preparers.B18DetectorPreparer;

public class B18DetectorPreparerTest {

	private Scannable energy_scannable;
	private Scannable[] sensitivities;
	private Scannable[] sensitivity_units;
	private Scannable[] offsets;
	private Scannable[] offsets_units;
	private List<Scannable> ionc_gas_injector_scannables;
	private MythenDetectorImpl mythen_scannable;
	private Xspress2Detector xspressSystem;
	private Xmap vortexConfig;
	private Xspress3Detector xspress3Detector;
	private DummyXspress3Controller xspress3Controller;
	private TfgScalerWithFrames ionchambers;
	private B18DetectorPreparer thePreparer;

	@Before
	public void setup() throws DeviceException {

		JythonServerFacade jythonserverfacade = Mockito.mock(JythonServerFacade.class);
		InterfaceProvider.setTerminalPrinterForTesting(jythonserverfacade);
		InterfaceProvider.setAuthorisationHolderForTesting(jythonserverfacade);

		JythonServer jythonserver = Mockito.mock(JythonServer.class);
		InterfaceProvider.setDefaultScannableProviderForTesting(jythonserver);
		InterfaceProvider.setCurrentScanInformationHolderForTesting(jythonserver);
		InterfaceProvider.setJythonServerNotiferForTesting(jythonserver);
		Mockito.when(jythonserver.getDefaultScannables()).thenReturn(new Vector<Scannable>());

		mythen_scannable = (MythenDetectorImpl) createMock(MythenDetectorImpl.class, "mythen_scannable");
		Mockito.when(mythen_scannable.readout()).thenReturn("/scratch/test/xml/path/0001.dat");

		xspressSystem = (Xspress2Detector) createMock(Xspress2Detector.class, "xspressSystem");
		vortexConfig = (Xmap) createMock(Xmap.class, "vortexConfig");
		xspress3Detector = (Xspress3Detector) createMock(Xspress3Detector.class, "xspress3Config");
		xspress3Controller = Mockito.mock(DummyXspress3Controller.class);
		Mockito.when(xspress3Detector.getController()).thenReturn(xspress3Controller);

		ionchambers = (TfgScalerWithFrames) createMock(TfgScalerWithFrames.class, "ionchambers");

		energy_scannable = createMockScannable("energy_scannable");
		Mockito.when(energy_scannable.getPosition()).thenReturn(10000.0);

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

		ionc_gas_injector_scannables = new ArrayList<Scannable>();
		ionc_gas_injector_scannables.add(createMockScannable("I0_gas_injector"));
		ionc_gas_injector_scannables.add(createMockScannable("It_gas_injector"));
		ionc_gas_injector_scannables.add(createMockScannable("Iref_gas_injector"));

		thePreparer = new B18DetectorPreparer(energy_scannable, mythen_scannable, sensitivities, sensitivity_units,
				offsets, offsets_units, ionc_gas_injector_scannables, ionchambers, xspressSystem, vortexConfig,
				xspress3Detector);
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
		Mockito.when(newMock.getInputNames()).thenReturn(new String[]{name});
		Mockito.when(newMock.getExtraNames()).thenReturn(new String[]{});
		Mockito.when(newMock.getOutputFormat()).thenReturn(new String[]{"%.2f"});
		return newMock;
	}

	@Test
	public void testMythenScan(){
		try {
			TransmissionParameters transParams = new TransmissionParameters();
			transParams.setMythenEnergy(10000.0);
			transParams.setMythenTime(1.2);
			transParams.setCollectDiffractionImages(true);

			DetectorParameters detParams = new DetectorParameters();
			detParams.setTransmissionParameters(transParams);
			detParams.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

			OutputParameters outParams = new OutputParameters();
			outParams.setNexusDirectory("nexus");
			outParams.setAsciiDirectory("ascii");

			LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT,"DummyDataWriter");

			thePreparer.configure(null, detParams, outParams, "/scratch/test/xml/path/");
			thePreparer.collectMythenData();

			Mockito.verify(energy_scannable).moveTo(10000.0);
			Mockito.verify(mythen_scannable).setCollectionTime(1.2);
			Mockito.verify(mythen_scannable).setSubDirectory("path/mythen");

			Mockito.verify(mythen_scannable).collectData();
			Mockito.verify(mythen_scannable).readout();
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

	@Test
	public void testFluoDetectors() {
		try {
			Set<IonChamberParameters> ionParamsSet = makeIonChamberParameters();

			FluorescenceParameters fluoParams = new FluorescenceParameters();
			fluoParams.setCollectDiffractionImages(false);
			for (IonChamberParameters params : ionParamsSet){
				fluoParams.addIonChamberParameter(params);
			}

			fluoParams.setConfigFileName("Fluo_config.xml");
			fluoParams.setDetectorType("Germanium");

			DetectorParameters detParams = new DetectorParameters();
			detParams.setFluorescenceParameters(fluoParams);
			detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

			thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");

			Mockito.verify(xspressSystem).setConfigFileName("/scratch/test/xml/path/Fluo_config.xml");
			Mockito.verify(xspressSystem).reconfigure();

			Mockito.verifyZeroInteractions(vortexConfig);
			Mockito.verifyZeroInteractions(xspress3Detector);

			fluoParams.setDetectorType("Xspress3");
			thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");
			Mockito.verify(xspress3Detector).setConfigFileName("/scratch/test/xml/path/Fluo_config.xml");
			Mockito.verify(xspress3Detector).loadConfigurationFromFile();
			Mockito.verifyZeroInteractions(vortexConfig);

			fluoParams.setDetectorType("Silicon");
			thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");
			Mockito.verify(vortexConfig).setConfigFileName("/scratch/test/xml/path/Fluo_config.xml");
			Mockito.verify(vortexConfig).reconfigure();

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
			for (IonChamberParameters params : ionParamsSet){
				transParams.addIonChamberParameter(params);
			}

			DetectorParameters detParams = new DetectorParameters();
			detParams.setTransmissionParameters(transParams);
			detParams.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

			thePreparer.configure(xanesParams, detParams, null, "/scratch/test/xml/path/");
			thePreparer.beforeEachRepetition();

			Mockito.verify(ionchambers).setTimes(new Double[]{1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0});

		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

	private Set<IonChamberParameters> makeIonChamberParameters(){
		IonChamberParameters ionParams = new IonChamberParameters();
		ionParams.setChangeSensitivity(true);
		ionParams.setAutoFillGas(true);
		ionParams.setName("I0");
		ionParams.setDeviceName("counterTimer01");
		ionParams.setGain("1 nA/V");
		ionParams.setOffset("1 pA");
		ionParams.setGasType("He");
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
			for (IonChamberParameters params : ionParamsSet){
				transParams.addIonChamberParameter(params);
			}

			DetectorParameters detParams = new DetectorParameters();
			detParams.setTransmissionParameters(transParams);
			detParams.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

			thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");

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

			Mockito.verify(ionc_gas_injector_scannables.get(0)).moveTo(new Object[]{"25.0","120.0",99630.0,200.0,1100.0,200.0,"-1","false"});
			Mockito.verifyZeroInteractions(ionc_gas_injector_scannables.get(1));
			Mockito.verifyZeroInteractions(ionc_gas_injector_scannables.get(2));

		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

}
