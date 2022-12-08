/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package gda.scan.ede.datawriters;

import static org.dawnsci.ede.EdeDataConstants.DATA_COLUMN_NAME;
import static org.dawnsci.ede.EdeDataConstants.DATA_RAW_COLUMN_NAME;
import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import org.dawnsci.ede.EdeDataConstants;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.january.dataset.BroadcastSelfIterator;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.january.dataset.IndexIterator;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.DeviceException;
import gda.device.detector.DAServer;
import gda.device.detector.xstrip.DummyXStripDAServer;
import gda.device.detector.xstrip.XhDetector;
import gda.device.monitor.DummyMonitor;
import gda.factory.Factory;
import gda.factory.Finder;
import gda.scan.EdeScanTest;
import gda.scan.EdeTestBase;
import gda.scan.ede.TimeResolvedExperiment;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class TimeResolvedDataFileHelperTest extends EdeTestBase {
	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedDataFileHelperTest.class);

	private static final String[] ALL_PROCESSED_DATA_GROUPS = {EdeDataConstants.LN_I0_IT_COLUMN_NAME, EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME,
			EdeDataConstants.LN_I0_IT_FINAL_I0_COLUMN_NAME, EdeDataConstants.LN_I0_IT_INTERP_I0S_COLUMN_NAME };
	private static final int NUM_PIXELS = XhDetector.MAX_PIXEL;
	static final double TOLERANCE = 1e-6;

	private XhDetector xh;

	@Before
	public void setupEnvironment() throws Exception {
		// dummy daserver
		DAServer daserver = new DummyXStripDAServer();
		// detector
		xh = new XhDetector();
		xh.setDaServer(daserver);
		xh.setName("xh");
		xh.setDetectorName("xh0");
		File file = new File(LocalProperties.getVarDir(), "/templates/EdeScan_Parameters.xml");
		xh.setTemplateFileName(file.getAbsolutePath());
		xh.configure();

		// topup monitor
		DummyMonitor topup = new DummyMonitor();
		topup.setName("topup");
		topup.setValue(120.0);

		AsciiDataWriterConfiguration config = new AsciiDataWriterConfiguration();
		config.setName("config");

		final Factory factory = TestHelpers.createTestFactory();
		factory.addFindable(xh);
		factory.addFindable(topup);
		factory.addFindable(config);
		Finder.addFactory(factory);

		LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "");
	}

	@AfterClass
	public static void tearDownClass() {
		// Remove factories from Finder so they do not affect other tests
		Finder.removeAllFactories();
	}

	@Test
	public void testCyclicDataAveragesAreCorrect() throws Exception {
		setup(EdeScanTest.class, "testSimpleCyclicExperiment");

		List<TimingGroup> groups = new ArrayList<>();

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(10);
		group1.setTimePerScan(0.00005);
		group1.setNumberOfScansPerFrame(5);
		groups.add(group1);

		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group2");
		group2.setNumberOfFrames(10);
		group2.setTimePerScan(0.0005);
		group2.setNumberOfScansPerFrame(5);
		groups.add(group2);

		TimingGroup group3 = new TimingGroup();
		group3.setLabel("group3");
		group3.setNumberOfFrames(5);
		group3.setTimePerScan(0.0001);
		group3.setNumberOfScansPerFrame(5);
		groups.add(group3);

		final int numCycles = 3;
		final int numberExpectedSpectra = getNumSpectra(groups);

		TimeResolvedExperiment theExperiment = createExperiment(groups);
		theExperiment.setRepetitions(numCycles);
		theExperiment.runExperiment();

		String fileName = theExperiment.getNexusFilename();
		for(String groupName : ALL_PROCESSED_DATA_GROUPS) {
			checkAveragedDataset(fileName, groupName, numCycles, numberExpectedSpectra);
		}
	}

	@Test
	public void testLogsAreCorrect() throws Exception {
		setup(EdeScanTest.class, "testLogsAreCorrecttestLogsAreCorrect");

		int numSpectra = 1000;
		List<TimingGroup> groups = new ArrayList<>();

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(numSpectra);
		group1.setTimePerScan(0.00005);
		group1.setNumberOfScansPerFrame(5);
		groups.add(group1);

		TimeResolvedExperiment theExperiment = createExperiment(groups);
		theExperiment.runExperiment();

		String fileName = theExperiment.getNexusFilename();
		IDataset rawDetectorData = getDataset(fileName, xh.getName(), DATA_COLUMN_NAME);
		DoubleDataset darkI0 = getSlice(rawDetectorData, 0, 1);
		DoubleDataset darkIt = getSlice(rawDetectorData, 1, 2);
		DoubleDataset lightI0 = getSlice(rawDetectorData, 2, 3);
		DoubleDataset lightIt = getSlice(rawDetectorData, 3, numSpectra+3);

		// Subtract initial darkI0 from lightI0
		lightI0.isubtract(darkI0);

		// Subtract darkIt from lightIt
		lightIt.isubtract(darkIt);

		// Calculate ln(I0/It) and put result in lightIt dataset
		final BroadcastSelfIterator it = BroadcastSelfIterator.createIterator(lightIt, lightI0); // NAN_OMIT
		while(it.hasNext()) {
			double lightItVal = lightIt.getData()[it.aIndex];
			double lightI0Val = it.bDouble;
			double logI0It = Math.log(lightI0Val / lightItVal);
			if (Double.isNaN(logI0It) || Double.isInfinite(logI0It)) {
				logI0It = 0;
			}
			lightIt.getData()[it.aIndex] = logI0It;
		}

		// Check that lnI0It (initial I0) in Nexus file matches calculated result :
		DoubleDataset lnI0ItFromFile = (DoubleDataset) getDataset(fileName, EdeDataConstants.LN_I0_IT_COLUMN_NAME, DATA_COLUMN_NAME);
		checkDatasetsEqual(lightIt, lnI0ItFromFile);
	}

	private TimeResolvedExperiment createExperiment(List<TimingGroup> groups) throws DeviceException {
		TimeResolvedExperiment theExperiment = new TimeResolvedExperiment(0.1, groups, null, null, "xh", "topup", "");
		theExperiment.setUseFastShutter(true);
		theExperiment.setWriteAsciiData(false);
		return theExperiment;
	}

	private DoubleDataset getSlice(IDataset dataset, int startRow, int endRow) {
		int numColumns = dataset.getShape()[1];
		return (DoubleDataset) dataset.getSlice(new int[] {startRow, 0}, new int[] {endRow,numColumns}, null).squeeze();
	}

	private void checkAveragedDataset(String fileName, String groupName, int numCycles, int numberExpectedSpectra) throws NexusException {
		logger.info("Checking average dataset in /entry1/{}", groupName);
		DoubleDataset rawData = (DoubleDataset) getDataset(fileName, groupName, DATA_RAW_COLUMN_NAME);
		DoubleDataset averagedData = (DoubleDataset) getDataset(fileName, groupName, DATA_COLUMN_NAME);
		assertArrayEquals(new int[] {numCycles, numberExpectedSpectra, NUM_PIXELS}, rawData.getShape());
		assertArrayEquals(new int[] {numberExpectedSpectra, NUM_PIXELS}, averagedData.getShape());

		DoubleDataset expectedAverage = computeAverage(rawData);
		checkDatasetsEqual(expectedAverage, averagedData);
	}

	/**
	 * Compute average across several cycles.
	 *
	 * @param rawDataset shape [numCycles, numSpectra, numPixels]
	 * @return
	 */
	private DoubleDataset computeAverage(IDataset rawDataset) {
		logger.info("  Computing average dataset from raw data");
		int[] dataShape = rawDataset.getShape();

		assertEquals("Raw cyclic dataset does not have the correct shape!", 3, dataShape.length);

		int numCycles = dataShape[0];
		int numSpectra = dataShape[1];
		int numPixels = dataShape[2];
		var avgData = DatasetFactory.zeros(numSpectra, numPixels);
		for(int i=0; i<numCycles; i++) {
			var slice = rawDataset.getSliceView(new int[] {i, 0, 0}, new int[] {i+1, numSpectra, numPixels}, null);
			avgData.iadd(slice.squeeze());
		}
		avgData.imultiply(1.0/numCycles);
		return avgData;
	}


	/**
	 * Check that expected and actual datasets have the same values, within absolute tolerance {@link #TOLERANCE}.
	 *
	 * @param expectedData
	 * @param actualData
	 */
	private void checkDatasetsEqual(DoubleDataset expectedData, DoubleDataset actualData) {
		logger.info("  Comparing expected and actual datasets");
		IndexIterator iter = actualData.getIterator();
		IndexIterator iterExp = expectedData.getIterator();
		while(iter.hasNext() && iterExp.hasNext()) {
			double avgVal = actualData.getData()[iter.index];
			double avgValExp = expectedData.getData()[iterExp.index];
			assertEquals("Value not correct for index "+iter.index, avgValExp, avgVal, TOLERANCE);
		}
		logger.info("  Datasets are ok");
	}

	/**
	 *
	 * @param groups list of TimingGroup objects
	 * @return Total number of spectra across list of timing group
	 */
	private int getNumSpectra(List<TimingGroup> groups) {
		int totalNumSpectra = 0;
		for(TimingGroup group : groups) {
			totalNumSpectra += group.getNumberOfFrames();
		}
		return totalNumSpectra;
	}

}
