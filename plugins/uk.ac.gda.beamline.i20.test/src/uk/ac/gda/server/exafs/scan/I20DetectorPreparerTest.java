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

import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;

import gda.TestHelpers;
import gda.device.Detector;
import gda.device.Scannable;
import gda.device.detector.NXDetector;
import gda.device.detector.TfgFFoverI0;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.NexusXmap;
import gda.device.detector.xmap.NexusXmapFluorescenceDetectorAdapter;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.DummyScannable;
import gda.device.scannable.TopupChecker;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.factory.ObjectFactory;
import gda.jython.InterfaceProvider;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.beans.vortex.VortexParameters;
import uk.ac.gda.beans.xspress.XspressParameters;
import uk.ac.gda.devices.detector.FluorescenceDetectorParameters;
import uk.ac.gda.server.exafs.scan.preparers.I20DetectorPreparer;

public class I20DetectorPreparerTest {

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
	private TfgFFoverI0 ffI0;
	private XspressParameters xspressParams ;
	private VortexParameters vortexParams;

	private class DetectorPreparerForTest extends I20DetectorPreparer {

		private FluorescenceDetectorParameters params;

		public DetectorPreparerForTest(Scannable[] sensitivities,
				Scannable[] sensitivity_units, Scannable[] offsets, Scannable[] offset_units,
				TfgScalerWithFrames ionchambers, TfgScalerWithFrames I1, Xmap vortex, NXDetector medipix,
				TopupChecker topupChecker) {
			super(xspressSystem, sensitivities, sensitivity_units, offsets, offset_units, ionchambers, I1, vortex, medipix,
					topupChecker);
			setSelectedXspressDetector(xspressSystem);
		}

		public void setParameterBean(FluorescenceDetectorParameters params) {
			this.params = params;
		}

		@Override
		public FluorescenceDetectorParameters getDetectorParametersBean(String path) {
			return params;
		}
	}

	@Before
	public void setup() {
		xspressSystem = (Xspress2Detector) createMock(Xspress2Detector.class, "xspressSystem");
		xmpaMca = (NexusXmap) createMock(NexusXmap.class, "xmpaMca");
		medipix = (NXDetector) createMock(NXDetector.class, "medipix");
		ionchambers = (TfgScalerWithFrames) createMock(TfgScalerWithFrames.class, "ionchambers");
		I1 = (TfgScalerWithFrames) createMock(TfgScalerWithFrames.class, "ionchambers");
		ffI0 = (TfgFFoverI0) createMock(TfgFFoverI0.class, "ffI0");

		xmapFluoDetector = PowerMockito.mock(NexusXmapFluorescenceDetectorAdapter.class);
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

		topupChecker = (TopupChecker) createMock(TopupChecker.class, "ionchambers");

		// Setup detector parameter objects
		xspressParams = new XspressParameters();
		xspressParams.setDetectorName(xspressSystem.getName());

		vortexParams = new VortexParameters();
		vortexParams.setDetectorName(xmapFluoDetector.getName());
	}

	private I20DetectorPreparer makePreparer(FluorescenceDetectorParameters params) {
		DetectorPreparerForTest thePreparer = new DetectorPreparerForTest(sensitivities, sensitivity_units, offset, offset_units,
				ionchambers, I1, xmpaMca, medipix, topupChecker);
		thePreparer.setFFI0(ffI0);
		thePreparer.setParameterBean(params);
		return thePreparer;
	}

	private void setupFinder(String testName) throws Exception {
		TestHelpers.setUpTest(I20DetectorPreparer.class, testName, true);

		// Findables the server needs to know about
		Findable[] findables = new Findable[] { xspressSystem, xmpaMca, medipix, ionchambers, I1, ffI0, xmapFluoDetector };

		ObjectFactory factory = new ObjectFactory();
		for(Findable f : findables) {
			factory.addFindable(f);
			InterfaceProvider.getJythonNamespace().placeInJythonNamespace(f.getName(), f);
		}

		// Need to add object factory to Finder if using Finder.getInstance().find(...) to get at scannables.
		Finder.getInstance().addFactory(factory);
	}

	private Scannable createMockScannable(String string) {
		return createMock(DummyScannable.class, string);
	}

	private Scannable createMock(Class<? extends Scannable> clazz, String name) {
		Scannable newMock = PowerMockito.mock(clazz);
		Mockito.when(newMock.getName()).thenReturn(name);
		return newMock;
	}

	@Test
	public void testGetDetectors() {
		List<Detector> arraylist = makePreparer(xspressParams).getDetectors();

		org.junit.Assert.assertEquals(6, arraylist.size());

		assertTrue(arraylist.contains(xspressSystem));
		assertTrue(arraylist.contains(xmpaMca));
		assertTrue(arraylist.contains(ionchambers));
		assertTrue(arraylist.contains(I1));
		assertTrue(arraylist.contains(medipix));
		assertTrue(arraylist.contains(ffI0));
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

		makePreparer(xspressParams).configure(scanBean, detBean, outputBean, experimentFullPath);

		Mockito.verify(topupChecker).setCollectionTime(2.5);
		Mockito.verify(ionchambers).setDarkCurrentCollectionTime(2.5);

		Mockito.verify(sensitivities[0]).moveTo("1");
		Mockito.verify(sensitivities[1]).moveTo("1");
		Mockito.verify(sensitivities[2]).moveTo("1");
		Mockito.verifyZeroInteractions(sensitivities[3]);

		Mockito.verify(sensitivity_units[0]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[1]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[2]).moveTo("nA/V");
		Mockito.verifyZeroInteractions(sensitivity_units[3]);

		Mockito.verify(offset[0]).moveTo("1");
		Mockito.verify(offset[1]).moveTo("1");
		Mockito.verify(offset[2]).moveTo("1");
		Mockito.verifyZeroInteractions(offset[3]);

		Mockito.verify(offset_units[0]).moveTo("pA");
		Mockito.verify(offset_units[1]).moveTo("pA");
		Mockito.verify(offset_units[2]).moveTo("pA");
		Mockito.verifyZeroInteractions(offset_units[3]);
	}

