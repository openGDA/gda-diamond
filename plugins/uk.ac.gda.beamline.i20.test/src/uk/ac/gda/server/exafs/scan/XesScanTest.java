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

import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;
import static org.mockito.ArgumentMatchers.any;

import java.util.ArrayList;
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

import gda.configuration.properties.LocalProperties;
import gda.data.metadata.NXMetaDataProvider;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.device.scannable.DummyScannable;
import gda.device.scannable.ScannableMotor;
import gda.device.scannable.TwoDScanPlotter;
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
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.MetadataParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.SignalParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;
import uk.ac.gda.util.beans.BeansFactory;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class XesScanTest {

	private Scannable analyserAngle;
	private Scannable xes_energy;
	private Scannable mono_energy;
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

	@Before
	public void setup() throws DeviceException {
		LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "DummyDataWriter");

		staticMock = Mockito.mockStatic(XMLHelpers.class);
		staticMock2 = Mockito.mockStatic(ScannableCommands.class);

		ionchambers = Mockito.mock(TfgScalerWithFrames.class);
		Mockito.when(ionchambers.getName()).thenReturn("ionchambers");
		Mockito.when(ionchambers.readout()).thenReturn(new double[] { 1.0, 2.0, 3.0 });
		Mockito.when(ionchambers.getExtraNames()).thenReturn(new String[] { "i0", "it", "iref" });
		Mockito.when(ionchambers.getInputNames()).thenReturn(new String[] { "time" });
		Mockito.when(ionchambers.getOutputFormat()).thenReturn(new String[] { "%.2f", "%.2f", "%.2f", "%.2f" });

		xmpaMca = (Xmap) createMock(Xmap.class, "xmpaMca");
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

		mono_energy = Mockito.mock(ScannableMotor.class);
		Mockito.when(mono_energy.getName()).thenReturn("mono_energy");
		Mockito.when(mono_energy.getInputNames()).thenReturn(new String[] { "mono_energy" });
		Mockito.when(mono_energy.getExtraNames()).thenReturn(new String[] {});
		Mockito.when(mono_energy.getOutputFormat()).thenReturn(new String[] { "%.2f" });
		Mockito.when(mono_energy.getPosition()).thenReturn(7000.0);

		// create XasScan object
		XasScanFactory theFactory = new XasScanFactory();
		theFactory.setBeamlinePreparer(beamlinePreparer);
		theFactory.setDetectorPreparer(detectorPreparer);
		theFactory.setSamplePreparer(samplePreparer);
		theFactory.setOutputPreparer(outputPreparer);
		theFactory.setLoggingScriptController(loggingScriptController);
		theFactory.setMetashop(metashop);
		theFactory.setIncludeSampleNameInNexusName(true);
		theFactory.setEnergyScannable(mono_energy);
		theFactory.setScanName("energyScan");
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

		analyserAngle = createMockScannable("analyserAngle");
		xes_energy = createMockScannable("analyserAngle");
		Mockito.when(xes_energy.getPosition()).thenReturn(6300.0);

		// normally use a factory object, but we are not testing that here
		xesScan = new XesScan();
		xesScan.setAnalyserAngle(analyserAngle);
		xesScan.setXes_energy(xes_energy);
		xesScan.setMono_energy(mono_energy);
		xesScan.setXas(xasscan);
		xesScan.setBeamlinePreparer(beamlinePreparer);
		xesScan.setDetectorPreparer(detectorPreparer);
		xesScan.setSamplePreparer(samplePreparer);
		xesScan.setOutputPreparer(outputPreparer);
		xesScan.setLoggingScriptController(loggingScriptController);
		xesScan.setMetashop(metashop);
		xesScan.setIncludeSampleNameInNexusName(true);



	}

	@After
	public void closeStaticMock() {
		staticMock.close();
		staticMock2.close();
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
		return createMock(DummyScannable.class, string);
	}

	private Scannable createMock(Class<? extends Scannable> clazz, String name) {
		Scannable newMock = Mockito.mock(clazz);
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
		Mockito.when(ScannableCommands.createConcurrentScan(any())).thenReturn(mockScan);

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
		Mockito.when(XMLHelpers.getBeanObject(ArgumentMatchers.anyString(), ArgumentMatchers.any())).thenReturn(xanesParams);
		return xanesParams;
	}

	private void verifySignalParametersContains(List<SignalParameters> signalList, Scannable[] scannables) {

		for (Scannable scannable : scannables) {
			boolean found = false;
			for (SignalParameters signal : signalList) {
				if (signal.getScannableName().equals(scannable.getName())) {
					found = true;
					break;
				}
			}
			if (!found) {
				fail("Signal parameters did not contain " + scannable.getName());
			}
		}

	}

	protected SampleEnvironmentIterator mockSampleEnvIterator() {
		SampleEnvironmentIterator it = Mockito.mock(SampleEnvironmentIterator.class);
		Mockito.when(it.getNumberOfRepeats()).thenReturn(1);
		Mockito.when(it.getNextSampleName()).thenReturn("My sample");
		Mockito.when(it.getNextSampleDescriptions()).thenReturn(new ArrayList<String>());
		Mockito.when(samplePreparer.createIterator("Fluorescence")).thenReturn(it);
		return it;
	}

	@Test
	public void testRunXanes() throws Exception {
		// mock the scan so it is not really run
		prepareMockScan();

		// mock the BeansFactory so an xml file is not really opened
		XanesScanParameters xanesParams = mockXanesBeansFactory();

		// mock the sample preparer object as we are not testing it here, we simply want to know that it was called
		SampleEnvironmentIterator it = mockSampleEnvIterator();

		// create and run the XES scan
		XesScanParameters xesParams = new XesScanParameters();
		xesParams.setScanType(XesScanParameters.FIXED_XES_SCAN_XANES);
		xesParams.setXesEnergy(6300.0);
		xesParams.setScanFileName(""); // response from BeansFactory mocked above
		xesScan.configureCollection(sampleParams, xesParams, detParams, outputParams, null, experimentalFullPath, 1);
		xesScan.doCollection();

		// what has been operated on?
		InOrder inorder = Mockito.inOrder(beamlinePreparer, detectorPreparer, samplePreparer, outputPreparer, it,
				mockScan);

		inorder.verify(beamlinePreparer).configure(xanesParams, detParams, sampleParams, outputParams,
				experimentalFullPath);
		inorder.verify(detectorPreparer).configure(xanesParams, detParams, outputParams, experimentalFullPath);
		inorder.verify(samplePreparer).configure(xanesParams, sampleParams);
		inorder.verify(outputPreparer).configure(outputParams, xanesParams, detParams, sampleParams);

		inorder.verify(samplePreparer).createIterator("Fluorescence");
		inorder.verify(beamlinePreparer).prepareForExperiment();

		inorder.verify(it).resetIterator();
		inorder.verify(it).next();
		inorder.verify(it).getNextSampleName();
		inorder.verify(it).getNextSampleDescriptions();

		inorder.verify(detectorPreparer).beforeEachRepetition();
		inorder.verify(outputPreparer).beforeEachRepetition();

		inorder.verify(outputPreparer).getPlotSettings();

		// the scan run is controlled by the xasscan object, which we do not wish to test here.
		// but do test that the outputParams object was modified to contain

		verifySignalParametersContains(outputParams.getSignalList(), new Scannable[] { xes_energy, analyserAngle });

		// inorder.verify(outputParams).getAfterScriptName();
		inorder.verify(detectorPreparer).completeCollection();
		inorder.verify(beamlinePreparer).completeExperiment();

	}

	@Test
	public void testRunXanesTestOutputParamsCalledCorrectly() throws Exception {
		mockI20OutputParameters();

		// mock the scan so it is not really run
		prepareMockScan();

		// mock the BeansFactory so an xml file is not really opened
		XanesScanParameters xanesParams = mockXanesBeansFactory();

		// mock the sample preparer object as we are not testing it here, we simply want to know that it was called
		SampleEnvironmentIterator it = mockSampleEnvIterator();

		// create and run the XES scan
		XesScanParameters xesParams = new XesScanParameters();
		xesParams.setScanType(XesScanParameters.FIXED_XES_SCAN_XANES);
		xesParams.setXesEnergy(6300.0);
		xesParams.setScanFileName(""); // response from BeansFactory mocked above
		xesScan.configureCollection(sampleParams, xesParams, detParams, outputParams, null, experimentalFullPath, 1);
		xesScan.doCollection();

		// what has been operated on?
		InOrder inorder = Mockito.inOrder(beamlinePreparer, detectorPreparer, samplePreparer, outputPreparer, it,
				mockScan, outputParams);

		inorder.verify(beamlinePreparer).configure(xanesParams, detParams, sampleParams, outputParams,
				experimentalFullPath);
		inorder.verify(detectorPreparer).configure(xanesParams, detParams, outputParams, experimentalFullPath);
		inorder.verify(samplePreparer).configure(xanesParams, sampleParams);
		inorder.verify(outputPreparer).configure(outputParams, xanesParams, detParams, sampleParams);

		inorder.verify(samplePreparer).createIterator("Fluorescence");
		inorder.verify(beamlinePreparer).prepareForExperiment();

		inorder.verify(it).resetIterator();
		inorder.verify(it).next();
		inorder.verify(it).getNextSampleName();
		inorder.verify(it).getNextSampleDescriptions();

		inorder.verify(outputParams).getBeforeScriptName();

		inorder.verify(detectorPreparer).beforeEachRepetition();
		inorder.verify(outputPreparer).beforeEachRepetition();

		inorder.verify(outputPreparer).getScannablesToBeAddedAsColumnInDataFile();
		inorder.verify(outputPreparer).getPlotSettings();

		// the scan run is controlled by the xasscan object, which we do not wish to test here.

		inorder.verify(outputParams).getAfterScriptName();
		inorder.verify(detectorPreparer).completeCollection();
		inorder.verify(beamlinePreparer).completeExperiment();

	}

	@Test
	public void test1DXesScan() throws Exception {

		mockI20OutputParameters();

		// mock the scan so it is not really run
		prepareMockScan();

		// // mock the sample preparer object as we are not testing it here, we simply want to know that it was called
		mockSampleEnvIterator();

		XesScanParameters xesParams = new XesScanParameters();
		xesParams.setScanType(XesScanParameters.SCAN_XES_FIXED_MONO);
		xesParams.setXesInitialEnergy(6000.0);
		xesParams.setXesFinalEnergy(7000.0);
		xesParams.setXesStepSize(200.0);
		xesParams.setMonoEnergy(10000.0);

		xesScan.configureCollection(sampleParams, xesParams, detParams, outputParams, null, experimentalFullPath, 1);
		xesScan.doCollection();

		Object[] scanArgs = xesScan.createScanArguments("sample 1", new ArrayList<String>());

		assertTrue(scanArgs.length == 9);

		assertTrue(((Scannable) scanArgs[0]).getName().equals(xes_energy.getName()));
		assertTrue(scanArgs[1].equals(6000.0));
		assertTrue(scanArgs[2].equals(7000.0));
		assertTrue(scanArgs[3].equals(200.0));
		assertTrue(getScannableName(scanArgs[4]).equals(mono_energy.getName()));
		assertTrue(scanArgs[5].equals(10000.0));
		assertTrue(getScannableName(scanArgs[6]).equals(analyserAngle.getName()));
		assertTrue(scanArgs[7] instanceof Xmap);
		assertTrue(scanArgs[8] instanceof TfgScalerWithFrames);

	}

	@Test
	public void test2DXesScan() throws Exception {

		mockI20OutputParameters();

		// mock the scan so it is not really run
		prepareMockScan();

		// mock the sample preparer object as we are not testing it here, we simply want to know that it was called
		mockSampleEnvIterator();

		XesScanParameters xesParams = new XesScanParameters();
		xesParams.setScanType(XesScanParameters.SCAN_XES_SCAN_MONO);
		xesParams.setXesInitialEnergy(6000.0);
		xesParams.setXesFinalEnergy(7000.0);
		xesParams.setXesStepSize(200.0);
		xesParams.setMonoInitialEnergy(11000.0);
		xesParams.setMonoFinalEnergy(12000.0);
		xesParams.setMonoStepSize(100.0);
		xesParams.setLoopChoice(XesScanParameters.LOOPOPTIONS[0]);

		xesScan.configureCollection(sampleParams, xesParams, detParams, outputParams, null, experimentalFullPath, 1);
		xesScan.doCollection();

		Object[] scanArgs = xesScan.createScanArguments("sample 1", new ArrayList<String>());

		assertTrue(scanArgs.length == 12);

		assertTrue(((Scannable) scanArgs[0]).getName().equals(xes_energy.getName()));
		assertTrue(scanArgs[1].equals(6000.0));
		assertTrue(scanArgs[2].equals(7000.0));
		assertTrue(scanArgs[3].equals(200.0));
		assertTrue(getScannableName(scanArgs[4]).equals(mono_energy.getName()));
		assertTrue(scanArgs[5].equals(11000.0));
		assertTrue(scanArgs[6].equals(12000.0));
		assertTrue(scanArgs[7].equals(100.0));
		assertTrue(getScannableName(scanArgs[8]).equals(analyserAngle.getName()));

		assertTrue(scanArgs[9] instanceof TwoDScanPlotter);
		assertTrue(scanArgs[10] instanceof Xmap);
		assertTrue(scanArgs[11] instanceof TfgScalerWithFrames);
	}

	@Test
	public void test2DXesScanOtherDirection() throws Exception {

		mockI20OutputParameters();

		// mock the scan so it is not really run
		prepareMockScan();

		// mock the sample preparer object as we are not testing it here, we simply want to know that it was called
		mockSampleEnvIterator();

		XesScanParameters xesParams = new XesScanParameters();
		xesParams.setScanType(XesScanParameters.SCAN_XES_SCAN_MONO);
		xesParams.setXesInitialEnergy(6000.0);
		xesParams.setXesFinalEnergy(7000.0);
		xesParams.setXesStepSize(200.0);
		xesParams.setMonoInitialEnergy(11000.0);
		xesParams.setMonoFinalEnergy(12000.0);
		xesParams.setMonoStepSize(100.0);
		xesParams.setLoopChoice(XesScanParameters.LOOPOPTIONS[1]);

		xesScan.configureCollection(sampleParams, xesParams, detParams, outputParams, null, experimentalFullPath, 1);
		xesScan.doCollection();

		Object[] scanArgs = xesScan.createScanArguments("sample 1", new ArrayList<String>());

		assertTrue(scanArgs.length == 12);

		assertTrue(((Scannable) scanArgs[0]).getName().equals(mono_energy.getName()));
		assertTrue(scanArgs[1].equals(11000.0));
		assertTrue(scanArgs[2].equals(12000.0));
		assertTrue(scanArgs[3].equals(100.0));
		assertTrue(getScannableName(scanArgs[4]).equals(xes_energy.getName()));
		assertTrue(scanArgs[5].equals(6000.0));
		assertTrue(scanArgs[6].equals(7000.0));
		assertTrue(scanArgs[7].equals(200.0));
		assertTrue(getScannableName(scanArgs[8]).equals(analyserAngle.getName()));

		assertTrue(scanArgs[9] instanceof TwoDScanPlotter);
		assertTrue(scanArgs[10] instanceof Xmap);
		assertTrue(scanArgs[11] instanceof TfgScalerWithFrames);
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
