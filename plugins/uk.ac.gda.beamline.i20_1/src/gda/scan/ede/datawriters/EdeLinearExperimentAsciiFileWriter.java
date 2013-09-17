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
import gda.scan.ScanDataPoint;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

import org.apache.commons.io.FilenameUtils;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public class EdeLinearExperimentAsciiFileWriter extends EdeAsciiFileWriter {

	private final EdeScan i0InitialScan;
	private final EdeScan itScan;
	private final EdeScan i0DarkScan;
	private final EdeScan i0FinalScan;
	private String i0Filename;
	private String itFilename;

	public EdeLinearExperimentAsciiFileWriter(EdeScan i0DarkScan, EdeScan i0InitialScan, EdeScan itScan,
			EdeScan i0FinalScan, StripDetector theDetector) {
		this.i0DarkScan = i0DarkScan;
		this.i0InitialScan = i0InitialScan;
		this.itScan = itScan;
		this.i0FinalScan = i0FinalScan;
		this.theDetector = theDetector;
	}

	/**
	 * This method creates more than one ascii file. The filename it returns is for the It data.
	 */
	@Override
	public String writeAsciiFile() throws Exception {
		// it will be assumed that there is an I0 spectrum in both the initial and final data for every timing group in
		// the itData.

		validateData();

		createI0File();

		createItFile();

		return itFilename;
	}

	private void validateData() throws Exception {
		List<ScanDataPoint> i0DarkData = i0DarkScan.getData();
		List<ScanDataPoint> i0InitialData = i0InitialScan.getData();
		List<ScanDataPoint> i0FinalData = i0FinalScan.getData();

		int numberOfTimingGroups = getNumberOfTimingGroups();

		if (numberOfTimingGroups != i0DarkData.size()) {
			throw new Exception(
					"Cannot reduce the data as the number of darks is not the same as the number of timing groups!");
		}
		if (numberOfTimingGroups != i0InitialData.size()) {
			throw new Exception(
					"Cannot reduce the data as the number of I0 spectra is not the same as the number of timing groups!");
		}
		if (numberOfTimingGroups != i0FinalData.size()) {
			throw new Exception(
					"Cannot reduce the data as the number of I0 final spectra is not the same as the number of timing groups!");
		}
	}

	private int getNumberOfTimingGroups() {
		return itScan.getScanParameters().getGroups().size();
	}

	private void createI0File() throws Exception {

		i0Filename = determineAsciiFilename("_I0_raw.txt");
		File asciiFile = new File(i0Filename);
		if (asciiFile.exists()) {
			throw new Exception("File " + i0Filename + " already exists!");
		}
		asciiFile.createNewFile();

		FileWriter writer = null;
		try {
			writer = new FileWriter(asciiFile);
			log("Writing EDE format ascii file for I0 data: " + i0Filename);
			writer.write("# Before_It\t" + TIMINGGROUP_COLUMN_NAME + "\t" + STRIP_COLUMN_NAME + "\t"
					+ ENERGY_COLUMN_NAME + "\t" + I0_CORR_COLUMN_NAME + "\t" + I0_RAW_COLUMN_NAME + "\t"
					+ I0_DARK_COLUMN_NAME + "\n");
			int numberOfTimingGroups = getNumberOfTimingGroups();

			for (int timingGroup = 0; timingGroup < numberOfTimingGroups; timingGroup++) {
				DoubleDataset i0DarkDataSet = extractDetectorDataSets(i0DarkScan, timingGroup);
				DoubleDataset i0InitialDataSet = extractDetectorDataSets(i0InitialScan, timingGroup);
				writeI0Spectrum(writer, timingGroup, i0DarkDataSet, i0InitialDataSet, true);
			}

			for (int timingGroup = 0; timingGroup < numberOfTimingGroups; timingGroup++) {
				DoubleDataset i0DarkDataSet = extractDetectorDataSets(i0DarkScan, timingGroup);
				DoubleDataset i0FinalDataSet = extractDetectorDataSets(i0FinalScan, timingGroup);
				writeI0Spectrum(writer, timingGroup, i0DarkDataSet, i0FinalDataSet, false);
			}

		} finally {
			if (writer != null) {
				writer.close();
			}
		}
	}

	private void writeI0Spectrum(FileWriter writer, int timingGroup, DoubleDataset i0DarkDataSet,
			DoubleDataset i0DataSet, boolean beforeIt) throws IOException {

		int i0_type_label = beforeIt ? 1 : 0;

		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
			Double i0Raw = i0DataSet.get(channel);
			Double i0DK = i0DarkDataSet.get(channel);
			Double i0_corrected = i0Raw - i0DK;

			StringBuffer stringToWrite = new StringBuffer(i0_type_label + "\t" + timingGroup + "\t" + channel + "\t");
			stringToWrite.append(String.format("%.2f", getEnergyForChannel(channel)) + "\t");
			stringToWrite.append(String.format("%.2f", i0_corrected) + "\t");
			stringToWrite.append(String.format("%.2f", i0Raw) + "\t");
			stringToWrite.append(String.format("%.2f", i0DK) + "\n");
			writer.write(stringToWrite.toString());
		}
	}

	private void createItFile() throws Exception {

		itFilename = determineAsciiFilename("_It_raw.txt");
		File asciiFile = new File(itFilename);
		if (asciiFile.exists()) {
			throw new Exception("File " + itFilename + " already exists!");
		}
		asciiFile.createNewFile();

		FileWriter writer = null;
		try {
			writer = new FileWriter(asciiFile);
			log("Writing EDE format ascii file for It data: " + itFilename);
			writer.write("#" + TIMINGGROUP_COLUMN_NAME + "\t" + STRIP_COLUMN_NAME + "\t" + ENERGY_COLUMN_NAME + "\t"
					+ IT_CORR_COLUMN_NAME + "\t" + LN_I0_IT_COLUMN_NAME + "\t" + IT_RAW_COLUMN_NAME + "\t"
					+ IT_DARK_COLUMN_NAME + "\n");
			int numberOfTimingGroups = getNumberOfTimingGroups();

			for (int timingGroup = 0; timingGroup < numberOfTimingGroups; timingGroup++) {
				DoubleDataset darkDataSet = extractDetectorDataSets(i0DarkScan, timingGroup);
				DoubleDataset i0InitialDataSet = extractDetectorDataSets(i0InitialScan, timingGroup);
				DoubleDataset itDataSet = extractDetectorDataSets(itScan, timingGroup);
				writeItSpectrum(writer, timingGroup, darkDataSet, i0InitialDataSet, itDataSet);
			}
		} finally {
			if (writer != null) {
				writer.close();
			}
		}
	}

	private void writeItSpectrum(FileWriter writer, int timingGroup, DoubleDataset darkDataSet,
			DoubleDataset i0DataSet, DoubleDataset itDataSet) throws IOException {

		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
			Double i0Raw = i0DataSet.get(channel);
			Double dark = darkDataSet.get(channel);
			Double itRaw = itDataSet.get(channel);
			Double i0_corrected = i0Raw - dark;
			Double it_corrected = itRaw - dark;
			Double lni0it = calcLnI0It(i0_corrected, it_corrected);

			StringBuffer stringToWrite = new StringBuffer(timingGroup + "\t" + channel + "\t");
			stringToWrite.append(String.format("%.2f", getEnergyForChannel(channel)) + "\t");
			stringToWrite.append(String.format("%.2f", it_corrected) + "\t");
			stringToWrite.append(String.format("%.2f", lni0it) + "\t");
			stringToWrite.append(String.format("%.2f", itRaw) + "\t");
			stringToWrite.append(String.format("%.2f", dark) + "\n");
			writer.write(stringToWrite.toString());
		}
	}

	private String determineAsciiFilename(String suffix) {
		// the scans would have created Nexus files, so base an ascii file on this plus any template, if supplied
		String itFilename = itScan.getDataWriter().getCurrentFileName();
		String folder = FilenameUtils.getFullPath(itFilename);
		String filename = FilenameUtils.getBaseName(itFilename);
		// String suffix = "_I0_raw.txt";

		String asciiFilename = folder + filename + suffix;

		if (filenameTemplate != null && !filenameTemplate.isEmpty()) {
			asciiFilename = folder + String.format(filenameTemplate, filename) + suffix;
		}

		return asciiFilename;
	}

	public String getAsciiI0Filename() {
		return i0Filename;
	}

	public String getAsciiItFilename() {
		return itFilename;
	}

}