	@Test
	public void testXspressIsConfigured() throws Exception {
		setupFinder("testXspressIsConfigured");

		XanesScanParameters scanBean = I20PreparersTestUtils.createXanesBean();

		I20OutputParameters outputBean = new I20OutputParameters();

		String experimentFullPath = "/tmp/";

		FluorescenceParameters fluoParams = I20PreparersTestUtils.createGeFluoParameters();

		DetectorParameters detParams = new DetectorParameters();
		detParams.setFluorescenceParameters(fluoParams);
		detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

		makePreparer(xspressParams).configure(scanBean, detParams, outputBean, experimentFullPath);

		Mockito.verify(xspressSystem, Mockito.times(1)).applyConfigurationParameters(xspressParams);
		Mockito.verify(xmapFluoDetector, Mockito.never()).applyConfigurationParameters(vortexParams);

		Mockito.verify(topupChecker).setCollectionTime(2.5);
		Mockito.verify(ionchambers).setDarkCurrentCollectionTime(2.5);

		Mockito.verify(sensitivities[0]).moveTo("1");
		Mockito.verify(sensitivities[1]).moveTo("1");
		Mockito.verify(sensitivities[2]).moveTo("1");
		Mockito.verifyZeroInteractions(sensitivities[3]);

		Mockito.verify(sensitivity_units[0]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[1]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[2]).moveTo("nA/V");
		Mockito.verifyZeroInteractions(sensitivity_units[3]);

		Mockito.verify(offset[0]).moveTo("1");
		Mockito.verify(offset[1]).moveTo("1");
		Mockito.verify(offset[2]).moveTo("1");
		Mockito.verifyZeroInteractions(offset[3]);

		Mockito.verify(offset_units[0]).moveTo("pA");
		Mockito.verify(offset_units[1]).moveTo("pA");
		Mockito.verify(offset_units[2]).moveTo("pA");
		Mockito.verifyZeroInteractions(offset_units[3]);
	}

	@Test
	public void testXmapIsConfigured() throws Exception {
		setupFinder("testXmapIsConfigured");

		XanesScanParameters scanBean = I20PreparersTestUtils.createXanesBean();

		I20OutputParameters outputBean = new I20OutputParameters();

		String experimentFullPath = "/tmp/";

		FluorescenceParameters fluoParams = I20PreparersTestUtils.createSiFluoParameters();

		DetectorParameters detParams = new DetectorParameters();
		detParams.setFluorescenceParameters(fluoParams);
		detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

		I20DetectorPreparer preparer = makePreparer(vortexParams);
		preparer.setVortex(null);
		preparer.configure(scanBean, detParams, outputBean, experimentFullPath);

		// This check incorrectly fails when this unit test is run along with the others in this class; ok when run on its own...
		// Mockito.verify(xmapFluoDetector, Mockito.time(1)).applyConfigurationParameters(vortexParams);

		// Check XMap detector has been set correctly by using detector object located using finder and parameters file
		assertEquals(preparer.getVortex().getName(), xmpaMca.getName());
		Mockito.verify(xspressSystem, Mockito.never()).applyConfigurationParameters(xspressParams);

		Mockito.verify(topupChecker).setCollectionTime(2.5);
		Mockito.verify(ionchambers).setDarkCurrentCollectionTime(2.5);

		Mockito.verify(sensitivities[0]).moveTo("1");
		Mockito.verify(sensitivities[1]).moveTo("1");
		Mockito.verify(sensitivities[2]).moveTo("1");
		Mockito.verifyZeroInteractions(sensitivities[3]);

		Mockito.verify(sensitivity_units[0]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[1]).moveTo("nA/V");
		Mockito.verify(sensitivity_units[2]).moveTo("nA/V");
		Mockito.verifyZeroInteractions(sensitivity_units[3]);

		Mockito.verify(offset[0]).moveTo("1");
		Mockito.verify(offset[1]).moveTo("1");
		Mockito.verify(offset[2]).moveTo("1");
		Mockito.verifyZeroInteractions(offset[3]);

		Mockito.verify(offset_units[0]).moveTo("pA");
		Mockito.verify(offset_units[1]).moveTo("pA");
		Mockito.verify(offset_units[2]).moveTo("pA");
		Mockito.verifyZeroInteractions(offset_units[3]);
	}

	@Test
	public void testCompleteCollection() {
		topupChecker.setCollectionTime(1.0);
		ionchambers.setOutputLogValues(true);

		makePreparer(xspressParams).completeCollection();

		assertTrue(topupChecker.getCollectionTime() == 0.0);
		assertTrue(!ionchambers.isOutputLogValues());
	}
}
