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

package gda.scan.ede;

import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.device.DeviceException;
import gda.device.detector.NXDetectorData;
import gda.device.detector.StripDetector;
import gda.jython.InterfaceProvider;
import gda.scan.ScanDataPoint;

import java.io.File;
import java.io.FileWriter;
import java.util.List;
import java.util.Vector;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public class EdeAsciiFileWriter {

	public static final String STRIP_COLUMN_NAME = "Strip";
	public static final String ENERGY_COLUMN_NAME = "Energy";
	public static final String LN_I0_IT_COLUMN_NAME = "LnI0It";
	public static final String I0_CORR_COLUMN_NAME = "I0_corr";
	public static final String IT_CORR_COLUMN_NAME = "It_corr";
	public static final String I0_RAW_COLUMN_NAME = "I0_raw";
	public static final String IT_RAW_COLUMN_NAME = "It_raw";
	public static final String I0_DARK_COLUMN_NAME = "I0_dark";
	public static final String IT_DARK_COLUMN_NAME = "It_dark";

	private static final Logger logger = LoggerFactory.getLogger(EdeAsciiFileWriter.class);

	private final EdeScan i0DarkScan;
	private final EdeScan itDarkScan;
	private final EdeScan i0InitialScan;
	private final EdeScan itScan;
	private final StripDetector theDetector;
	private String asciiFilename;

	public EdeAsciiFileWriter(EdeScan i0InitialScan, EdeScan itScan, EdeScan i0DarkScan, EdeScan itDarkScan,
			StripDetector theDetector) {
		super();
		this.i0InitialScan = i0InitialScan;
		this.itScan = itScan;
		this.i0DarkScan = i0DarkScan;
		this.itDarkScan = itDarkScan;
		this.theDetector = theDetector;
	}

	public String writeAsciiFile() throws Exception {
		DoubleDataset i0DarkDataSet = extractDetectorDataSets(i0DarkScan);
		DoubleDataset itDarkDataSet = extractDetectorDataSets(itDarkScan);
		DoubleDataset i0InitialDataSet = extractDetectorDataSets(i0InitialScan);
		DoubleDataset itDataSet = extractDetectorDataSets(itScan);

		String itFilename = itScan.getTheScan().getDataWriter().getCurrentFileName();
		String folder = FilenameUtils.getFullPath(itFilename);
		String filename = FilenameUtils.getBaseName(itFilename);

		asciiFilename = folder + filename + ".txt";

		File asciiFile = new File(asciiFilename);
		if (asciiFile.exists()) {
			throw new Exception("File " + asciiFilename + " already exists!");
		}

		asciiFile.createNewFile();
		FileWriter writer = new FileWriter(asciiFile);
		log("Writing EDE format ascii file: "+asciiFilename);
		writer.write("#" + STRIP_COLUMN_NAME + "\t" + ENERGY_COLUMN_NAME + "\t" + I0_CORR_COLUMN_NAME + "\t" + IT_CORR_COLUMN_NAME + "\t" + LN_I0_IT_COLUMN_NAME + "\t " + I0_RAW_COLUMN_NAME + "\t" + IT_RAW_COLUMN_NAME + "\t" + I0_DARK_COLUMN_NAME + "\t" + IT_DARK_COLUMN_NAME + "\n");
		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
			Double i0Initial = i0InitialDataSet.get(channel);
			Double it = itDataSet.get(channel);

			Double i0DK = i0DarkDataSet.get(channel);
			Double itDK = itDarkDataSet.get(channel);

			Double i0_corrected = i0Initial - i0DK;
			Double it_corrected = it - itDK;

			Double lni0it = Math.log(i0_corrected / it_corrected);
			if (lni0it.isNaN() || lni0it.isInfinite() || lni0it < 0.0) {
				lni0it = .0;
			}

			StringBuffer stringToWrite = new StringBuffer(channel + "\t");
			stringToWrite.append(String.format("%.2f",getEnergyForChannel(channel)) + "\t");
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

	public String getAsciiFilename() {
		return asciiFilename;
	}

	private Double getEnergyForChannel(int channel){
		PolynomialFunction function;
		try {
			function = theDetector.getEnergyCalibration();
		} catch (DeviceException e) {
			logger.error("Detector did not supply a calibration.", e);
			return (double) channel;
		}
		return function.value(channel);
	}

	private DoubleDataset extractDetectorDataSets(EdeScan scan) {
		List<ScanDataPoint> sdps = scan.getData();
		Vector<Object> data = sdps.get(0).getDetectorData();
		int detIndex = getIndexOfMyDetector(sdps.get(0));
		NXDetectorData detData = (NXDetectorData) data.get(detIndex);
		NexusGroupData groupData = detData.getData(theDetector.getName(), "data", NexusExtractor.SDSClassName);
		double[] originalData = (double[]) groupData.getBuffer();
		return new DoubleDataset(originalData, originalData.length);
	}

	private int getIndexOfMyDetector(ScanDataPoint scanDataPoint) {
		Vector<String> names = scanDataPoint.getDetectorNames();
		return names.indexOf(theDetector.getName());
	}

	private void log (String message){
		InterfaceProvider.getTerminalPrinter().print(message);
		logger.info(message);
	}


}
