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

import static org.junit.Assert.assertEquals;
import static org.mockito.ArgumentMatchers.any;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.mockito.ArgumentMatchers;
import org.mockito.MockedStatic;
import org.mockito.Mockito;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.Detector;
import gda.device.Scannable;
import gda.device.detector.DetectorBase;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.NexusXmap;
import gda.device.detector.xmap.NexusXmapFluorescenceDetectorAdapter;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.DummyScannable;
import gda.factory.Factory;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import uk.ac.gda.beans.exafs.DetectorConfig;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.OutputParameters;
import uk.ac.gda.beans.exafs.QEXAFSParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.vortex.VortexParameters;
import uk.ac.gda.beans.vortex.Xspress3Parameters;
import uk.ac.gda.beans.xspress.XspressParameters;
import uk.ac.gda.devices.detector.FluorescenceDetectorParameters;
import uk.ac.gda.devices.detector.xspress3.Xspress3Detector;
import uk.ac.gda.devices.detector.xspress3.controllerimpl.DummyXspress3Controller;
import uk.ac.gda.server.exafs.b18.scan.preparers.B18DetectorPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class B18DetectorPreparerTest {

	private Scannable energy_scannable;
	private Scannable[] sensitivities;
	private Scannable[] sensitivity_units;
	private Scannable[] offsets;
	private Scannable[] offsets_units;
	private List<Scannable> ionc_gas_injector_scannables;
	private DetectorBase diffractionDetector;
	private Xspress2Detector xspressDetector;
	private NexusXmap xmapMca;
	private Xspress3Detector xspress3Detector;
	private DummyXspress3Controller xspress3Controller;
	private TfgScalerWithFrames ionchambers;
	private B18DetectorPreparer thePreparer;
	private NexusXmapFluorescenceDetectorAdapter xmapFluoDetector;
	private Map<Detector, FluorescenceDetectorParameters> params;
	private MockedStatic<XMLHelpers> xmlHelpersMock;

	@Before
	public void setup() throws Exception {
		xmlHelpersMock = Mockito.mockStatic(XMLHelpers.class);
		diffractionDetector = createMock(DetectorBase.class, "diffractionDetector");
		Mockito.when(diffractionDetector.readout()).thenReturn("/scratch/test/xml/path/0001.dat");

		xspressDetector = createMock(Xspress2Detector.class, "xspressDetector");
		xmapMca = createMock(NexusXmap.class, "vortexConfig");

		xspress3Detector = createMock(Xspress3Detector.class, "xspress3Detector");
		xspress3Controller = Mockito.mock(DummyXspress3Controller.class);
		Mockito.when(xspress3Detector.getController()).thenReturn(xspress3Controller);

		xmapFluoDetector = Mockito.mock(NexusXmapFluorescenceDetectorAdapter.class);
		Mockito.when(xmapFluoDetector.getName()).thenReturn("xmapFluoDetector");
		Mockito.when(xmapFluoDetector.getXmap()).thenReturn(xmapMca);

		ionchambers = createMock(TfgScalerWithFrames.class, "ionchambers");

		energy_scannable = createMock("energy_scannable");
		Mockito.when(energy_scannable.getPosition()).thenReturn(10000.0);

		sensitivities = new Scannable[3];
		sensitivities[0] = createMock("I0_sensitivity");
		sensitivities[1] = createMock("It_sensitivity");
		sensitivities[2] = createMock("Iref_sensitivity");

		sensitivity_units = new Scannable[3];
		sensitivity_units[0] = createMock("I0_sensitivity_units");
		sensitivity_units[1] = createMock("It_sensitivity_units");
		sensitivity_units[2] = createMock("Iref_sensitivity_units");

		offsets = new Scannable[3];
		offsets[0] = createMock("I0_offsets");
		offsets[1] = createMock("It_offsets");
		offsets[2] = createMock("Iref_offsets");

		offsets_units = new Scannable[3];
		offsets_units[0] = createMock("I0_offsets_units");
		offsets_units[1] = createMock("It_offsets_units");
		offsets_units[2] = createMock("Iref_offsets_units");

		ionc_gas_injector_scannables = new ArrayList<Scannable>();
		ionc_gas_injector_scannables.add(createMock("I0_gas_injector"));
		ionc_gas_injector_scannables.add(createMock("It_gas_injector"));
		ionc_gas_injector_scannables.add(createMock("Iref_gas_injector"));

		thePreparer = new B18DetectorPreparer(energy_scannable, sensitivities, sensitivity_units,
				offsets, offsets_units, ionc_gas_injector_scannables, ionchambers);
		thePreparer.setDiffractionDetector(diffractionDetector);
		XspressParameters xspressParams = new XspressParameters();
		xspressParams.setDetectorName(xspressDetector.getName());
		Xspress3Parameters xspress3Params = new Xspress3Parameters();
		xspress3Params.setDetectorName(xspressDetector.getName());
		VortexParameters vortexParams = new VortexParameters();
		vortexParams.setDetectorName(xmapFluoDetector.getName());

		setupFinder();
	}

	@After
	public void tearDown() {
		// Remove factories from Finder so they do not affect other tests
		Finder.removeAllFactories();
		xmlHelpersMock.close();
	}

	private void setupFinder() throws Exception {
		TestHelpers.setUpTest(B18DetectorPreparerTest.class, "B18DetectorPreparerTest", true);

		// Findables the server needs to know about
		Findable[] findables = new Findable[] { xspressDetector, xspress3Detector, xmapFluoDetector};

		final Factory factory = TestHelpers.createTestFactory();
		for(Findable f : findables) {
			factory.addFindable(f);
			InterfaceProvider.getJythonNamespace().placeInJythonNamespace(f.getName(), f);
		}

		// Need to add object factory to Finder if using Finder.find(...) to get at scannables.
		Finder.addFactory(factory);
	}

	private Scannable createMock(String string) {
		return createMock(DummyScannable.class, string);
	}

	private <T extends Scannable> T createMock(Class<T> clazz, String name) {
		T newMock = Mockito.mock(clazz);
		Mockito.when(newMock.getName()).thenReturn(name);
		Mockito.when(newMock.getInputNames()).thenReturn(new String[]{name});
		Mockito.when(newMock.getExtraNames()).thenReturn(new String[]{});
		Mockito.when(newMock.getOutputFormat()).thenReturn(new String[]{"%.2f"});
		return newMock;
	}

	private void setupMockXmlHelper(FluorescenceDetectorParameters params) throws Exception {
			Mockito.when(XMLHelpers.getBean(ArgumentMatchers.any())).thenReturn(params);
	}

	@Test
	public void testMythenScan() throws Exception{
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
		thePreparer.collectDiffractionData();

		Mockito.verify(energy_scannable).moveTo(10000.0);
		Mockito.verify(diffractionDetector).setCollectionTime(1.2);

		Mockito.verify(diffractionDetector).collectData();
		Mockito.verify(diffractionDetector).readout();
	}

	@Test
	public void testXspress2Detector() throws Exception {

		DetectorParameters detParams = createDetectorParameters();
		FluorescenceParameters fluoParams = detParams.getFluorescenceParameters();

		XspressParameters paramsBean = new XspressParameters();
		paramsBean.setDetectorName(xspressDetector.getName());
		setupMockXmlHelper(paramsBean);

		thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");

		String fullPath = "/scratch/test/xml/path/"+fluoParams.getConfigFileName();
		Mockito.verify(xspressDetector).setConfigFileName(fullPath);
		Mockito.verify(xspressDetector).applyConfigurationParameters(paramsBean);
		assertEquals(xspressDetector.getName(), thePreparer.getSelectedDetector().getName());

		Mockito.verify(xmapFluoDetector, Mockito.never()).applyConfigurationParameters(any(VortexParameters.class));
		Mockito.verify(xspress3Detector, Mockito.never()).applyConfigurationParameters(any(Xspress3Parameters.class));
	}

	@Test
	public void testXspress3Detector() throws Exception {

		DetectorParameters detParams = createDetectorParameters();
		FluorescenceParameters fluoParams = detParams.getFluorescenceParameters();

		Xspress3Parameters paramsBean = new Xspress3Parameters();
		paramsBean.setDetectorName(xspress3Detector.getName());
		setupMockXmlHelper(paramsBean);

		thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");

		String fullPath = "/scratch/test/xml/path/"+fluoParams.getConfigFileName();

		Mockito.verify(xspress3Detector).setConfigFileName(fullPath);
		Mockito.verify(xspress3Detector).applyConfigurationParameters(paramsBean);
		assertEquals(xspress3Detector.getName(), thePreparer.getSelectedDetector().getName());

		Mockito.verify(xmapFluoDetector, Mockito.never()).applyConfigurationParameters(any(VortexParameters.class));
		Mockito.verify(xspressDetector, Mockito.never()).applyConfigurationParameters(any(XspressParameters.class));
	}

	@Test
	public void testXmapDetector() throws Exception {

		DetectorParameters detParams = createDetectorParameters();
		FluorescenceParameters fluoParams = detParams.getFluorescenceParameters();

		VortexParameters paramsBean = new VortexParameters();
		paramsBean.setDetectorName(xmapFluoDetector.getName());
		setupMockXmlHelper(paramsBean);

		thePreparer.configure(null, detParams, null, "/scratch/test/xml/path/");

		String fullPath = "/scratch/test/xml/path/"+fluoParams.getConfigFileName();

		Mockito.verify(xmapMca).setConfigFileName(fullPath);
		Mockito.verify(xmapFluoDetector).applyConfigurationParameters(paramsBean);
		assertEquals(xmapMca.getName(), thePreparer.getSelectedDetector().getName());

		Mockito.verify(xspress3Detector, Mockito.never()).applyConfigurationParameters(any(Xspress3Parameters.class));
		Mockito.verify(xspressDetector, Mockito.never()).applyConfigurationParameters(any(XspressParameters.class));
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
		for (IonChamberParameters params : ionParamsSet){
			transParams.addIonChamberParameter(params);
		}

		DetectorParameters detParams = new DetectorParameters();
		detParams.setTransmissionParameters(transParams);
		detParams.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

		thePreparer.configure(xanesParams, detParams, null, "/scratch/test/xml/path/");
		thePreparer.beforeEachRepetition();

		Mockito.verify(ionchambers).setTimes(new Double[]{1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0});
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
	public void testIonChambers() throws Exception {
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
		Mockito.verifyNoInteractions(sensitivities[1]);
		Mockito.verifyNoInteractions(sensitivity_units[1]);
		Mockito.verifyNoInteractions(offsets[1]);
		Mockito.verifyNoInteractions(offsets_units[1]);
		Mockito.verifyNoInteractions(sensitivities[2]);
		Mockito.verifyNoInteractions(sensitivity_units[2]);
		Mockito.verifyNoInteractions(offsets[2]);
		Mockito.verifyNoInteractions(offsets_units[2]);

		Mockito.verify(ionc_gas_injector_scannables.get(0)).moveTo(new Object[]{"25.0","120.0",99630.0,200.0,1100.0,200.0,"-1","false"});
		Mockito.verifyNoInteractions(ionc_gas_injector_scannables.get(1));
		Mockito.verifyNoInteractions(ionc_gas_injector_scannables.get(2));
	}

	@Test
	public void testStringSubstitutes() throws Exception {
		DetectorConfig detConfig = new DetectorConfig("script command");
		detConfig.setUseScriptCommand(true);
		detConfig.setScriptCommand("test_function(initialEnergy, finalEnergy)");

		DetectorParameters detParams = new DetectorParameters();
		detParams.setDetectorConfigurations(Arrays.asList(detConfig));

		QEXAFSParameters scanParams = new QEXAFSParameters();
		scanParams.setInitialEnergy(1000);
		scanParams.setFinalEnergy(2000);
		thePreparer.configure(scanParams, detParams, null, "/scratch/test/xml/path/");

		// ScriptCommand should have initialEnergy and finalEnergy replaces by actual initial and final energy from scan bean
		String expectedString = String.format("test_function(%.1f, %.1f)", scanParams.getInitialEnergy(), scanParams.getFinalEnergy());
		assertEquals(expectedString, detConfig.getScriptCommand());
	}

	@Test
	public void testStringSubstitutesWorksWithNull() throws Exception {
		DetectorConfig detConfig = new DetectorConfig("script command");
		detConfig.setUseScriptCommand(true);

		DetectorParameters detParams = new DetectorParameters();
		detParams.setDetectorConfigurations(Arrays.asList(detConfig));

		QEXAFSParameters scanParams = new QEXAFSParameters();
		scanParams.setInitialEnergy(1000);
		scanParams.setFinalEnergy(2000);
		thePreparer.configure(scanParams, detParams, null, "/scratch/test/xml/path/");

		// Script command should be unmodified
		assertEquals(null, detConfig.getScriptCommand());
	}

	@Test
	public void testStringSubstitutesBeforeAfterScriptCommands() throws Exception {

		DetectorParameters detParams = new DetectorParameters();
		detParams.setExperimentType(""); // so that detector(s) are not configured

		QEXAFSParameters scanParams = new QEXAFSParameters();
		scanParams.setInitialEnergy(1000);
		scanParams.setFinalEnergy(2000);

		OutputParameters outputParams = new OutputParameters();
		outputParams.setBeforeFirstRepetition("test_before_first(initialEnergy)");
		outputParams.setBeforeScriptName("test_before(initialEnergy, finalEnergy)");
		outputParams.setAfterScriptName("test_after(finalEnergy)");

		thePreparer.configure(scanParams, detParams, outputParams, "/scratch/test/xml/path/");

		// ScriptCommand should have initialEnergy and finalEnergy replaces by actual initial and final energy from scan bean
		String expectedString = String.format("test_before_first(%.1f)", scanParams.getInitialEnergy());
		assertEquals(expectedString, outputParams.getBeforeFirstRepetition());

		expectedString = String.format("test_before(%.1f, %.1f)", scanParams.getInitialEnergy(), scanParams.getFinalEnergy());
		assertEquals(expectedString, outputParams.getBeforeScriptName());

		expectedString = String.format("test_after(%.1f)", scanParams.getFinalEnergy());
		assertEquals(expectedString, outputParams.getAfterScriptName());
	}

	@Test
	public void testStringSubstitutesBeforeAfterScriptWorkWithNull() throws Exception {

		DetectorParameters detParams = new DetectorParameters();
		detParams.setExperimentType(""); // so that detector(s) are not configured

		QEXAFSParameters scanParams = new QEXAFSParameters();
		scanParams.setInitialEnergy(1000);
		scanParams.setFinalEnergy(2000);

		OutputParameters outputParams = new OutputParameters();

		thePreparer.configure(scanParams, detParams, outputParams, "/scratch/test/xml/path/");

		// Script names should be unmodified
		assertEquals(null, outputParams.getBeforeFirstRepetition());
		assertEquals(null, outputParams.getBeforeScriptName());
		assertEquals(null, outputParams.getAfterScriptName());
	}

	private DetectorParameters createDetectorParameters() {
		Set<IonChamberParameters> ionParamsSet = makeIonChamberParameters();

		FluorescenceParameters fluoParams = new FluorescenceParameters();
		fluoParams.setCollectDiffractionImages(false);
		for (IonChamberParameters params : ionParamsSet){
			fluoParams.addIonChamberParameter(params);
		}

		fluoParams.setConfigFileName("Fluo_config.xml");

		DetectorParameters detParams = new DetectorParameters();
		detParams.setFluorescenceParameters(fluoParams);
		detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

		return detParams;
	}
}
