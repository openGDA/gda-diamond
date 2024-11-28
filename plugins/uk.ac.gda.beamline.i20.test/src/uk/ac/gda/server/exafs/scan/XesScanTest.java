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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertSame;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;
import static org.mockito.ArgumentMatchers.any;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.Vector;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.mockito.ArgumentMatchers;
import org.mockito.InOrder;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.invocation.InvocationOnMock;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.data.metadata.NXMetaDataProvider;
import gda.device.Scannable;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.device.scannable.DummyScannable;
import gda.device.scannable.ScannableMotor;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TwoDScanPlotter;
import gda.device.scannable.XESEnergyScannable;
import gda.device.scannable.XasScannable;
import gda.device.scannable.XesSpectrometerScannable;
import gda.factory.Factory;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServer;
import gda.jython.JythonServerFacade;
import gda.jython.batoncontrol.ClientDetails;
import gda.jython.commands.ScannableCommands;
import gda.jython.scriptcontroller.logging.LoggingScriptController;
import gda.scan.ConcurrentScan;
import gda.scan.ScanPlotSettings;
import uk.ac.gda.beans.exafs.DetectorGroup;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.MetadataParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.ScanColourType;
import uk.ac.gda.beans.exafs.SignalParameters;
import uk.ac.gda.beans.exafs.SpectrometerScanParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;
import uk.ac.gda.util.beans.BeansFactory;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class XesScanTest {

	private Scannable xesBraggGroup;
	private Scannable xesEnergyBoth;
	private Scannable xesEnergyGroup;

	private Scannable monoEnergy;
	private XESEnergyScannable xesUpperEnergy;
	private XESEnergyScannable xesLowerEnergy;
	private XesSpectrometerScannable xesBraggUpper;
	private XesSpectrometerScannable xesBraggLower;

	private I20OutputParameters outputParams;
	private ISampleParameters sampleParams;
	private DetectorParameters detParams;
	private Xmap xmpaMca;
	private TfgScalerWithFrames ionchambers;
	private BeamlinePreparer beamlinePreparer;
	private DetectorPreparer detectorPreparer;
	private SampleEnvironmentPreparer samplePreparer;
	private OutputPreparer outputPreparer;
	private NXMetaDataProvider metashop;
	private LoggingScriptController loggingScriptController;
	private EnergyScan xasscan;
	private XesScan xesScan;
	private ConcurrentScan mockScan;
	private ScanPlotSettings mockPlotSettings;
	private final String experimentalFullPath = "/scratch/test/xml/path/";
	private MockedStatic<XMLHelpers> staticMock;
	private MockedStatic<ScannableCommands> staticMock2;
	private SampleEnvironmentIterator mockSampleEnvironmentIterator;

	@Before
	public void setup() throws NoSuchMethodException, SecurityException, Exception {
		LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "DummyDataWriter");

		staticMock = Mockito.mockStatic(XMLHelpers.class);
		staticMock2 = Mockito.mockStatic(ScannableCommands.class);

		ionchambers = Mockito.mock(TfgScalerWithFrames.class);
		Mockito.when(ionchambers.getName()).thenReturn("ionchambers");
		Mockito.when(ionchambers.readout()).thenReturn(new double[] { 1.0, 2.0, 3.0 });
		Mockito.when(ionchambers.getExtraNames()).thenReturn(new String[] { "i0", "it", "iref" });
		Mockito.when(ionchambers.getInputNames()).thenReturn(new String[] { "time" });
		Mockito.when(ionchambers.getOutputFormat()).thenReturn(new String[] { "%.2f", "%.2f", "%.2f", "%.2f" });

		xmpaMca = createMockOfType(Xmap.class, "xmpaMca");
		Mockito.when(xmpaMca.getName()).thenReturn("xmpaMca");
		Mockito.when(xmpaMca.readout()).thenReturn(new double[] { 7.0 });
		Mockito.when(xmpaMca.getExtraNames()).thenReturn(new String[] { "FF" });
		Mockito.when(xmpaMca.getInputNames()).thenReturn(new String[] { "time" });
		Mockito.when(xmpaMca.getOutputFormat()).thenReturn(new String[] { "%.2f", "%.2f" });

		ClientDetails details = Mockito.mock(ClientDetails.class);
		Mockito.when(details.getVisitID()).thenReturn("0-0");

		JythonServerFacade jythonserverfacade = Mockito.mock(JythonServerFacade.class);
		Mockito.when(jythonserverfacade.getBatonHolder()).thenReturn(details);
		InterfaceProvider.setTerminalPrinterForTesting(jythonserverfacade);
		InterfaceProvider.setAuthorisationHolderForTesting(jythonserverfacade);
		InterfaceProvider.setBatonStateProviderForTesting(jythonserverfacade);
		InterfaceProvider.setJythonNamespaceForTesting(jythonserverfacade);
		InterfaceProvider.setScanStatusHolderForTesting(jythonserverfacade);

		// Set the visit directory - so that logging in XasScanBase exception handling works
		LocalProperties.set(LocalProperties.GDA_VISIT_DIR, "/Data");

		Mockito.when(jythonserverfacade.getFromJythonNamespace("ionchambers")).thenReturn(ionchambers);
		Mockito.when(jythonserverfacade.getFromJythonNamespace("xmpaMca")).thenReturn(xmpaMca);


		JythonServer jythonserver = Mockito.mock(JythonServer.class);
		InterfaceProvider.setDefaultScannableProviderForTesting(jythonserver);
		InterfaceProvider.setCurrentScanInformationHolderForTesting(jythonserver);
		InterfaceProvider.setJythonServerNotiferForTesting(jythonserver);
		Mockito.when(jythonserver.getDefaultScannables()).thenReturn(new Vector<Scannable>());

		InterfaceProvider.setScanDataPointProviderForTesting(jythonserverfacade);

		// create the preparers
		beamlinePreparer = Mockito.mock(BeamlinePreparer.class);
		detectorPreparer = Mockito.mock(DetectorPreparer.class);
		samplePreparer = Mockito.mock(SampleEnvironmentPreparer.class);
		outputPreparer = Mockito.mock(OutputPreparer.class);
		metashop = new NXMetaDataProvider();
		loggingScriptController = Mockito.mock(LoggingScriptController.class);

		monoEnergy = Mockito.mock(ScannableMotor.class);
		Mockito.when(monoEnergy.getName()).thenReturn("mono_energy");
		Mockito.when(monoEnergy.getInputNames()).thenReturn(new String[] { "mono_energy" });
		Mockito.when(monoEnergy.getExtraNames()).thenReturn(new String[] {});
		Mockito.when(monoEnergy.getOutputFormat()).thenReturn(new String[] { "%.2f" });
		Mockito.when(monoEnergy.getPosition()).thenReturn(7000.0);

		// create XasScan object
		XasScanFactory theFactory = new XasScanFactory();
		theFactory.setBeamlinePreparer(beamlinePreparer);
		theFactory.setDetectorPreparer(detectorPreparer);
		theFactory.setSamplePreparer(samplePreparer);
		theFactory.setOutputPreparer(outputPreparer);
		theFactory.setLoggingScriptController(loggingScriptController);
		theFactory.setMetashop(metashop);
		theFactory.setIncludeSampleNameInNexusName(true);
		theFactory.setEnergyScannable(monoEnergy);
		xasscan = theFactory.createEnergyScan();

		// create the beans and give to the XasScan

		Set<IonChamberParameters> ionParamsSet = makeIonChamberParameters();

		FluorescenceParameters fluoParams = new FluorescenceParameters();
		fluoParams.setDetectorType("Silicon");
		for (IonChamberParameters params : ionParamsSet) {
			fluoParams.addIonChamberParameter(params);
		}

		TransmissionParameters transParams = new TransmissionParameters();
		transParams.setCollectDiffractionImages(false);
		transParams.setDetectorType("transmission");
		for (IonChamberParameters params : ionParamsSet) {
			transParams.addIonChamberParameter(params);
		}

		DetectorGroup transmissionDetectors = new DetectorGroup("Transmission", new String[] { "ionchambers" });
		DetectorGroup fluoDetectors = new DetectorGroup("Silicon", new String[] { "xmpaMca", "ionchambers" });
		List<DetectorGroup> detectorGroups = new ArrayList<DetectorGroup>();
		detectorGroups.add(transmissionDetectors);
		detectorGroups.add(fluoDetectors);

		detParams = new DetectorParameters();
		detParams.setTransmissionParameters(transParams);
		detParams.setFluorescenceParameters(fluoParams);
		detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);
		detParams.setDetectorGroups(detectorGroups);

		sampleParams = Mockito.mock(ISampleParameters.class);
		Mockito.when(sampleParams.getName()).thenReturn("My Sample");
		Mockito.when(sampleParams.getDescriptions()).thenReturn(new ArrayList<String>());

		outputParams = new I20OutputParameters();
		outputParams.setAsciiFileName("");
		outputParams.setAsciiDirectory("ascii");
		outputParams.setNexusDirectory("nexus");

		// Create the XES energy and bragg scannables
		xesUpperEnergy = createMockOfType(XESEnergyScannable.class, "XESEnergyUpper");
		xesLowerEnergy = createMockOfType(XESEnergyScannable.class, "XESEnergyLower");

		xesBraggUpper = createMockOfType(XesSpectrometerScannable.class, "XESBraggUpper");
		xesBraggLower = createMockOfType(XesSpectrometerScannable.class, "XESBraggLower");
		Mockito.when(xesUpperEnergy.getXes()).thenReturn(xesBraggUpper);
		Mockito.when(xesLowerEnergy.getXes()).thenReturn(xesBraggLower);

		xesBraggGroup = createMockScannable("XESBraggBoth");
		xesEnergyGroup = createMockScannable("XESEnergyGroup");
		xesEnergyBoth = createMockScannable("XESEnergyBoth");

		Mockito.when(xesEnergyBoth.getPosition()).thenReturn(6300.0);

		// normally use a factory object, but we are not testing that here
		xesScan = new XesScan();
		xesScan.setXesBraggGroup(xesBraggGroup);
		xesScan.setXesEnergyGroup(xesEnergyGroup);
		xesScan.setXesEnergyBoth(xesEnergyBoth);
		xesScan.setMono_energy(monoEnergy);
		xesScan.setXas(xasscan);
		xesScan.setBeamlinePreparer(beamlinePreparer);
		xesScan.setDetectorPreparer(detectorPreparer);
		xesScan.setSamplePreparer(samplePreparer);
		xesScan.setOutputPreparer(outputPreparer);
		xesScan.setLoggingScriptController(loggingScriptController);
		xesScan.setMetashop(metashop);
		xesScan.setIncludeSampleNameInNexusName(true);


		// mock the scan so it is not really run
		prepareMockScan();

		// mock the sample preparer object as we are not testing it here, we simply want to know that it was called
		mockSampleEnvironmentIterator = mockSampleEnvIterator();

		mockI20OutputParameters();

		// Add XES scannables to the finder
		final Factory factory = TestHelpers.createTestFactory();
		factory.addFindable(xesUpperEnergy);
		factory.addFindable(xesLowerEnergy);
		Finder.addFactory(factory);
	}

	@After
	public void closeStaticMock() {
		staticMock.close();
		staticMock2.close();
		Finder.removeAllFactories();
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

	private Scannable createMockScannable(String string) {
		return createMockOfType(DummyScannable.class, string);
	}

	private <T extends Scannable> T createMockOfType(Class<T> clazz, String name) {
		T newMock = Mockito.mock(clazz);
		Mockito.when(newMock.getName()).thenReturn(name);
		return newMock;
	}

	private void prepareMockScan() throws NoSuchMethodException, SecurityException, Exception {
		// create mock scan
		mockScan = Mockito.mock(ConcurrentScan.class);

		// runScan is a void method, so have to make an Answer for just that method
		try {
			Mockito.doAnswer(new org.mockito.stubbing.Answer<Void>() {
				@Override
				public Void answer(InvocationOnMock invocation) throws Throwable {
					return null;
				}

			}).when(mockScan).runScan();
		} catch (Exception e) {
			fail(e.getMessage());
		}

		mockPlotSettings = Mockito.mock(ScanPlotSettings.class);
		Mockito.when(mockScan.getScanPlotSettings()).thenReturn(mockPlotSettings);

		// then stub the factory method and make sure that it always retruns the stub
		Mockito.when(ScannableCommands.createConcurrentScan(any(Object[].class))).thenReturn(mockScan);

	}

	@SuppressWarnings("unchecked")
	protected XanesScanParameters mockXanesBeansFactory() throws Exception {
		Region region = new Region();
		region.setEnergy(7000.0);
		region.setStep(3.0);
		region.setTime(1.0);
		XanesScanParameters xanesParams = new XanesScanParameters();
		xanesParams.setEdge("K");
		xanesParams.setElement("Fe");
		xanesParams.addRegion(region);
		xanesParams.setFinalEnergy(7021.0);

		BeansFactory.setClasses(new Class[] { XanesScanParameters.class });
		Mockito.when(XMLHelpers.getBean(ArgumentMatchers.any())).thenReturn(xanesParams);
		return xanesParams;
	}

	protected SampleEnvironmentIterator mockSampleEnvIterator() {
		SampleEnvironmentIterator it = Mockito.mock(SampleEnvironmentIterator.class);
		Mockito.when(it.getNumberOfRepeats()).thenReturn(1);
		Mockito.when(it.getNextSampleName()).thenReturn("My sample");
		Mockito.when(it.getNextSampleDescriptions()).thenReturn(new ArrayList<String>());
		Mockito.when(samplePreparer.createIterator("Fluorescence")).thenReturn(it);
		return it;
	}

	private SpectrometerScanParameters createSpectrometerParams(String name, double start, double stop, double step) {
		SpectrometerScanParameters params = new SpectrometerScanParameters();
		params.setScannableName(name);
		params.setInitialEnergy(start);
		params.setFinalEnergy(stop);
		params.setStepSize(step);
		params.setIntegrationTime(1.0);
		return params;
	}

	@Test
	public void testRunFixedXesScanMonoXanes() throws Exception {

		// mock the BeansFactory so an xml file is not really opened
		XanesScanParameters xanesParams = mockXanesBeansFactory();

		// create and run the XES scan

		var xesParams = new XesScanParameterBuilder()
				.setScanType(XesScanParameters.FIXED_XES_SCAN_XANES)
				.setScanColour(ScanColourType.ONE_COLOUR)
				.build();

		xesParams.setScanFileName("xanes_file.xml");

		SpectrometerScanParameters specParams = new SpectrometerScanParameters();
		specParams.setScannableName(xesUpperEnergy.getName());
		specParams.setFixedEnergy(6300.0);
		specParams.setScanFileName("scan_params.xml");

		xesParams.addSpectrometerScanParameter(specParams);

		Object[] scanArgs = runScan(xesParams);
		InOrder inorder = testOrder(xesParams, mockSampleEnvironmentIterator);

		inorder.verify(detectorPreparer).completeCollection();
		inorder.verify(beamlinePreparer).completeExperiment();

		// Check the scan arguments are correct
		assertEquals(7, scanArgs.length);

		assertTrue(scanArgs[0] instanceof XasScannable);
		var xasScannable = (XasScannable)scanArgs[0];
		assertSame(monoEnergy, xasScannable.getEnergyScannable());

		assertSame(xesUpperEnergy, scanArgs[2]);
		assertEquals(specParams.getFixedEnergy(), scanArgs[3]);

		assertSame(xesBraggUpper, scanArgs[4]);

		assertSame(xmpaMca, scanArgs[5]);
		assertSame(ionchambers, scanArgs[6]);
	}

	@Test
	public void testRunScanXesRegionFixedMono() throws Exception {

		// mock the BeansFactory so an xml file is not really opened
		XanesScanParameters xanesParams = mockXanesBeansFactory();

		// create and run the XES scan

		var xesParams = new XesScanParameterBuilder()
//				.addSpectrometerParameters(xesUpperEnergy.getName(), 6000, 7000, 200)
				.setScanType(XesScanParameters.SCAN_XES_REGION_FIXED_MONO)
				.setScanColour(ScanColourType.ONE_COLOUR)
				.build();

		SpectrometerScanParameters specParams = new SpectrometerScanParameters();
		specParams.setScannableName(xesUpperEnergy.getName());
		specParams.setFixedEnergy(6300.0);
		specParams.setScanFileName("scan_params.xml");

		xesParams.addSpectrometerScanParameter(specParams);

		Object[] scanArgs = runScan(xesParams);

		// Check the scan arguments are correct
		assertEquals(8, scanArgs.length);

		InOrder inorder = testOrder(xesParams, mockSampleEnvironmentIterator);

		inorder.verify(detectorPreparer).completeCollection();
		inorder.verify(beamlinePreparer).completeExperiment();

		assertTrue(scanArgs[0] instanceof XasScannable);
		var xasScannable = (XasScannable)scanArgs[0];
		assertSame(xesEnergyBoth, xasScannable.getEnergyScannable());

		assertSame(monoEnergy, scanArgs[2]);
		assertEquals(xesParams.getMonoEnergy(), scanArgs[3]);

		assertSame(xesUpperEnergy, scanArgs[4]);
		assertSame(xesBraggUpper, scanArgs[5]);

		assertSame(xmpaMca, scanArgs[6]);
		assertSame(ionchambers, scanArgs[7]);
	}

	/**
	 * Test correct order of operation
	 *
	 * @param scanParams
	 * @param it
	 * @return
	 * @throws Exception
	 */
	private InOrder testOrder(IScanParameters scanParams, SampleEnvironmentIterator it) throws Exception {
		InOrder inorder = Mockito.inOrder(beamlinePreparer, detectorPreparer, samplePreparer, outputPreparer, it,
				mockScan);

		inorder.verify(beamlinePreparer).configure(scanParams, detParams, sampleParams, outputParams,
				experimentalFullPath);
		inorder.verify(detectorPreparer).configure(scanParams, detParams, outputParams, experimentalFullPath);
		inorder.verify(samplePreparer).configure(scanParams, sampleParams);
		inorder.verify(outputPreparer).configure(outputParams, scanParams, detParams, sampleParams);

		inorder.verify(samplePreparer).createIterator("Fluorescence");
		inorder.verify(beamlinePreparer).prepareForExperiment();

		inorder.verify(it).resetIterator();
		inorder.verify(it).next();
		inorder.verify(it).getNextSampleName();
		inorder.verify(it).getNextSampleDescriptions();

		inorder.verify(detectorPreparer).beforeEachRepetition();
		inorder.verify(outputPreparer).beforeEachRepetition();

		inorder.verify(outputPreparer).getScannablesToBeAddedAsColumnInDataFile();
		inorder.verify(outputPreparer).getPlotSettings();

		return inorder;
	}

	@Test
	public void test1DXesScan() throws Exception {

		// // mock the sample preparer object as we are not testing it here, we simply want to know that it was called
		var it = mockSampleEnvIterator();

		var xesParams = new XesScanParameterBuilder()
				.addSpectrometerParameters(xesUpperEnergy.getName(), 6000, 7000, 200)
				.build();

		Object[] scanArgs = runScanAndTestPositions(xesParams);
		assertEquals(7, scanArgs.length);

		testOrder(xesParams, it);

		assertEquals(getScannableName(scanArgs[0]), xesUpperEnergy.getName());

		assertEquals(monoEnergy.getName(), getScannableName(scanArgs[2]));
		assertEquals(10000.0, scanArgs[3]);

		assertEquals(xesBraggUpper.getName(), getScannableName(scanArgs[4]));

		assertTrue(scanArgs[5] instanceof Xmap);
		assertTrue(scanArgs[6] instanceof TfgScalerWithFrames);
	}

	@Test
	public void testOneColourEnergies() throws Exception {

		var xesParams = new XesScanParameterBuilder()
				.addSpectrometerParameters(xesUpperEnergy.getName(), 6000, 7000, 200)
				.build();
		runScanAndTestPositions(xesParams);
	}

	@Test
	public void testOneColourDecreasingEnergies() throws Exception {
		var xesParams = new XesScanParameterBuilder()
				.addSpectrometerParameters(xesUpperEnergy.getName(), 7000, 6000, 200)
				.build();

		runScanAndTestPositions(xesParams);
	}

	@Test
	public void testOneColourBothRowEnergies() throws Exception {
		var xesParams = new XesScanParameterBuilder()
				.setScanColour(ScanColourType.ONE_COLOUR)
				.addSpectrometerParameters(xesUpperEnergy.getName(), 7000, 6000, 200)
				.addSpectrometerParameters(xesLowerEnergy.getName(), 7000, 6000, 200)
				.build();

		runScanAndTestPositions(xesParams);
	}

	@Test
	public void testTwoColourEnergies() throws Exception {
		var xesParams = new XesScanParameterBuilder()
				.setScanColour(ScanColourType.TWO_COLOUR)
				.addSpectrometerParameters(xesUpperEnergy.getName(), 7000, 6000, 200)
				.addSpectrometerParameters(xesLowerEnergy.getName(), 6000, 7000, 200)
				.build();
		runScanAndTestPositions(xesParams);
	}

	private Object[] runScanAndTestPositions(XesScanParameters scanParams) throws Exception {
		Object[] scanArgs = runScan(scanParams);
		testPositions( (XesScanPositionProvider)scanArgs[1], scanParams);
		return scanArgs;
	}

	private Object[] runScan(XesScanParameters scanParams) throws Exception {
		xesScan.configureCollection(sampleParams, scanParams, detParams, outputParams, null, experimentalFullPath, 1);
		xesScan.doCollection();
		return xesScan.createScanArguments("sample 1", new ArrayList<String>());
	}
	private class XesScanParameterBuilder {
		private int scanType = XesScanParameters.SCAN_XES_FIXED_MONO;
		private ScanColourType scanColour = ScanColourType.ONE_COLOUR_ROW1;
		private List<SpectrometerScanParameters> specParams = new ArrayList<>();
		private double monoEnergy = 10000;

		public XesScanParameterBuilder addSpectrometerParameters(String name, double start, double stop, double step) {
			this.specParams.add(createSpectrometerParams(name, start, stop, step));
			return this;
		}

		public XesScanParameterBuilder setScanType(int scanType) {
			this.scanType = scanType;
			return this;
		}
		public XesScanParameterBuilder setScanColour(ScanColourType scanColour) {
			this.scanColour = scanColour;
			return this;
		}
		public XesScanParameters build() {
			XesScanParameters params = new XesScanParameters();
			params.setScanColourType(scanColour);
			params.setScanType(scanType);
			params.setSpectrometerScanParameters(specParams);
			params.setMonoEnergy(monoEnergy);
			return params;
		}
	}

	/**
	 * Test all the positions contained in position provider against values
	 * expected based on spectrometer parameters in XesScanParameters.
	 *
	 * @param positionProvider
	 * @param xesParams
	 */
	private void testPositions(XesScanPositionProvider positionProvider, XesScanParameters xesParams) {
		var specParams = xesParams.getPrimarySpectrometerScanParams();
		var secondParams = xesParams.getSecondarySpectrometerScanParams();
		if (xesParams.getScanColourType() == ScanColourType.ONE_COLOUR) {
			secondParams = specParams;
		}
		var points = createPoints(specParams.getInitialEnergy(), specParams.getFinalEnergy(), specParams.getStepSize());
		assertEquals(points.size(), positionProvider.size());

		List<Double> secondarypoints = Collections.emptyList();
		if (secondParams != null) {
			secondarypoints = createPoints(secondParams.getInitialEnergy(), secondParams.getFinalEnergy(), secondParams.getStepSize());
			assertEquals("Incorrect number of second spectrometer row energy points", secondarypoints.size(), positionProvider.size());
		}
		for(int i=0; i<points.size(); i++) {
			Double[] currentPosition = ScannableUtils.objectToArray(positionProvider.get(i));

			assertEquals("Spectrometer energy value incorrect", points.get(i).doubleValue(), currentPosition[0], 1e-5);
			if (!secondarypoints.isEmpty()) {
				assertEquals("Spectrometer second row energy value incorrect", secondarypoints.get(i).doubleValue(), currentPosition[1], 1e-5);
			}
		}
	}

	private List<Double> createPoints(double start, double stop, double step) {
		double stepSize = Math.abs(step);
		if (start > stop) {
			stepSize *= -1;
		}
		List<Double> points = new ArrayList<>();
		double currentPoint = Math.min(start, stop);
		double endPoint = Math.max(start, stop);
		while(currentPoint <= endPoint) {
			points.add(currentPoint);
			currentPoint += Math.abs(stepSize);
		}
		if (start > stop) {
			return points.reversed();
		}
		return points;
	}

	@Test
	public void test2DXesScanMonoInner() throws Exception {

		var xesParams = new XesScanParameterBuilder()
				.addSpectrometerParameters(xesUpperEnergy.getName(), 6000, 7000, 200)
				.setScanType(XesScanParameters.SCAN_XES_SCAN_MONO)
				.build();

		xesParams.setMonoInitialEnergy(11000.0);
		xesParams.setMonoFinalEnergy(12000.0);
		xesParams.setMonoStepSize(100.0);
		xesParams.setLoopChoice(XesScanParameters.LOOPOPTIONS[0]);

		Object[] scanArgs = runScanAndTestPositions(xesParams);
		testOrder(xesParams, mockSampleEnvironmentIterator);

		assertEquals(10, scanArgs.length);

		assertEquals(xesUpperEnergy.getName(), getScannableName(scanArgs[0]));
		testPositions((XesScanPositionProvider)scanArgs[1], xesParams);

		assertEquals(monoEnergy.getName(), getScannableName(scanArgs[2]));
		assertEquals(11000.0, scanArgs[3]);
		assertEquals(12000.0, scanArgs[4]);
		assertEquals(100.0, scanArgs[5]);

		assertEquals(xesBraggUpper.getName(), getScannableName(scanArgs[6]));

		assertTrue(scanArgs[7] instanceof TwoDScanPlotter);
		assertTrue(scanArgs[8] instanceof Xmap);
		assertTrue(scanArgs[9] instanceof TfgScalerWithFrames);
	}

	@Test
	public void test2DXesScanMonoOuter() throws Exception {

		var xesParams = new XesScanParameterBuilder()
				.addSpectrometerParameters(xesUpperEnergy.getName(), 6000, 7000, 200)
				.setScanType(XesScanParameters.SCAN_XES_SCAN_MONO)
				.build();

		xesParams.setMonoInitialEnergy(11000.0);
		xesParams.setMonoFinalEnergy(12000.0);
		xesParams.setMonoStepSize(100.0);
		xesParams.setLoopChoice(XesScanParameters.LOOPOPTIONS[1]);

		Object[] scanArgs = runScan(xesParams);

		testOrder(xesParams, mockSampleEnvironmentIterator);

		assertEquals(10, scanArgs.length);

		assertEquals(monoEnergy.getName(), getScannableName(scanArgs[0]));
		assertEquals(11000.0, scanArgs[1]);
		assertEquals(12000.0, scanArgs[2]);
		assertEquals(100.0, scanArgs[3]);

		assertEquals(xesUpperEnergy.getName(), getScannableName(scanArgs[4]));
		testPositions((XesScanPositionProvider)scanArgs[5], xesParams);

		assertEquals(xesBraggUpper.getName(), getScannableName(scanArgs[6]));

		assertTrue(scanArgs[7] instanceof TwoDScanPlotter);
		assertTrue(scanArgs[8] instanceof Xmap);
		assertTrue(scanArgs[9] instanceof TfgScalerWithFrames);
	}

	protected void mockI20OutputParameters() {
		outputParams = Mockito.mock(I20OutputParameters.class);
		Mockito.when(outputParams.getAsciiFileName()).thenReturn("");
		Mockito.when(outputParams.getAsciiDirectory()).thenReturn("ascii");
		Mockito.when(outputParams.getNexusDirectory()).thenReturn("nexus");
		Mockito.when(outputParams.getMetadataList()).thenReturn(new ArrayList<MetadataParameters>());
		Mockito.when(outputParams.getAfterScriptName()).thenReturn("");
		Mockito.when(outputParams.getBeforeScriptName()).thenReturn("");
		Mockito.when(outputParams.getSignalList()).thenReturn(new ArrayList<SignalParameters>());
	}

	private String getScannableName(Object obj) {
		if (obj instanceof Scannable) {
			return ((Scannable)obj).getName();
		}
		return "";
	}
}
