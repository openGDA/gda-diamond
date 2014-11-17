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
import gda.scan.EnergyDispersiveExafsScan;

import java.io.File;
import java.io.FileWriter;

import org.apache.commons.io.FilenameUtils;
import org.dawnsci.plotting.tools.profile.DataFileHelper;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;

public class EdeSingleSpectrumAsciiFileWriter extends EdeExperimentDataWriter {

	private final EnergyDispersiveExafsScan i0DarkScan;
	private final EnergyDispersiveExafsScan itDarkScan;
	private final EnergyDispersiveExafsScan i0InitialScan;
	private final EnergyDispersiveExafsScan itScan;
	private String asciiFilename;

	public EdeSingleSpectrumAsciiFileWriter(EnergyDispersiveExafsScan i0InitialScan, EnergyDispersiveExafsScan itScan, EnergyDispersiveExafsScan i0DarkScan,
			EnergyDispersiveExafsScan itDarkScan, StripDetector theDetector) {
		super(i0DarkScan.extractEnergyDetectorDataSet());
		this.i0InitialScan = i0InitialScan;
		this.itScan = itScan;
		this.i0DarkScan = i0DarkScan;
		this.itDarkScan = itDarkScan;
		this.theDetector = theDetector;
	}

	@Override
	public String writeDataFile() throws Exception {
		// FIXME Check this
		DoubleDataset i0DarkDataSet = i0DarkScan.extractDetectorDataSet(0);
		DoubleDataset itDarkDataSet = itDarkScan.extractDetectorDataSet(0);
		DoubleDataset i0InitialDataSet = i0InitialScan.extractDetectorDataSet(0);
		DoubleDataset itDataSet = itScan.extractDetectorDataSet(0);

		determineFileAsciiFilePath();

		File asciiFile = new File(asciiFilename);
		if (asciiFile.exists()) {
			throw new Exception("File " + asciiFilename + " already exists!");
		}

		asciiFile.createNewFile();
		FileWriter writer = new FileWriter(asciiFile);
		log("Writing EDE format ascii file: " + asciiFilename);
		writer.write("# " + this.getScannablesConfiguration());
		writer.write("# I0 Dark\n");
		writer.write("# " + EdeDataConstants.TimingGroupMetadata.toMetadataString(createTimingGroupsMetaData(i0DarkScan.getScanParameters())[0]));
		writer.write("# I0\n");
		writer.write("# " + EdeDataConstants.TimingGroupMetadata.toMetadataString(createTimingGroupsMetaData(i0InitialScan.getScanParameters())[0]));
		writer.write("# It Dark\n");
		writer.write("# " + EdeDataConstants.TimingGroupMetadata.toMetadataString(createTimingGroupsMetaData(itDarkScan.getScanParameters())[0]));
		writer.write("# It\n");
		writer.write("# " + EdeDataConstants.TimingGroupMetadata.toMetadataString(createTimingGroupsMetaData(itScan.getScanParameters())[0]));
		writer.write("#" + EdeDataConstants.STRIP_COLUMN_NAME + "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t" + EdeDataConstants.I0_CORR_COLUMN_NAME + "\t"
				+ EdeDataConstants.IT_CORR_COLUMN_NAME + "\t" + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "\t " + EdeDataConstants.I0_RAW_COLUMN_NAME + "\t"
				+ EdeDataConstants.IT_RAW_COLUMN_NAME + "\t" + EdeDataConstants.I0_DARK_COLUMN_NAME + "\t" + EdeDataConstants.IT_DARK_COLUMN_NAME + "\n");
		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
			Double i0Initial = i0InitialDataSet.get(channel);
			Double it = itDataSet.get(channel);

			Double i0DK = i0DarkDataSet.get(channel);
			Double itDK = itDarkDataSet.get(channel);

			Double i0_corrected = i0Initial - i0DK;
			Double it_corrected = it - itDK;

			Double lni0it = calcLnI0It(i0_corrected, it_corrected);

			StringBuffer stringToWrite = new StringBuffer(channel + "\t");
			stringToWrite.append(String.format("%.2f", energyDataSet.getDouble(channel)) + "\t");
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

	@Override
	public String getAsciiFilename() {
		return asciiFilename;
	}

	private void determineFileAsciiFilePath() {
		String itFilename = itScan.getDataWriter().getCurrentFileName();
		String folder = DataFileHelper.convertFromNexusToAsciiFolder(itFilename);
		String filename = FilenameUtils.getBaseName(itFilename);
		asciiFilename = String.format("%s%s_%s.%s", folder, filename, EdeDataConstants.LN_I0_IT_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
	}
}
