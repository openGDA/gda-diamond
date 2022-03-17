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
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.mock;

import java.nio.file.Paths;
import java.util.List;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.mockito.ArgumentMatchers;
import org.mockito.MockedStatic;
import org.mockito.Mockito;

import gda.TestHelpers;
import gda.device.Detector;
import gda.device.Scannable;
import gda.device.detector.NXDetector;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.NexusXmap;
import gda.device.detector.xmap.NexusXmapFluorescenceDetectorAdapter;
import gda.device.detector.xmap.TfgXMapFFoverI0;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.DummyScannable;
import gda.device.scannable.DummyScannableMotor;
import gda.device.scannable.TopupChecker;
import gda.factory.Factory;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerFacade;
import uk.ac.gda.beamline.i20.scannable.MonoOptimisation;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.beans.vortex.VortexParameters;
import uk.ac.gda.beans.xspress.XspressParameters;
import uk.ac.gda.devices.detector.FluorescenceDetectorParameters;
import uk.ac.gda.server.exafs.scan.preparers.I20DetectorPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class I20DetectorPreparerTest {

	private static MockedStatic<XMLHelpers> xmlHelpersMock;

	private Xspress2Detector xspressSystem;
	private NexusXmap xmpaMca;
	private NexusXmapFluorescenceDetectorAdapter xmapFluoDetector;
	private NXDetector medipix;
	private TfgScalerWithFrames ionchambers;
	private TfgScalerWithFrames I1;
	private Scannable[] sensitivities;
	private Scannable[] sensitivity_units;
	private Scannable[] offset;
	private Scannable[] offset_units;
	private TopupChecker topupChecker;
	private TfgXMapFFoverI0 ffI1;
	private XspressParameters xspressParams ;
	private VortexParameters vortexParams;
	private MonoOptimisation monoOptimiser;


	@BeforeClass
	public static void initStaticMock() {
		xmlHelpersMock = Mockito.mockStatic(XMLHelpers.class);
	}

	@AfterClass
	public static void releaseStaticMock() {
		xmlHelpersMock.close();
	}

	@Before
	public void setup() {
		JythonServerFacade jythonserverfacade = mock(JythonServerFacade.class);
		InterfaceProvider.setTerminalPrinterForTesting(jythonserverfacade);

		xspressSystem = createMock(Xspress2Detector.class, "xspressSystem");
		xmpaMca =  createMock(NexusXmap.class, "xmpaMca");
		medipix = createMock(NXDetector.class, "medipix");
		ionchambers = createMock(TfgScalerWithFrames.class, "ionchambers");
		I1 =  createMock(TfgScalerWithFrames.class, "ionchambers");
		ffI1 = createMock(TfgXMapFFoverI0.class, "ffI0");

		xmapFluoDetector = Mockito.mock(NexusXmapFluorescenceDetectorAdapter.class);
		Mockito.when(xmapFluoDetector.getName()).thenReturn("xmapFluoDetector");
		Mockito.when(xmapFluoDetector.getXmap()).thenReturn(xmpaMca);

		sensitivities = new Scannable[4];
		sensitivities[0] = createMockScannable("i0_stanford_sensitivity");
		sensitivities[1] = createMockScannable("it_stanford_sensitivity");
		sensitivities[2] = createMockScannable("iref_stanford_sensitivity");
		sensitivities[3] = createMockScannable("i1_stanford_sensitivity");

		sensitivity_units = new Scannable[4];
		sensitivity_units[0] = createMockScannable("i0_stanford_sensitivity_units");
		sensitivity_units[1] = createMockScannable("it_stanford_sensitivity_units");
		sensitivity_units[2] = createMockScannable("iref_stanford_sensitivity_units");
		sensitivity_units[3] = createMockScannable("i1_stanford_sensitivity_units");

		offset = new Scannable[4];
		offset[0] = createMockScannable("i0_stanford_offset");
		offset[1] = createMockScannable("it_stanford_offset");
		offset[2] = createMockScannable("iref_stanford_offset");
		offset[3] = createMockScannable("i1_stanford_offset");

		offset_units = new Scannable[4];
		offset_units[0] = createMockScannable("i0_stanford_offset_units");
		offset_units[1] = createMockScannable("it_stanford_offset_units");
		offset_units[2] = createMockScannable("iref_stanford_offset_units");
		offset_units[3] = createMockScannable("i1_stanford_offset_units");

		topupChecker = createMock(TopupChecker.class, "ionchambers");

		// Setup detector parameter objects
		xspressParams = new XspressParameters();
		xspressParams.setDetectorName(xspressSystem.getName());

		vortexParams = new VortexParameters();
		vortexParams.setDetectorName(xmapFluoDetector.getName());

		Scannable dummyMotor = new DummyScannableMotor();
		dummyMotor.setName("dummyMotor");

		monoOptimiser = new MonoOptimisation(dummyMotor, ionchambers);
		monoOptimiser.setAllowOptimisation(false);
	}

	@After
	public void tearDown() {
		// Remove factories from Finder so they do not affect other tests
		Finder.removeAllFactories();
	}

	private I20DetectorPreparer makePreparer() {
		I20DetectorPreparer thePreparer = new I20DetectorPreparer(sensitivities, sensitivity_units, offset, offset_units,
				ionchambers, I1, xmpaMca, medipix, topupChecker);
		thePreparer.setFFI1(ffI1);
		thePreparer.setMonoOptimiser(monoOptimiser);
		return thePreparer;
	}

	private void setupFinder(String testName) throws Exception {
		TestHelpers.setUpTest(I20DetectorPreparer.class, testName, true);

		// Findables the server needs to know about
		Findable[] findables = new Findable[] { xspressSystem, xmpaMca, medipix, ionchambers, I1, ffI1, xmapFluoDetector };

		final Factory factory = TestHelpers.createTestFactory();
		for(Findable f : findables) {
			factory.addFindable(f);
			InterfaceProvider.getJythonNamespace().placeInJythonNamespace(f.getName(), f);
		}

		// Need to add object factory to Finder if using Finder.find(...) to get at scannables.
		Finder.addFactory(factory);
	}

	private Scannable createMockScannable(String string) {
		return createMock(DummyScannable.class, string);
	}

	private <T extends Scannable> T createMock(Class<T> clazz, String name) {
		T newMock = Mockito.mock(clazz);
		Mockito.when(newMock.getName()).thenReturn(name);
		return newMock;
	}

	private void setupMockXmlHelper(FluorescenceDetectorParameters params) throws Exception {
		Mockito.when(XMLHelpers.getBean(ArgumentMatchers.any())).thenReturn(params);
	}

	@Test
	public void testGetDetectors() {
		List<Detector> arraylist = makePreparer().getDetectors();

		org.junit.Assert.assertEquals(5, arraylist.size());
		// empty element for selected Xspress detector (set after configure has been run, only if using Fluorescence parameters in the DetectorParameters)
		assertTrue(arraylist.contains(null));
		assertTrue(arraylist.contains(xmpaMca));
		assertTrue(arraylist.contains(ionchambers));
		assertTrue(arraylist.contains(I1));
		assertTrue(arraylist.contains(medipix));
	}

	@Test
	public void testIonChambersAreConfigured() throws Exception {
		XanesScanParameters scanBean = I20PreparersTestUtils.createXanesBean();

		I20OutputParameters outputBean = new I20OutputParameters();

		String experimentFullPath = "/tmp";

		TransmissionParameters transParams = I20PreparersTestUtils.createTransmissionParameters();

		DetectorParameters detBean = new DetectorParameters();
		detBean.setTransmissionParameters(transParams);
		detBean.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

		setupMockXmlHelper(xspressParams);

		I20DetectorPreparer preparer = makePreparer();
		preparer.configure(scanBean, detBean, outputBean, experimentFullPath);
		preparer.beforeEachRepetition();

		Mockito.verify(topupChecker).setCollectionTime(2.5);
		Mockito.verify(ionchambers).setDarkCurrentCollectionTime(2.5);

		Mockito.verify(sensitivities[0]).moveTo("1");
		Mockito.verify(sensitivities[1]).moveTo("1");
		Mockito.verify(sensitivities[2]).moveTo("1");
		Mockito.verifyNoInteractions(sensitivities[3]);

		Mockito.verify(sensitivity_units[0]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[1]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[2]).moveTo("nA/V");
		Mockito.verifyNoInteractions(sensitivity_units[3]);

		Mockito.verify(offset[0]).moveTo("1");
		Mockito.verify(offset[1]).moveTo("1");
		Mockito.verify(offset[2]).moveTo("1");
		Mockito.verifyNoInteractions(offset[3]);

		Mockito.verify(offset_units[0]).moveTo("pA");
		Mockito.verify(offset_units[1]).moveTo("pA");
		Mockito.verify(offset_units[2]).moveTo("pA");
		Mockito.verifyNoInteractions(offset_units[3]);
	}

	@Test
	public void testXspressIsConfigured() throws Exception {
		setupFinder("testXspressIsConfigured");
		String experimentFullPath = "/tmp/";

		FluorescenceParameters fluoParams = I20PreparersTestUtils.createGeFluoParameters();
		DetectorParameters detParams = new DetectorParameters();
		detParams.setFluorescenceParameters(fluoParams);
		detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

		setupMockXmlHelper(xspressParams);

		I20DetectorPreparer preparer = makePreparer();
		preparer.configure(I20PreparersTestUtils.createXanesBean(), detParams, new I20OutputParameters(), experimentFullPath);

		assertEquals(xspressSystem.getName(), preparer.getSelectedXspressDetector().getName());
		Mockito.verify(xspressSystem).applyConfigurationParameters(xspressParams);
		Mockito.verify(xspressSystem).setConfigFileName(Paths.get(experimentFullPath, fluoParams.getConfigFileName()).toString());
		Mockito.verify(xmapFluoDetector, Mockito.never()).applyConfigurationParameters(ArgumentMatchers.any(XspressParameters.class));

		preparer.beforeEachRepetition();
		Mockito.verify(topupChecker).setCollectionTime(2.5);
		Mockito.verify(ionchambers).setDarkCurrentCollectionTime(2.5);

		Mockito.verify(sensitivities[0]).moveTo("1");
		Mockito.verify(sensitivities[1]).moveTo("1");
		Mockito.verify(sensitivities[2]).moveTo("1");
		Mockito.verifyNoInteractions(sensitivities[3]);

		Mockito.verify(sensitivity_units[0]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[1]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[2]).moveTo("nA/V");
		Mockito.verifyNoInteractions(sensitivity_units[3]);

		Mockito.verify(offset[0]).moveTo("1");
		Mockito.verify(offset[1]).moveTo("1");
		Mockito.verify(offset[2]).moveTo("1");
		Mockito.verifyNoInteractions(offset[3]);

		Mockito.verify(offset_units[0]).moveTo("pA");
		Mockito.verify(offset_units[1]).moveTo("pA");
		Mockito.verify(offset_units[2]).moveTo("pA");
		Mockito.verifyNoInteractions(offset_units[3]);
	}

	@Test
	public void testXmapIsConfigured() throws Exception {
		setupFinder("testXmapIsConfigured");

		String experimentFullPath = "/tmp/";

		FluorescenceParameters fluoParams = I20PreparersTestUtils.createSiFluoParameters();
		DetectorParameters detParams = new DetectorParameters();
		detParams.setFluorescenceParameters(fluoParams);
		detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);
		setupMockXmlHelper(vortexParams);

		I20DetectorPreparer preparer = makePreparer();
		preparer.configure(I20PreparersTestUtils.createXanesBean(), detParams, new I20OutputParameters(), experimentFullPath);

		// Check XMap detector has been set correctly by using detector object located using finder and parameters file
		assertEquals(preparer.getVortex().getName(), xmpaMca.getName());
		Mockito.verify(xmapFluoDetector).applyConfigurationParameters(vortexParams);
		Mockito.verify(xmpaMca).setConfigFileName(Paths.get(experimentFullPath, fluoParams.getConfigFileName()).toString());
		Mockito.verify(xspressSystem, Mockito.never()).applyConfigurationParameters(ArgumentMatchers.any(XspressParameters.class));

		preparer.beforeEachRepetition();
		Mockito.verify(topupChecker).setCollectionTime(2.5);
		Mockito.verify(ionchambers).setDarkCurrentCollectionTime(2.5);

		Mockito.verify(sensitivities[0]).moveTo("1");
		Mockito.verify(sensitivities[1]).moveTo("1");
		Mockito.verify(sensitivities[2]).moveTo("1");
		Mockito.verifyNoInteractions(sensitivities[3]);

		Mockito.verify(sensitivity_units[0]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[1]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[2]).moveTo("nA/V");
		Mockito.verifyNoInteractions(sensitivity_units[3]);

		Mockito.verify(offset[0]).moveTo("1");
		Mockito.verify(offset[1]).moveTo("1");
		Mockito.verify(offset[2]).moveTo("1");
		Mockito.verifyNoInteractions(offset[3]);

		Mockito.verify(offset_units[0]).moveTo("pA");
		Mockito.verify(offset_units[1]).moveTo("pA");
		Mockito.verify(offset_units[2]).moveTo("pA");
		Mockito.verifyNoInteractions(offset_units[3]);
	}

	@Test
	public void testCompleteCollection() {
		topupChecker.setCollectionTime(1.0);
		ionchambers.setOutputLogValues(true);

		makePreparer().completeCollection();

		assertTrue(topupChecker.getCollectionTime() == 0.0);
		assertTrue(!ionchambers.isOutputLogValues());
	}
}
