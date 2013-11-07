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

package gda.scan.ede.datawriters;

import gda.device.detector.StripDetector;
import gda.scan.EdeScan;
import gda.scan.ede.EdeExperiment;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import org.apache.commons.io.FilenameUtils;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public class EdeSingleSpectrumAsciiFileWriter extends EdeAsciiFileWriter {

	private final EdeScan i0DarkScan;
	private final EdeScan itDarkScan;
	private final EdeScan i0InitialScan;
	private final EdeScan itScan;
	private String asciiFilename;

	public EdeSingleSpectrumAsciiFileWriter(EdeScan i0InitialScan, EdeScan itScan, EdeScan i0DarkScan,
			EdeScan itDarkScan, StripDetector theDetector) {
		super();
		this.i0InitialScan = i0InitialScan;
		this.itScan = itScan;
		this.i0DarkScan = i0DarkScan;
		this.itDarkScan = itDarkScan;
		this.theDetector = theDetector;
	}

	@Override
	public String writeAsciiFile() throws Exception {
		DoubleDataset i0DarkDataSet = extractDetectorDataSets(theDetector.getName(), i0DarkScan, 0);
		DoubleDataset itDarkDataSet = extractDetectorDataSets(theDetector.getName(), itDarkScan, 0);
		DoubleDataset i0InitialDataSet = extractDetectorDataSets(theDetector.getName(), i0InitialScan, 0);
		DoubleDataset itDataSet = extractDetectorDataSets(theDetector.getName(), itScan, 0);

		determineAsciiFilename();

		File asciiFile = new File(asciiFilename);
		if (asciiFile.exists()) {
			throw new Exception("File " + asciiFilename + " already exists!");
		}

		asciiFile.createNewFile();
		FileWriter writer = new FileWriter(asciiFile);
		log("Writing EDE format ascii file: " + asciiFilename);
		writerHeader(writer);
		writer.write("#" + EdeExperiment.STRIP_COLUMN_NAME + "\t" + EdeExperiment.ENERGY_COLUMN_NAME + "\t" + EdeExperiment.I0_CORR_COLUMN_NAME + "\t"
				+ EdeExperiment.IT_CORR_COLUMN_NAME + "\t" + EdeExperiment.LN_I0_IT_COLUMN_NAME + "\t " + EdeExperiment.I0_RAW_COLUMN_NAME + "\t"
				+ EdeExperiment.IT_RAW_COLUMN_NAME + "\t" + EdeExperiment.I0_DARK_COLUMN_NAME + "\t" + EdeExperiment.IT_DARK_COLUMN_NAME + "\n");
		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
			Double i0Initial = i0InitialDataSet.get(channel);
			Double it = itDataSet.get(channel);

			Double i0DK = i0DarkDataSet.get(channel);
			Double itDK = itDarkDataSet.get(channel);

			Double i0_corrected = i0Initial - i0DK;
			Double it_corrected = it - itDK;

			Double lni0it = calcLnI0It(i0_corrected, it_corrected);

			StringBuffer stringToWrite = new StringBuffer(channel + "\t");
			stringToWrite.append(String.format("%.2f", theDetector.getEnergyForChannel(channel)) + "\t");
			stringToWrite.append(String.format("%.2f", i0_corrected) + "\t");
			stringToWrite.append(String.format("%.2f", it_corrected) + "\t");
			stringToWrite.append(String.format("%.5f", lni0it) + "\t");
			stringToWrite.append(String.format("%.2f", i0Initial) + "\t");
			stringToWrite.append(String.format("%.2f", it) + "\t");
			stringToWrite.append(String.format("%.2f", i0DK) + "\t");
			stringToWrite.append(String.format("%.2f", itDK) + "\t");
			stringToWrite.append("\n");
			writer.write(stringToWrite.toString());
		}
		writer.close();
		return asciiFilename;
	}

	private void writerHeader(FileWriter writer) throws IOException {
		if (!itDarkScan.equals(i0DarkScan)) {
			writer.write("#I0 Dark:" + i0DarkScan.getHeaderDescription());
			writer.write("\n#It Dark:" + itDarkScan.getHeaderDescription());
		} else {
			writer.write("#Dark:" + i0DarkScan.getHeaderDescription());
		}
		writer.write("\n#I0:" + i0InitialScan.getHeaderDescription());
		writer.write("\n#It:" + itScan.getHeaderDescription());
		writer.write("\n");
	}

	public String getAsciiFilename() {
		return asciiFilename;
	}

	private void determineAsciiFilename() {
		// the scans would have created Nexus files, so base an ascii file on this plus any template, if supplied
		String itFilename = itScan.getDataWriter().getCurrentFileName();
		String folder = FilenameUtils.getFullPath(itFilename);
		String filename = FilenameUtils.getBaseName(itFilename);

		if (filenameTemplate != null && !filenameTemplate.isEmpty()) {
			asciiFilename = folder + String.format(filenameTemplate, filename) + ASCII_FILE_EXTENSION;
		} else {
			asciiFilename = folder + filename + ASCII_FILE_EXTENSION;
		}
	}
}
