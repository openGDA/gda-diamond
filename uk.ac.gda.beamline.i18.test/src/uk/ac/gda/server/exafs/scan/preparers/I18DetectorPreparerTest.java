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

import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.NXDetector;
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
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;

public class I18DetectorPreparerTest {

	private Scannable[] sensitivities;
	private Xspress2Detector xspressSystem;
	private Xmap xmpaMca;
	private TfgScalerWithFrames ionchambers;
	private I18DetectorPreparer thePreparer;
	private BufferedDetector qexafs_counterTimer01;
	private BufferedDetector qexafs_xspress;
	private BufferedDetector QexafsFFI0;
	private BufferedDetector qexafs_xmap;
	private NXDetector cmos_for_maps;
	private BufferedDetector buffered_cid;

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
		qexafs_counterTimer01 = (BufferedDetector) createMock(BufferedDetector.class, "qexafs_counterTimer01");
		qexafs_xspress = (BufferedDetector) createMock(BufferedDetector.class, "qexafs_xspress");
		QexafsFFI0 = (BufferedDetector) createMock(BufferedDetector.class, "QexafsFFI0");
		qexafs_xmap = (BufferedDetector) createMock(BufferedDetector.class, "qexafs_xmap");
		buffered_cid = (BufferedDetector) createMock(BufferedDetector.class, "buffered_cid");
		cmos_for_maps = (NXDetector) createMock(NXDetector.class, "cmos_for_maps");

		sensitivities = new Scannable[3];
		sensitivities[0] = createMockScannable("i0_keithley_gain");
		sensitivities[1] = createMockScannable("it_keithley_gain");

		thePreparer = new I18DetectorPreparer(sensitivities, ionchambers, xspressSystem, xmpaMca,
				qexafs_counterTimer01, qexafs_xspress, QexafsFFI0, qexafs_xmap, buffered_cid, cmos_for_maps);
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
	public void testDiffractionDetectors() throws Exception {
		Set<IonChamberParameters> ionParamsSet = makeIonChamberParameters();

		FluorescenceParameters fluoParams = new FluorescenceParameters();
		for (IonChamberParameters params : ionParamsSet) {
			fluoParams.addIonChamberParameter(params);
		}

		fluoParams.setConfigFileName("Fluo_config.xml");
		fluoParams.setDetectorType("Germanium");

		DetectorParameters detParams = new DetectorParameters();
		detParams.setFluorescenceParameters(fluoParams);
		detParams.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);
		
		MicroFocusScanParameters mfParameters = new MicroFocusScanParameters();

		thePreparer.configure(mfParameters, detParams, null, "/scratch/test/xml/path/");
		
		// only return an object for step maps with diffraction flag set to true
		
		mfParameters.setRaster(false);
		fluoParams.setCollectDiffractionImages(true);
		org.junit.Assert.assertEquals(cmos_for_maps, thePreparer.getExtraDetectors()[0]);
		
		mfParameters.setRaster(false);
		fluoParams.setCollectDiffractionImages(false);
		org.junit.Assert.assertNull(thePreparer.getExtraDetectors());
		
		
		mfParameters.setRaster(true);
		fluoParams.setCollectDiffractionImages(true);
		org.junit.Assert.assertNull(thePreparer.getExtraDetectors());
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

		thePreparer.configure(xanesParams, detParams, null, "/scratch/test/xml/path");
		thePreparer.beforeEachRepetition();

		Mockito.verify(ionchambers).setTimes(new Double[] { 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0 });
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

		Mockito.verify(sensitivities[0]).moveTo("1 nA/V");
	}

}
