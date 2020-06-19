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

import java.util.ArrayList;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;

import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.scan.ScanPlotSettings;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.server.exafs.scan.preparers.I20DetectorPreparer;
import uk.ac.gda.server.exafs.scan.preparers.I20OutputPreparer;

public class I20OutputPreparerTest {

	private AsciiDataWriterConfiguration datawriterconfig;
	private AsciiDataWriterConfiguration datawriterconfig_xes;
	private TfgScalerWithFrames ionchambers;
	private Xspress2Detector xspressSystem;
	private Xmap xmpaMca;
	private I20DetectorPreparer i20DetectorPreparer;
	private I20OutputPreparer thePreparer;
	private NXMetaDataProvider metashop;

	@Before
	public void setup() {

//		// mock the metashop and add it to the Finder. Yuck, but then we can see calls to it.
		metashop = Mockito.mock(NXMetaDataProvider.class);
//		Mockito.when(metashop.getName()).thenReturn("metashop");
//		ObjectFactory factory = new ObjectFactory();
//		factory.addFindable(metashop);
//		Finder.addFactory(factory);

		datawriterconfig = PowerMockito.mock(AsciiDataWriterConfiguration.class);
		datawriterconfig_xes = PowerMockito.mock(AsciiDataWriterConfiguration.class);

		ionchambers = (TfgScalerWithFrames) createMock(TfgScalerWithFrames.class, "ionchambers");
		xspressSystem = (Xspress2Detector) createMock(Xspress2Detector.class, "xspressSystem");
		xmpaMca = (Xmap) createMock(Xmap.class, "xmpaMca");

		i20DetectorPreparer = PowerMockito.mock(I20DetectorPreparer.class);
		List<Detector> detList = new ArrayList<Detector>();
		detList.add(ionchambers);
		detList.add(xspressSystem);
		detList.add(xmpaMca);
		Mockito.when(i20DetectorPreparer.getDetectors()).thenReturn(detList);

		thePreparer = new I20OutputPreparer(datawriterconfig, datawriterconfig_xes, metashop, ionchambers,
				xmpaMca, i20DetectorPreparer);
		thePreparer.setDatawriterconfig(datawriterconfig);

	}

	private Scannable createMock(Class<? extends Scannable> clazz, String name) {
		Scannable newMock = PowerMockito.mock(clazz);
		Mockito.when(newMock.getName()).thenReturn(name);
		return newMock;
	}

	@Test
	public void testConfigureOptionsTrue() throws DeviceException {
		XanesScanParameters scanBean = I20PreparersTestUtils.createXanesBean();

		I20OutputParameters outputBean = new I20OutputParameters();
		outputBean.setXspressOnlyShowFF(true);
		outputBean.setXspressSaveRawSpectrum(true);
		outputBean.setXspressShowDTRawValues(true);
		outputBean.setVortexSaveRawSpectrum(true);

		TransmissionParameters transParams = I20PreparersTestUtils.createTransmissionParameters();
		DetectorParameters detBean = new DetectorParameters();
		detBean.setTransmissionParameters(transParams);
		detBean.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

		thePreparer.configure(outputBean, scanBean, detBean, null);

//		Mockito.verify(ionchambers).setOutputLogValues(true);
//		Mockito.verify(xspressSystem).setOnlyDisplayFF(true);
//		Mockito.verify(xspressSystem).setAddDTScalerValuesToAscii(true);
//		Mockito.verify(xspressSystem).setSaveRawSpectrum(true);
		Mockito.verify(xmpaMca).setSaveRawSpectrum(true);

	}

	@Test
	public void testConfigureOptionsFalse() throws DeviceException {
		XanesScanParameters scanBean = I20PreparersTestUtils.createXanesBean();

		I20OutputParameters outputBean = new I20OutputParameters();
		outputBean.setXspressOnlyShowFF(false);
		outputBean.setXspressSaveRawSpectrum(false);
		outputBean.setXspressShowDTRawValues(false);
		outputBean.setVortexSaveRawSpectrum(false);

		TransmissionParameters transParams = I20PreparersTestUtils.createTransmissionParameters();
		DetectorParameters detBean = new DetectorParameters();
		detBean.setTransmissionParameters(transParams);
		detBean.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

		thePreparer.configure(outputBean, scanBean, detBean, null);

//		Mockito.verify(ionchambers).setOutputLogValues(true);
//		Mockito.verify(xspressSystem).setOnlyDisplayFF(false);
//		Mockito.verify(xspressSystem).setAddDTScalerValuesToAscii(false);
//		Mockito.verify(xspressSystem).setSaveRawSpectrum(false);
		Mockito.verify(xmpaMca).setSaveRawSpectrum(false);
	}

