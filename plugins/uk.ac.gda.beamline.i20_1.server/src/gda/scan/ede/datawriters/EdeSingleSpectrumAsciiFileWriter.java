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

import java.io.File;
import java.io.FileWriter;
import java.util.List;

import org.apache.commons.io.FilenameUtils;
import org.dawnsci.ede.DataFileHelper;
import org.dawnsci.ede.EdeDataConstants;
import org.eclipse.january.dataset.Dataset;

import gda.device.detector.EdeDetector;
import gda.scan.EnergyDispersiveExafsScan;
import gda.scan.ScanDataPoint;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

public class EdeSingleSpectrumAsciiFileWriter extends EdeExperimentDataWriter {

	private final EnergyDispersiveExafsScan i0DarkScan;
	private final EnergyDispersiveExafsScan itDarkScan;
	private final EnergyDispersiveExafsScan i0InitialScan;
	private final EnergyDispersiveExafsScan itScan;
	private String asciiFilename;

	private final EnergyDispersiveExafsScan iRefScan, iRefDarkScan, i0FinalScan, iRefFinalScan;
	protected final EnergyDispersiveExafsScan[] itScans;
	private final String nexusfileName;
	private double accumulationReadoutTime = 0;

	public EdeSingleSpectrumAsciiFileWriter(EnergyDispersiveExafsScan i0InitialScan, EnergyDispersiveExafsScan itScan, EnergyDispersiveExafsScan i0DarkScan,
			EnergyDispersiveExafsScan itDarkScan, EdeDetector theDetector) {
		super(i0DarkScan.extractEnergyDetectorDataSet());
		this.i0DarkScan = i0DarkScan;
		this.itDarkScan = itDarkScan;
		this.i0InitialScan = i0InitialScan;
		this.itScan = itScan;
		this.theDetector = theDetector;
		iRefScan = null; iRefDarkScan = null; i0FinalScan = null; iRefFinalScan = null; nexusfileName = null; itScans = null;
	}

	/**
	 * New constructor - used when updating NeXuS file with processed lnI0It data.
	 * @since 5/2/2016
	 */
	public EdeSingleSpectrumAsciiFileWriter(EnergyDispersiveExafsScan i0DarkScan, EnergyDispersiveExafsScan i0LightScan, EnergyDispersiveExafsScan iRefScan,
			EnergyDispersiveExafsScan iRefDarkScan, EnergyDispersiveExafsScan itDarkScan, EnergyDispersiveExafsScan[] itScans, EnergyDispersiveExafsScan i0FinalScan, EnergyDispersiveExafsScan iRefFinalScan,
			EdeDetector theDetector, String nexusfileName) {
		super(i0DarkScan.extractEnergyDetectorDataSet());
		this.i0DarkScan = i0DarkScan;
		this.itDarkScan = itDarkScan;
		this.iRefScan = iRefScan;
		this.iRefDarkScan = iRefDarkScan;
		i0InitialScan = i0LightScan;
		this.itScans = itScans;
		this.i0FinalScan = i0FinalScan;
		this.iRefFinalScan = iRefFinalScan;
		this.theDetector = theDetector;
		this.nexusfileName = nexusfileName;
		this.theDetector = theDetector;
		itScan = itScans[0];
	}

	@Override
	public String writeDataFile(EdeDetector detector) throws Exception {
		theDetector = detector; // are these not already the same, as set by constructor?
		String asciiName = writeAsciiData();
		if ( nexusfileName != null )
		{
			updateNexusFile(); // update NeXuS file with lnI0It data
		}
		return asciiName;
	}

	/**
	 * Update NeXuS file with lnI0It data by using EdeTimeResolvedExperimentDataWriter.
	 * @throws Exception
	 * @since 5/2/2016
	 */
	private void updateNexusFile() throws Exception {
		EdeTimeResolvedExperimentDataWriter dataWriter = new EdeTimeResolvedExperimentDataWriter( i0DarkScan, i0InitialScan, iRefScan, iRefDarkScan, itDarkScan, itScans,
				i0FinalScan, iRefFinalScan, theDetector, nexusfileName);
		dataWriter.setWriteAsciiData( false ); // Don't write ascii data - single spectrum ascii data is different format and written by this.writeAsciiData().
		dataWriter.setWriteInNewThread( false );
		dataWriter.setSampleDetails(getSampleDetails());
		dataWriter.writeDataFile( theDetector );
	}

	private Dataset getDetectorDataset(EnergyDispersiveExafsScan scan) {
		List<ScanDataPoint> datapoints = scan.getData();
		return ScanDataHelper.extractDetectorDataFromSDP(theDetector.getName(), datapoints.get(0));
	}

	/**
	 * Write Ascii data file with lnI0It and dark current corrected data.
	 * (Refactored from 'writeDataFile')
	 * @since 5/2/2016
	 * @return String with name of Ascii file produced
	 * @throws Exception
	 */
	private String writeAsciiData() throws Exception {
		Dataset i0DarkDataSet = getDetectorDataset(i0DarkScan);
		Dataset itDarkDataSet = getDetectorDataset(itDarkScan);
		Dataset i0InitialDataSet = getDetectorDataset(i0InitialScan);
		Dataset itDataSet = getDetectorDataset(itScan);

		determineFileAsciiFilePath();

		File asciiFile = new File(asciiFilename);
		if (asciiFile.exists()) {
			throw new Exception("File " + asciiFilename + " already exists!");
		}

		asciiFile.createNewFile();
		FileWriter writer = new FileWriter(asciiFile);
		log("Writing EDE format ascii file: " + asciiFilename);
		writer.write("# " + this.getScannablesConfiguration());
		// Add sample details
		String sampleDetails = this.getSampleDetails();
		if (sampleDetails!=null){
			writer.write("# " + sampleDetails +"\n");
		}
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
		for (int channel = 0; channel < theDetector.getMaxPixel(); channel++) {
			Double i0Initial = i0InitialDataSet.getDouble(channel);
			Double it = itDataSet.getDouble(channel);

			Double i0DK = i0DarkDataSet.getDouble(channel);
			Double itDK = itDarkDataSet.getDouble(channel);

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

	public double getAccumulationReadoutTime() {
		return accumulationReadoutTime;
	}

	public void setAccumulationReadoutTime(double accumulationReadoutTime) {
		this.accumulationReadoutTime = accumulationReadoutTime;
	}

	@Override
	protected EdeDataConstants.TimingGroupMetadata[] createTimingGroupsMetaData(EdeScanParameters scanParameters) {
		return super.createTimingGroupsMetaData(scanParameters, accumulationReadoutTime);
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
