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

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertSame;

import java.util.ArrayList;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.server.exafs.scan.preparers.I20DetectorPreparer;
import uk.ac.gda.server.exafs.scan.preparers.I20OutputPreparer;

public class I20OutputPreparerTest {

	private AsciiDataWriterConfiguration datawriterconfig_xas;
	private AsciiDataWriterConfiguration datawriterconfig_xes;
	private TfgScalerWithFrames ionchambers;
	private Xspress2Detector xspressSystem;
	private Xmap xmapMca;
	private I20DetectorPreparer i20DetectorPreparer;
	private I20OutputPreparer thePreparer;
	private NXMetaDataProvider metashop;

	@Before
	public void setup() {
//		// mock the metashop and add it to the Finder. Yuck, but then we can see calls to it.
		metashop = Mockito.mock(NXMetaDataProvider.class);

		datawriterconfig_xas = Mockito.mock(AsciiDataWriterConfiguration.class);
		datawriterconfig_xes = Mockito.mock(AsciiDataWriterConfiguration.class);

		ionchambers = (TfgScalerWithFrames) createMock(TfgScalerWithFrames.class, "ionchambers");
		xspressSystem = (Xspress2Detector) createMock(Xspress2Detector.class, "xspressSystem");
		xmapMca = (Xmap) createMock(Xmap.class, "xmapMca");

		i20DetectorPreparer = Mockito.mock(I20DetectorPreparer.class);
		List<Detector> detList = new ArrayList<Detector>();
		detList.add(ionchambers);
		detList.add(xspressSystem);
		detList.add(xmapMca);
		Mockito.when(i20DetectorPreparer.getDetectors()).thenReturn(detList);

		thePreparer = new I20OutputPreparer(datawriterconfig_xas, datawriterconfig_xes, metashop, ionchambers,
				i20DetectorPreparer);
		thePreparer.setXMap(xmapMca);
		thePreparer.setDatawriterconfig(datawriterconfig_xas);
	}

	private Scannable createMock(Class<? extends Scannable> clazz, String name) {
		Scannable newMock = Mockito.mock(clazz);
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
		DetectorParameters detBean = I20PreparersTestUtils.createDetectorParameters(transParams);

		thePreparer.configure(outputBean, scanBean, detBean, null);

//		Mockito.verify(ionchambers).setOutputLogValues(true);
//		Mockito.verify(xspressSystem).setOnlyDisplayFF(true);
//		Mockito.verify(xspressSystem).setAddDTScalerValuesToAscii(true);
//		Mockito.verify(xspressSystem).setSaveRawSpectrum(true);
		Mockito.verify(xmapMca).setSaveRawSpectrum(true);

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
		DetectorParameters detBean = I20PreparersTestUtils.createDetectorParameters(transParams);

		thePreparer.configure(outputBean, scanBean, detBean, null);

//		Mockito.verify(ionchambers).setOutputLogValues(true);
//		Mockito.verify(xspressSystem).setOnlyDisplayFF(false);
//		Mockito.verify(xspressSystem).setAddDTScalerValuesToAscii(false);
//		Mockito.verify(xspressSystem).setSaveRawSpectrum(false);
		Mockito.verify(xmapMca).setSaveRawSpectrum(false);
	}

	@Test
	public void testGetCorrectWriterConfiguration() throws DeviceException {

		I20OutputParameters outputBean = new I20OutputParameters();
		outputBean.setXspressOnlyShowFF(true);
		outputBean.setXspressSaveRawSpectrum(false);
		outputBean.setXspressShowDTRawValues(true);
		outputBean.setVortexSaveRawSpectrum(false);

		TransmissionParameters transParams = I20PreparersTestUtils.createTransmissionParameters();
		DetectorParameters detBean = I20PreparersTestUtils.createDetectorParameters(transParams);

		IScanParameters scanBean = I20PreparersTestUtils.createXanesBean();
		thePreparer.configure(outputBean, scanBean, detBean, null);
		assertSame(datawriterconfig_xas, thePreparer.getAsciiDataWriterConfig(scanBean));

		scanBean = new XasScanParameters();
		thePreparer.configure(outputBean, scanBean, detBean, null);
		assertSame(datawriterconfig_xas, thePreparer.getAsciiDataWriterConfig(scanBean));

		scanBean = new XesScanParameters();
		thePreparer.configure(outputBean, scanBean, detBean, null);
		assertSame(datawriterconfig_xes, thePreparer.getAsciiDataWriterConfig(scanBean));
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
		DetectorParameters detBean = I20PreparersTestUtils.createDetectorParameters(fluoParams);

		thePreparer.configure(outputBean, scanBean, detBean, null);
		assertNotNull(thePreparer.getPlotSettings());

		I20OutputParameters outputBean2 = new I20OutputParameters();
		outputBean2.setXspressOnlyShowFF(false);
		outputBean2.setXspressSaveRawSpectrum(false);
		outputBean2.setXspressShowDTRawValues(false);
		outputBean2.setVortexSaveRawSpectrum(false);

		thePreparer.configure(outputBean2, scanBean, detBean, null);
		assertNotNull(thePreparer.getPlotSettings());
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
		DetectorParameters detBean = I20PreparersTestUtils.createDetectorParameters(fluoParams);
		thePreparer.configure(outputBean, scanBean, detBean, null);
		assertNull(thePreparer.getPlotSettings());

		FluorescenceParameters fluoParams2 = I20PreparersTestUtils.createSiFluoParameters();
		DetectorParameters detBean2 = I20PreparersTestUtils.createDetectorParameters(fluoParams2);
		thePreparer.configure(outputBean, scanBean, detBean2, null);
		assertNull(thePreparer.getPlotSettings());

		TransmissionParameters transParams = I20PreparersTestUtils.createTransmissionParameters();
		DetectorParameters detBean3 = I20PreparersTestUtils.createDetectorParameters(transParams);
		thePreparer.configure(outputBean, scanBean, detBean3, null);
		assertNull(thePreparer.getPlotSettings());
	}

}