	@Test
	public void testGetCorrectWriterConfiguration() {
		XanesScanParameters scanBean = I20PreparersTestUtils.createXanesBean();
		AsciiDataWriterConfiguration configFromXanes = thePreparer.getAsciiDataWriterConfig(scanBean);
		assertTrue(configFromXanes == datawriterconfig);

		XasScanParameters xasScan = new XasScanParameters();
		AsciiDataWriterConfiguration configFromXas = thePreparer.getAsciiDataWriterConfig(xasScan);
		assertTrue(configFromXas == datawriterconfig);

		XesScanParameters xesScan = new XesScanParameters();
		AsciiDataWriterConfiguration configFromXes = thePreparer.getAsciiDataWriterConfig(xesScan);
		assertTrue(configFromXes == datawriterconfig_xes);
	}

	@Test
	public void testGetPlotSettings() throws DeviceException {
		XanesScanParameters scanBean = I20PreparersTestUtils.createXanesBean();

		I20OutputParameters outputBean = new I20OutputParameters();
		outputBean.setXspressOnlyShowFF(true);
		outputBean.setXspressSaveRawSpectrum(false);
		outputBean.setXspressShowDTRawValues(true);
		outputBean.setVortexSaveRawSpectrum(false);

		FluorescenceParameters fluoParams = I20PreparersTestUtils.createGeFluoParameters();
		DetectorParameters detBean = new DetectorParameters();
		detBean.setFluorescenceParameters(fluoParams);
		detBean.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

		thePreparer.configure(outputBean, scanBean, detBean, null);

		ScanPlotSettings sps = thePreparer.getPlotSettings();

		assertTrue(sps != null);


		I20OutputParameters outputBean2 = new I20OutputParameters();
		outputBean2.setXspressOnlyShowFF(false);
		outputBean2.setXspressSaveRawSpectrum(false);
		outputBean2.setXspressShowDTRawValues(false);
		outputBean2.setVortexSaveRawSpectrum(false);

		thePreparer.configure(outputBean2, scanBean, detBean, null);

		ScanPlotSettings sps2 = thePreparer.getPlotSettings();

		assertTrue(sps2 != null);

	}

	@Test
	public void testDoNotGetPLotSettings() throws DeviceException {
		XanesScanParameters scanBean = I20PreparersTestUtils.createXanesBean();

		I20OutputParameters outputBean = new I20OutputParameters();
		outputBean.setXspressOnlyShowFF(true);
		outputBean.setXspressSaveRawSpectrum(false);
		outputBean.setXspressShowDTRawValues(false);
		outputBean.setVortexSaveRawSpectrum(false);

		FluorescenceParameters fluoParams = I20PreparersTestUtils.createGeFluoParameters();
		DetectorParameters detBean = new DetectorParameters();
		detBean.setFluorescenceParameters(fluoParams);
		detBean.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

		thePreparer.configure(outputBean, scanBean, detBean, null);

		ScanPlotSettings sps = thePreparer.getPlotSettings();

		assertTrue(sps == null);


		FluorescenceParameters fluoParams2 = I20PreparersTestUtils.createSiFluoParameters();
		DetectorParameters detBean2 = new DetectorParameters();
		detBean2.setFluorescenceParameters(fluoParams2);
		detBean2.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);

		thePreparer.configure(outputBean, scanBean, detBean2, null);

		ScanPlotSettings sps2 = thePreparer.getPlotSettings();

		assertTrue(sps2 == null);

		TransmissionParameters transParams = I20PreparersTestUtils.createTransmissionParameters();
		DetectorParameters detBean3 = new DetectorParameters();
		detBean3.setTransmissionParameters(transParams);
		detBean3.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);

		thePreparer.configure(outputBean, scanBean, detBean2, null);

		ScanPlotSettings sps3 = thePreparer.getPlotSettings();

		assertTrue(sps3 == null);

	}

}
