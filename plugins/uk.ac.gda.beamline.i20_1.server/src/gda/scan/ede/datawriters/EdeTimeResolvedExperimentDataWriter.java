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

import java.io.File;
import java.util.List;

import org.apache.commons.lang.ArrayUtils;
import org.dawnsci.ede.DataFileHelper;
import org.dawnsci.ede.EdeDataConstants;
import org.dawnsci.ede.EdeDataConstants.TimingGroupMetadata;
import org.dawnsci.ede.TimeResolvedDataFileHelper;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;

import gda.device.detector.EdeDetector;
import gda.scan.EdeScan;
import gda.scan.EnergyDispersiveExafsScan;
import gda.scan.ScanDataPoint;

public class EdeTimeResolvedExperimentDataWriter extends EdeExperimentDataWriter {

	protected final EnergyDispersiveExafsScan i0DarkScan;
	protected final EnergyDispersiveExafsScan i0InitialLightScan;
	protected final EnergyDispersiveExafsScan iRefDarkScan;
	protected final EnergyDispersiveExafsScan iRefScan;
	protected final EnergyDispersiveExafsScan itDarkScan;
	protected final EnergyDispersiveExafsScan[] itScans; // one of these for each cycle (repetition)
	protected final EnergyDispersiveExafsScan i0FinalLightScan;
	protected final EnergyDispersiveExafsScan iRefFinalScan;

	private String i0Filename;
	private String iRefFilename;
	private String itFilename;
	private String itAveragedFilename;
	private String itFinalFilename;

	private boolean writeAsciiData   = true;
	private boolean writeInNewThread = false;


	public EdeTimeResolvedExperimentDataWriter(EnergyDispersiveExafsScan i0DarkScan, EnergyDispersiveExafsScan i0LightScan, EnergyDispersiveExafsScan iRefScan,
			EnergyDispersiveExafsScan iRefDarkScan, EnergyDispersiveExafsScan itDarkScan, EnergyDispersiveExafsScan[] itScans, EnergyDispersiveExafsScan i0FinalScan, EnergyDispersiveExafsScan iRefFinalScan,
			EdeDetector theDetector, String nexusfileName) {
		super(i0DarkScan.extractEnergyDetectorDataSet(), nexusfileName);
		this.i0DarkScan = i0DarkScan;
		i0InitialLightScan = i0LightScan;
		this.iRefScan = iRefScan;
		this.iRefDarkScan = iRefDarkScan;
		this.itDarkScan = itDarkScan;
		this.itScans = itScans;
		i0FinalLightScan = i0FinalScan;
		this.iRefFinalScan = iRefFinalScan;
		this.theDetector = theDetector;
	}

	/**
	 * This method creates more than one ascii file. The filename it returns is for the It data.
	 */
	@Override
	public String writeDataFile(EdeDetector detector) throws Exception {
		// Writing out meta data
		TimingGroupMetadata[] i0ScanMetaData = createTimingGroupsMetaData(i0InitialLightScan.getScanParameters());
		TimingGroupMetadata[] itScanMetaData = createTimingGroupsMetaData(itScans[0].getScanParameters());
		TimingGroupMetadata[] irefScanMetaData = null;
		if (iRefScan != null) {
			irefScanMetaData = createTimingGroupsMetaData(iRefScan.getScanParameters());
		}
		// FIXME
		TimingGroupMetadata[] i0ForIRefScanMetaData = null;

		String scannablesConfiguration = getScannablesConfiguration();
		if (itScans.length > 1) {
			scannablesConfiguration = scannablesConfiguration + "# Number of cycles: " + itScans.length + "\n";
		}
		String energyCalibration = null;
		if (detector.isEnergyCalibrationSet()) {
			energyCalibration = detector.getEnergyCalibration().toString();
		}

		TimeResolvedDataFileHelper timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(nexusfileName);
		timeResolvedNexusFileHelper.setDetectorName4Node(itScans[0].getDetector().getName());
		timeResolvedNexusFileHelper.createMetaDataEntries(i0ScanMetaData, itScanMetaData, i0ForIRefScanMetaData, irefScanMetaData, scannablesConfiguration, energyCalibration, getSampleDetails());
		if (itScans.length>1) {
			List<Integer> incompleteCycles = getIncompleteCycles(itScans[0].getScanParameters().getTotalNumberOfFrames());
			timeResolvedNexusFileHelper.setIndicesOfExcludedCycles(incompleteCycles);
		}
		timeResolvedNexusFileHelper.updateWithNormalisedData(writeAsciiData);

		addDataForExtraScannables();

		return itFilename;
	}



