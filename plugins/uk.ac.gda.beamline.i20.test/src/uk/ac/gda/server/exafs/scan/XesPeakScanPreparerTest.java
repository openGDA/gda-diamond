/*-
 * Copyright © 2024 Diamond Light Source Ltd.
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
import static org.mockito.ArgumentMatchers.anyDouble;
import static org.mockito.Mockito.never;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Stream;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.mockito.MockedStatic;
import org.mockito.Mockito;

import com.github.tschoonj.xraylib.Xraylib;

import gda.TestHelpers;
import gda.device.Scannable;
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian;
import uk.ac.gda.beans.exafs.ScanColourType;
import uk.ac.gda.beans.exafs.SpectrometerScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.server.exafs.scan.preparers.CurveFitScanRunner;
import uk.ac.gda.server.exafs.scan.preparers.XesPeakScanPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class XesPeakScanPreparerTest {

	private XesPeakScanPreparer preparer;

	private XesScanParameters xesScanParameters;
	private XasScanParameters xasXanesScanParameters;
	private Scannable monoScannable;
	private String dataPath = "/path/to/xml/directory";
	private CurveFitScanRunner[] scanRunners;
	private Scannable[] xesScannables;

	private static MockedStatic<XMLHelpers> xmlHelpers;

	@Before
	public void prepare() throws Exception {
		scanRunners = new CurveFitScanRunner[2];
		xesScannables = new Scannable[2];

		monoScannable = createMockScannable("mono");
		for(int i=0; i<2; i++) {
			xesScannables[i] = createMockScannable("XESEnergy"+i);

			scanRunners[i] = Mockito.mock(CurveFitScanRunner.class);
			Mockito.when(scanRunners[i].getScannableToMove()).thenReturn(xesScannables[i]);
			Mockito.when(scanRunners[i].fitData()).thenReturn(new Gaussian(2000+i, 1, 1));

		}
		setupXesParameters();
		setupPreparer();
		TestHelpers.setUpTest(XesPeakScanPreparer.class, "test", false);
	}

	@BeforeClass
	public static void setupMock() {
		xmlHelpers = Mockito.mockStatic(XMLHelpers.class);
	}

	@AfterClass
	public static void removeMock() {
		xmlHelpers.close();
	}

	private Scannable createMockScannable(String name) {
		Scannable mockScannable = Mockito.mock(Scannable.class);
		Mockito.when(mockScannable.getName()).thenReturn(name);
		return mockScannable;
	}

	public void setupPreparer() {
		preparer = new XesPeakScanPreparer();
		preparer.setMonoScannable(monoScannable);
		preparer.setScanRunners(Arrays.asList(scanRunners));
		preparer.setRunPeakFinding(true);
		preparer.setOneColourXesScannableName("XESEnergy0");
	}

	public void setupXesParameters() throws Exception {
		xesScanParameters = new XesScanParameters();
		List<SpectrometerScanParameters> spectrometerParams = Stream.of(xesScannables)
			.map(scn -> {
				var specParams = new SpectrometerScanParameters();
				specParams.setScannableName(scn.getName());
				specParams.setFixedEnergy(2000.0 + 10*Math.random());
				return specParams;
			}).toList();
		xesScanParameters.setSpectrometerScanParameters(spectrometerParams);
		xesScanParameters.setScanFileName("xas_xanes_file.xml");

		xasXanesScanParameters = new XasScanParameters();
		xasXanesScanParameters.setElement("Mn");
		xasXanesScanParameters.setEdge("K");

		Mockito.when(XMLHelpers.getBeanObject(dataPath, xesScanParameters.getScanFileName())).thenReturn(xasXanesScanParameters);
	}

	private double getEdgeEnergy() {
		return Xraylib.EdgeEnergy(Xraylib.SymbolToAtomicNumber(xasXanesScanParameters.getElement()), Xraylib.K_SHELL)*1000;
	}

	@Test
	public void testRow1OneColour() throws Exception {
		xesScanParameters.setScanColourType(ScanColourType.ONE_COLOUR_ROW1);
		xesScanParameters.setScanType(XesScanParameters.FIXED_XES_SCAN_XAS);

		SpectrometerScanParameters specParams = xesScanParameters.getSpectrometerScanParameters().get(0);
		double xesInitialEnergy = specParams.getFixedEnergy();
		double edgeEnergy = getEdgeEnergy();

		preparer.configure(xesScanParameters, null, null, dataPath);
		preparer.beforeEachRepetition();
		testMocks(0, edgeEnergy, xesInitialEnergy, true);
		assertEquals(specParams.getFixedEnergy().doubleValue(), scanRunners[0].fitData().getPosition(), 1e-6);
	}

	@Test
	public void testRow2OneColour() throws Exception {
		xesScanParameters.setScanColourType(ScanColourType.ONE_COLOUR_ROW2);
		xesScanParameters.setScanType(XesScanParameters.FIXED_XES_SCAN_XAS);

		SpectrometerScanParameters specParams = xesScanParameters.getSpectrometerScanParameters().get(1);
		double xesInitialEnergy = specParams.getFixedEnergy();
		double edgeEnergy = getEdgeEnergy();

		preparer.configure(xesScanParameters, null, null, dataPath);
		preparer.beforeEachRepetition();
		testMocks(1, edgeEnergy, xesInitialEnergy, true);
		assertEquals(specParams.getFixedEnergy().doubleValue(), scanRunners[1].fitData().getPosition(), 1e-6);
	}

	@Test
	public void testRow12OneColour() throws Exception {
		xesScanParameters.setScanColourType(ScanColourType.ONE_COLOUR);
		xesScanParameters.setScanType(XesScanParameters.FIXED_XES_SCAN_XAS);

		SpectrometerScanParameters specParams = xesScanParameters.getSpectrometerScanParameters().get(0);
		double xesInitialEnergy = specParams.getFixedEnergy();
		double edgeEnergy = getEdgeEnergy();

		preparer.configure(xesScanParameters, null, null, dataPath);
		preparer.beforeEachRepetition();
		testMocks(0, edgeEnergy, xesInitialEnergy, true);
		assertEquals(specParams.getFixedEnergy().doubleValue(), scanRunners[0].fitData().getPosition(), 1e-6);
	}

	@Test
	public void testRow12TwoColour() throws Exception {
		xesScanParameters.setScanColourType(ScanColourType.TWO_COLOUR);
		xesScanParameters.setScanType(XesScanParameters.FIXED_XES_SCAN_XAS);

		SpectrometerScanParameters specParams0 = xesScanParameters.getSpectrometerScanParameters().get(0);
		SpectrometerScanParameters specParams1= xesScanParameters.getSpectrometerScanParameters().get(1);

		double xesInitialEnergy1 = specParams0.getFixedEnergy();
		double xesInitialEnergy2 = specParams1.getFixedEnergy();
		double edgeEnergy = getEdgeEnergy();

		preparer.configure(xesScanParameters, null, null, dataPath);
		preparer.beforeEachRepetition();
		var inorder = Mockito.inOrder(monoScannable, scanRunners[0], scanRunners[1]);
		inorder.verify(monoScannable).moveTo(edgeEnergy);
		inorder.verify(scanRunners[0]).runScan(xesInitialEnergy1);
		inorder.verify(scanRunners[0]).fitData();
		inorder.verify(scanRunners[1]).runScan(xesInitialEnergy2);
		inorder.verify(scanRunners[1]).fitData();

		assertEquals(specParams0.getFixedEnergy().doubleValue(), scanRunners[0].fitData().getPosition(), 1e-6);
		assertEquals(specParams1.getFixedEnergy().doubleValue(), scanRunners[1].fitData().getPosition(), 1e-6);
	}

	private void testMocks(int row, double monoEnergy, double intialXesEnergy, boolean ensureNoOtherMoves) throws Exception {
		var inorder = Mockito.inOrder(monoScannable, scanRunners[row]);
		if (monoEnergy > 0) {
			inorder.verify(monoScannable).moveTo(monoEnergy);
		}
		inorder.verify(scanRunners[row]).runScan(intialXesEnergy);
		inorder.verify(scanRunners[row]).fitData();
		inorder.verifyNoMoreInteractions();
		if (ensureNoOtherMoves) {
			for(int i=0; i<scanRunners.length; i++) {
				if(i!=row) {
					Mockito.verify(scanRunners[i], never()).runScan(anyDouble());
				}
			}
		}
	}
}
