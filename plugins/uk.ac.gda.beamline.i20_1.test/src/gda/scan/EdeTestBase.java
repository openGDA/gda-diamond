/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package gda.scan;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.dawnsci.analysis.api.tree.DataNode;
import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DatasetUtils;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.january.dataset.IndexIterator;
import org.mockito.Mockito;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.DeviceException;
import gda.device.MotorException;
import gda.device.detector.DetectorBase;
import gda.device.enumpositioner.DummyEnumPositioner;
import gda.device.motor.DummyMotor;
import gda.device.scannable.ScannableMotor;
import gda.factory.Factory;
import gda.factory.FactoryException;
import gda.factory.Finder;

public class EdeTestBase {

	private static final Logger logger = LoggerFactory.getLogger(EdeTestBase.class);

	public static ScannableMotor createMotor(String name) throws Exception {
		return createMotor(name, 7000.0);
	}

	public static ScannableMotor createMotor(String name, double position) throws Exception {

		ScannableMotor energy_scannable = Mockito.mock(ScannableMotor.class);
		Mockito.when(energy_scannable.getName()).thenReturn(name);
		Mockito.when(energy_scannable.getInputNames()).thenReturn(new String[] { name });
		Mockito.when(energy_scannable.getExtraNames()).thenReturn(new String[] {});
		Mockito.when(energy_scannable.getOutputFormat()).thenReturn(new String[] { "%.2f" });
		Mockito.when(energy_scannable.getPosition()).thenReturn(position);

		return energy_scannable;
	}

	public static ScannableMotor createScannableMotor(String name) throws MotorException, FactoryException {
		DummyMotor dummyMotor = new DummyMotor();
		dummyMotor.setName("dummyMotor");
		dummyMotor.setMinPosition(0);
		dummyMotor.setMaxPosition(100000);
		dummyMotor.setPosition(0);
		dummyMotor.setSpeed(1000000);
		dummyMotor.configure();

		ScannableMotor scnMotor = new ScannableMotor();
		scnMotor.setName(name);
		scnMotor.setMotor(dummyMotor);
		scnMotor.configure();

		return scnMotor;
	}

	/**
	 * Detector that returns values from supplied array/dataset when it is read out.
	 */
	protected class DetectorArrayReadout extends DetectorBase {

		private int positionIndex = 0;
		private IDataset values = null;

		public DetectorArrayReadout(String name, double[] values) {
			setName(name);
			setInputNames(new String[] {name});
			this.values = DatasetFactory.createFromObject(values);
		}

		public DetectorArrayReadout(String name, IDataset values) {
			setName(name);
			setInputNames(new String[] {name});
			this.values = values.clone();
		}

		public IDataset getValues() {
			return values;
		}

		@Override
		public Object readout() throws DeviceException {
			Object val = null;
			int[] dataShape = values.getShape();
			if (dataShape.length==1) {
				val = values.getDouble(positionIndex);
			} else {
				Dataset row = (Dataset) values.getSlice(new int[] {positionIndex, 0}, new int[] {positionIndex+1, dataShape[1]}, null).squeeze();
				val = DatasetUtils.createJavaArray(row);
			}
			positionIndex++;
			return val;
		}

		@Override
		public boolean isBusy() throws DeviceException {
			return false;
		}

		@Override
		public void rawAsynchronousMoveTo(Object position) {
			// Do nothing
		}

		@Override
		public void collectData() throws DeviceException {
			// Do nothing
		}

		@Override
		public int getStatus() throws DeviceException {
			return IDLE;
		}

		@Override
		public boolean createsOwnFiles() throws DeviceException {
			return false;
		}
	}

	protected DummyEnumPositioner createShutter2(){
		DummyEnumPositioner shutter2 = new DummyEnumPositioner();
		shutter2.setName("Shutter");
		shutter2.setPositions(new String[] { "Open", "Close", "Reset" });
		shutter2.setTimeToMove(0);
		return shutter2;
	}

	public static void assertDimensions(IDataset dataset, int[] expectedDims) {
		assertArrayEquals("Shape of "+dataset.getName()+" is not correct", expectedDims,  dataset.getShape());
		logger.info("Shape of {} dataset is ok ", dataset.getName());
	}

	public static void assertDimensions(String filename, String groupName, String dataName, int[] expectedDims) throws NexusException {
		int[] shape = getDataset(filename, groupName, dataName).getShape();
		assertArrayEquals("Shape of "+groupName+"/"+dataName+" is not correct", expectedDims,  shape);
		logger.info("Shape of {}/{} is ok ", groupName, dataName);
	}

	public static GroupNode getGroupNode(String nexusFilename, String groupName) throws NexusException {
		try(NexusFile file = NexusFileHDF5.openNexusFileReadOnly(nexusFilename)) {
			return file.getGroup("/entry1/"+groupName, false);
		}
	}

	public static IDataset getDataset(String nexusFilename, String groupName, String dataName) throws NexusException {
		try(NexusFile file = NexusFileHDF5.openNexusFileReadOnly(nexusFilename)) {
			GroupNode group = file.getGroup("/entry1/"+groupName, false);
			DataNode d = file.getData(group, dataName);
			return d.getDataset().getSlice(null, null, null);
		}catch(NexusException | DatasetException e){
			String msg = "Problem opening nexus data group="+groupName+" data="+dataName;
			throw new NexusException(msg+e);
		}
	}


