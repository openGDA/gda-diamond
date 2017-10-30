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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.eclipse.dawnsci.analysis.api.tree.DataNode;
import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.january.dataset.IndexIterator;
import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.enumpositioner.DummyPositioner;
import gda.device.scannable.ScannableMotor;

public class EdeTestBase {

	public static ScannableMotor createMotor(String name) throws Exception {
		return createMotor(name, 7000.0);
	}

	public static ScannableMotor createMotor(String name, double position) throws Exception {

		ScannableMotor energy_scannable = PowerMockito.mock(ScannableMotor.class);
		Mockito.when(energy_scannable.getName()).thenReturn(name);
		Mockito.when(energy_scannable.getInputNames()).thenReturn(new String[] { name });
		Mockito.when(energy_scannable.getExtraNames()).thenReturn(new String[] {});
		Mockito.when(energy_scannable.getOutputFormat()).thenReturn(new String[] { "%.2f" });
		Mockito.when(energy_scannable.getPosition()).thenReturn(position);

		return energy_scannable;
	}

	protected DummyPositioner createShutter2(){
		DummyPositioner shutter2 = new DummyPositioner();
		shutter2.setName("Shutter");
		shutter2.setPositions(new String[]{"In","Out"});
		return shutter2;
	}

	public static void assertDimensions(String filename, String groupName, String dataName, int[] expectedDims) throws NexusException {
		int[] shape = getDataset(filename, groupName, dataName).getShape();
		for (int i = 0; i < expectedDims.length; i++) {
			assertEquals(groupName+"/"+dataName, expectedDims[i], shape[i]);
		}
	}

	public static IDataset getDataset(String nexusFilename, String groupName, String dataName) throws NexusException {
		NexusFile file = NexusFileHDF5.openNexusFileReadOnly(nexusFilename);
		try {
			GroupNode group = file.getGroup("/entry1/"+groupName, false);
			DataNode d = file.getData(group, dataName);
			return d.getDataset().getSlice(null, null, null);
		}catch(NexusException | DatasetException e){
			String msg = "Problem opening nexus data group="+groupName+" data="+dataName;
			throw new NexusException(msg+e);
		}finally {
			file.close();
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
	};

	// Check all values in a Dataset to make sure they are all within expected range
	public static void checkDataValidRange(String filename, String groupName, String dataName, RangeValidator rangeValidator) throws NexusException {
		Dataset dataset = (Dataset) getDataset(filename, groupName, dataName);
		IndexIterator iter=dataset.getIterator();
		while (iter.hasNext()) {
			double val = dataset.getElementDoubleAbs(iter.index);
			String message = "Data value "+val+" not within valid range at index = "+iter.index+"\n"+rangeValidator.info();
			assertTrue(message, rangeValidator.valueOk(val));
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
}