	private void setAsciiFilenames() {
		File nexusFile = new File(nexusfileName);
		String asciiFolder = DataFileHelper.convertFromNexusToAsciiFolder(nexusfileName);
		i0Filename = asciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.I0_RAW_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);

	}

	private void validateData(EdeDetector detector) throws Exception {
		List<ScanDataPoint> i0DarkData = i0DarkScan.getData();
		List<ScanDataPoint> i0LightData = i0InitialLightScan.getData();
		List<ScanDataPoint> i0FinalData = i0FinalLightScan.getData();

		int numberOfTimingGroups = getNumberOfTimingGroups();

		if (numberOfTimingGroups != i0DarkData.size()) {
			throw new Exception(
					"Cannot reduce the data as the number of darks is not the same as the number of timing groups!");
		}
		if (numberOfTimingGroups != i0LightData.size()) {
			throw new Exception(
					"Cannot reduce the data as the number of I0 spectra is not the same as the number of timing groups!");
		}
		if (numberOfTimingGroups != i0FinalData.size()) {
			throw new Exception(
					"Cannot reduce the data as the number of I0 final spectra is not the same as the number of timing groups!");
		}
	}

	private int getNumberOfTimingGroups() {
		return itScans[0].getScanParameters().getGroups().size();
	}

	public DoubleDataset deriveAndWriteItSpectrum(int spectrumIndex, EdeScan i0DarkScan,
			EdeScan itDarkScan, EdeScan transmissionScan, EdeScan firstI0Scan, EdeScan secondI0Scan) {
		int timingGroupNumber = deriveTimingGroupFromSpectrumIndex(spectrumIndex);
		DoubleDataset i0DarkDataSet = i0DarkScan.extractDetectorDataSet(timingGroupNumber);
		DoubleDataset i0FirstDataSet = firstI0Scan.extractDetectorDataSet(timingGroupNumber);
		DoubleDataset itDarkDataSet = itDarkScan.extractDetectorDataSet(timingGroupNumber);
		DoubleDataset itDataSet = transmissionScan.extractDetectorDataSet(spectrumIndex);
		if (secondI0Scan != null) {
			DoubleDataset i0SecondDataSet = secondI0Scan.extractDetectorDataSet(timingGroupNumber);
			DoubleDataset i0DataSet_averaged = i0FirstDataSet.iadd(i0SecondDataSet).idivide(2);
			i0FirstDataSet = i0DataSet_averaged;
		}
		DoubleDataset normalisedDataset = createNormalisedDataset(i0DarkDataSet, itDarkDataSet, i0FirstDataSet, itDataSet);
		return normalisedDataset;
	}

	private int deriveTimingGroupFromSpectrumIndex(int spectrumIndex) {
		ScanDataPoint sdp = itScans[0].getData().get(spectrumIndex);
		String sdpString = sdp.toDelimitedString();
		int indexOfGroup = ArrayUtils.indexOf(sdp.getScannableHeader(), "Group");
		String timingGroup = sdpString.split(ScanDataPoint.DELIMITER)[indexOfGroup];
		return Integer.parseInt(timingGroup);
	}

	private DoubleDataset createNormalisedDataset(DoubleDataset i0DarkDataSet, DoubleDataset itDarkDataSet, DoubleDataset i0DataSet, DoubleDataset itDataSet) {
		int channels = itDataSet.getShape()[0];
		DoubleDataset normalisedIt = DatasetFactory.zeros(DoubleDataset.class, channels);
		for (int channel = 0; channel < channels; channel++) {
			Double i0Raw = i0DataSet.get(channel);
			Double i0Dark = i0DarkDataSet.get(channel);
			Double itRaw = itDataSet.get(channel);
			Double itDark = itDarkDataSet.get(channel);
			Double i0_corrected = i0Raw - i0Dark;
			Double it_corrected = itRaw - itDark;
			Double lni0it = calcLnI0It(i0_corrected, it_corrected);
			normalisedIt.set(lni0it, channel);
		}
		return normalisedIt;
	}

	public String getAsciiI0Filename() {
		return i0Filename;
	}

	public String getAsciiIRefFilename() {
		return iRefFilename;
	}

	/**
	 * @return full path of the ascii data file of It data derived using the initial I0 data
	 */
	public String getAsciiItFilename() {
		return itFilename;
	}

	/**
	 * @return full path of the ascii data file of It data derived using the final I0 data
	 */
	public String getAsciiItFinalFilename() {
		return itFinalFilename;
	}

	/**
	 * @return full path of the ascii data file of It data derived using an average of the initial and final I0 data
	 */
	public String getAsciiItAveragedFilename() {
		return itAveragedFilename;
	}

	@Override
	public String getAsciiFilename() {
		return this.getAsciiItFilename();
	}

	public boolean getWriteAsciiData() {
		return writeAsciiData;
	}

	public void setWriteAsciiData(boolean writeAsciiData) {
		this.writeAsciiData = writeAsciiData;
	}

	public boolean getWriteInNewThread() {
		return writeInNewThread;
	}

	public void setWriteInNewThread(boolean writeInNewThread) {
		this.writeInNewThread = writeInNewThread;
	}

}
