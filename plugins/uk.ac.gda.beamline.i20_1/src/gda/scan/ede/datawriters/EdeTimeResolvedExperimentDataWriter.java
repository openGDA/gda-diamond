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

package gda.scan.ede.datawriters;

import gda.data.nexus.GdaNexusFile;
import gda.device.detector.StripDetector;
import gda.scan.EdeScan;

import java.io.File;
import java.io.FileWriter;

import org.apache.commons.lang.ArrayUtils;
import org.nexusformat.NXlink;
import org.nexusformat.NexusException;
import org.nexusformat.NexusFile;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public class EdeTimeResolvedExperimentDataWriter extends EdeLinearExperimentAsciiFileWriter {

	public EdeTimeResolvedExperimentDataWriter(EdeScan i0DarkScan, EdeScan i0LightScan, EdeScan iRefScan,
			EdeScan iRefDarkScan, EdeScan itDarkScan, EdeScan[] itScans, EdeScan i0FinalScan, EdeScan iRefFinalScan,
			StripDetector theDetector, String nexusfile) {
		super(i0DarkScan, i0LightScan, iRefScan, iRefDarkScan, itDarkScan, itScans, i0FinalScan, iRefFinalScan,
				theDetector, nexusfile);
	}

	@Override
	protected String createItFile(EdeScan firstI0Scan, EdeScan secondI0Scan, String fileSuffix) throws Exception {

		String filename = determineAsciiFilename(fileSuffix + EdeDataConstants.ASCII_FILE_EXTENSION);
		File asciiFile = new File(filename);
		if (asciiFile.exists()) {
			throw new Exception("File " + filename + " already exists!");
		}
		asciiFile.createNewFile();

		boolean includeRepetitionColumn = itScans.length > 1 ? true : false;

		FileWriter writer = null;
		try {
			writer = new FileWriter(asciiFile);
			log("Writing EDE format ascii file for It data: " + filename);

			writerHeader(writer);
			writeItColumns(writer, includeRepetitionColumn);

			int numberOfSpectra = itScans[0].getNumberOfAvailablePoints();
			double[][] normalisedItSpectra = new double[itScans.length * numberOfSpectra][];
			int absSpectrumIndex = 0;
			for (int repIndex = 0; repIndex < itScans.length; repIndex++) {
				for (int spectrumNum = 0; spectrumNum < numberOfSpectra; spectrumNum++) {
					DoubleDataset normalisedIt = deriveAndWriteItSpectrum(writer, spectrumNum, i0DarkScan, itDarkScan,
							itScans[repIndex], firstI0Scan, secondI0Scan, repIndex, includeRepetitionColumn);
					normalisedItSpectra[absSpectrumIndex] = normalisedIt.getData();
					absSpectrumIndex++;
				}
			}

			writeItToNexus(normalisedItSpectra, fileSuffix, includeRepetitionColumn);

		} finally {
			if (writer != null) {
				writer.close();
			}
		}

		return filename;
	}

	@Override
	protected void writeItToNexus(double[][] normalisedItSpectra, String fileSuffix, boolean includeRepetitionColumn)
			throws NexusException {

		if (nexusfile == null || nexusfile.isEmpty()) {
			return;
		}

		String datagroupname = deriveDatagroupName(fileSuffix);

		GdaNexusFile file = new GdaNexusFile(nexusfile, NexusFile.NXACC_RDWR);
		file.openpath("entry1");

		double[] timeAxis = calculateTimeAxis();
		double[][] groupAxis = calculateGroupAxis();
		// this assumes we are at the top-level so must be done before opening the <datagroupname> group

		file.makegroup(datagroupname, "NXdata");
		file.openpath(datagroupname);

		String axes = includeRepetitionColumn ? "energy:time:cycle" : "energy:time";

		addMultipleSpectra(normalisedItSpectra, file, axes);

		addTimeAxis(timeAxis, file);
		addGroupAxis(groupAxis, file);
		addEnergyLink(file);

		if (includeRepetitionColumn) {
			double[] cycleAxis = calculateCycleAxis();
			file.makedata(EdeDataConstants.CYCLE_COLUMN_NAME, NexusFile.NX_INT32, 1,
					new int[] { normalisedItSpectra.length });
			file.opendata(EdeDataConstants.CYCLE_COLUMN_NAME);
			file.putdata(cycleAxis);
			file.putattr("axis", "1".getBytes(), NexusFile.NX_CHAR);
			file.putattr("primary", "2".getBytes(), NexusFile.NX_CHAR);
			file.closedata();

			file.closegroup(); // move out of <datagroupname> before writing the averaged data
			averageCyclesAndInsert(normalisedItSpectra, datagroupname, file);
			int numberOfSpectraPerCycle = itScans[0].getNumberOfAvailablePoints();
			addTimeAxis(ArrayUtils.subarray(timeAxis, 0, numberOfSpectraPerCycle), file);
			addGroupAxis((double[][]) ArrayUtils.subarray(groupAxis, 0, numberOfSpectraPerCycle), file);
			addEnergyLink(file);
		}

		file.close();
	}

	private void addEnergyLink(GdaNexusFile file) throws NexusException {
		String currentPath = file.getpath();
		file.openpath("/entry1/instrument/" + theDetector.getName() + "/" + EdeDataConstants.ENERGY_COLUMN_NAME);
		NXlink link = file.getdataID();
		file.closegroup();
		file.openpath(currentPath);
		file.makenamedlink("energy", link);
	}
}
