/*-
 * Copyright © 2009 Diamond Light Source Ltd., Science and Technology
 * Facilities Council Daresbury Laboratory
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

package gda.analysis.io;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

import org.eclipse.dawnsci.analysis.api.io.ScanFileHolderException;
import org.eclipse.january.IMonitor;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.IntegerDataset;

import gda.util.OSCommandRunner;
import uk.ac.diamond.daq.util.logging.deprecation.DeprecationLogger;
import uk.ac.diamond.scisoft.analysis.io.AbstractFileLoader;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.Utils;

/**
 * Basic file loader for the Pilatus, this works with tiff images created by the 100k and the 2M Pilatuses
 */
public class PilatusLoader extends AbstractFileLoader {

	/**
	 * Setup the logging facilities
	 */
	private static final DeprecationLogger logger = DeprecationLogger.getLogger(PilatusLoader.class);

	/**
	 * @param FileName
	 * @deprecated Use {@link PilatusTiffLoader} or {@link TIFFImageLoader}
	 */
	@Deprecated(since="(at least) 2013")
	public PilatusLoader(String FileName) {
		logger.deprecatedClass(null, "gda.analysis.io.PilatusTiffLoader or gda.analysis.io.TIFFImageLoader");
		fileName = FileName;
	}

	@Override
	protected void clearMetadata() {
	}

	/**
	 * This is the function which load in the tiff file
	 *
	 * @return The holder object which contains the datasets containing the tiff information
	 * @throws ScanFileHolderException
	 */
	@Override
	public DataHolder loadFile() throws ScanFileHolderException {

		// so using the external program to read the file and write it out as binary

		String command = System.getProperty("gda.analysis.io.PilatusLoader.commandPath",
				"/dls_sw/apps/PilatusReader/recent/preader");
		// create the command
		// String command = LocalProperties.get("gda.analysis.io.PilatusLoader.commandPath");
		String tempName = System.getProperty("gda.analysis.io.PilatusLoader.tempFile", "/tmp/temp.dat");
		command += " " + fileName + " " + tempName;

		// run the command, would be nice to not have the files
		OSCommandRunner os = new OSCommandRunner(command, true, null, null);

		// once the command has been run, the produced file needs to be loaded in
		if (os.exception != null)
			throw new ScanFileHolderException("Exception in PilatusLoader.loadFile for file '" + fileName + "'",
					os.exception);
		// Try to load the file
		if (os.exitValue != 0)
			throw new ScanFileHolderException("Failure in PilatusLoader.loadFile for file '" + fileName
					+ "' Exit code =" + os.exitValue);

		try {

			File f = new File(tempName);

			FileInputStream fi = new FileInputStream(f);

			// get the width and height
			int width = Utils.readLeInt(fi);
			int height = Utils.readLeInt(fi);

			int size = height * width;

			int[] dims = { height, width };
			IntegerDataset data = DatasetFactory.zeros(IntegerDataset.class, dims);

			// read in all the data at once for speed.
			byte[] read = new byte[size * 4];

			fi.read(read);

			// and put it into the dataset
			int[] databuf = data.getData();
			for (int i = 0; i < size; i++) {
				int j = 4 * i;
				databuf[i] = Utils.leInt(read[j], read[j + 1], read[j + 2], read[j + 3]);
			}
			data.setDirty();

			// create the holder and then put to the output.
			DataHolder output = new DataHolder();

			output.addDataset("Pilatus_Image", data);

			return output;

		} catch (Exception e) {
			String msg = "PilatusLoader.loadFile failed for file '" + fileName + "'. Temp filename = '" + tempName
					+ "'";
			logger.error(msg);
			String problem = "output from the failed program is := \n";
			for (int i = 0; i <  os.getOutputLines().size(); i++) {
				problem += os.getOutputLines().get(i) + "\n";
			}
			logger.info(problem);
			throw new ScanFileHolderException(msg, e);
		}
	}

	@Override
	public void loadMetadata(IMonitor mon) throws IOException {
	}
}