	protected class RangeValidator {
		private double min, max;
		private boolean checkMin, checkMax;
		public RangeValidator(double min, double max, boolean checkMin, boolean checkMax) {
			this.min = min; this.max = max;
			this.checkMin = checkMin; this.checkMax = checkMax;
		}
		public boolean valueOk(double val) {
			boolean minOk = checkMin ? val>=min : true;
			boolean maxOk = checkMax ? val<=max : true;
			return minOk && maxOk;
		}
		public String info() {
			return "Range : "+min+" (check = "+checkMin+") ... "+max+" (check = "+checkMax+")";
		}
	}

	// Check all values in a Dataset to make sure they are all within expected range
	public static void checkDataValidRange(String filename, String groupName, String dataName, RangeValidator rangeValidator) throws NexusException {
		Dataset dataset = (Dataset) getDataset(filename, groupName, dataName);
		IndexIterator iter=dataset.getIterator();
		while (iter.hasNext()) {
			double val = dataset.getElementDoubleAbs(iter.index);
			String message = "Data value "+val+" not within valid range at index = "+iter.index+"\n"+rangeValidator.info();
			assertTrue(message, rangeValidator.valueOk(val));
		}
		logger.info("Data in {}/{} is ok", groupName, dataName);
	}

	/**
	 * Check that two datasets match - i.e. have same shape and matching content. Relative error in all
	 * numbers in 'actual' data is < 'toleranceFrac'
	 * @param expected
	 * @param actual
	 * @param toleranceFrac
	 */
	public static void assertDatasetsMatch(IDataset expected, IDataset actual, double toleranceFrac) {
		assertArrayEquals(expected.getShape(), actual.getShape());
		int numElements = expected.getShape()[0];
		for(int i=0; i<numElements; i++) {
			double diff = Math.abs(expected.getDouble(i) - actual.getDouble(i));
			if (diff>0 && Math.abs(expected.getDouble(i))>0) {
				diff /= expected.getDouble(i);
			}
			if (Double.isFinite(diff))  {
				assertTrue(Math.abs(diff)<toleranceFrac);
			} else {
				assertTrue(Double.isNaN(expected.getDouble(i)) == Double.isNaN(actual.getDouble(i)));
			}
		}
		logger.info("Datasets {} and {} match ok", expected.getName(), actual.getName());
	}

	public static List<String> getLinesInFile(String filename) throws IOException {
		return Files.readAllLines(Paths.get(filename), Charset.defaultCharset());
	}

	/**
	 * Convert ascii file into list of string arrays. Lines beginning with '#' are ignored.
	 * Each string array is one line of data from the file; each element is content of one column in the row.
	 * @param filename
	 * @return List of String[].
	 * @throws IOException
	 */
	public static List<String[]> getDataFromAsciiFile(String filename) throws IOException {
		List<String> lines = Files.readAllLines(Paths.get(filename), Charset.defaultCharset());
		List<String[]> dataLines = new ArrayList<>();

		for(String line : lines) {
			if (!line.trim().startsWith("#")) {
				dataLines.add(line.trim().split("\\s+"));
			}
		}
		return dataLines;
	}

	public static void testNumberLinesInFile(String filename, int numExpectedLines) throws IOException {
		List<String> lines = Files.readAllLines(Paths.get(filename), Charset.defaultCharset());
		int numDataLines = 0;
		for (String line : lines) {
			if (!line.trim().startsWith("#")) {
				numDataLines++;
			}
		}
		assertEquals(numExpectedLines, numDataLines);
	}

	public static void testNumberColumnsInFile(String filename, int numExpectedColumns) throws FileNotFoundException, IOException {
		List<String> lines = Files.readAllLines(Paths.get(filename), Charset.defaultCharset());
		for (String line : lines) {
			String trimmedLine = line.trim();
			if (!trimmedLine.startsWith("#")) {
				String[] dataParts = trimmedLine.split("\\s+");
				assertEquals(numExpectedColumns, dataParts.length);
			}
		}
	}


	protected String testDir;

	protected void setup(Class<?> classType, String testName) throws Exception {
		/* String testFolder = */TestHelpers.setUpTest(classType, testName, true);
		LocalProperties.setScanSetsScanNumber(true);
		LocalProperties.set("gda.scan.sets.scannumber", "true");
		LocalProperties.set("gda.scanbase.firstScanNumber", "-1");
		LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusDataWriter");
		LocalProperties.set("gda.nexus.createSRS", "false");
		testDir = LocalProperties.getBaseDataDir();
	}

	/**
	 * Setup metaShop and add it to the Finder.
	 */
	protected static void addMetashopToFinder() {
		NXMetaDataProvider metaShop = new NXMetaDataProvider();
		metaShop.setName("metaShop");
		LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, metaShop.getName());
		final Factory factory = TestHelpers.createTestFactory();
		factory.addFindable(metaShop);
		Finder.addFactory(factory);
	}
}
