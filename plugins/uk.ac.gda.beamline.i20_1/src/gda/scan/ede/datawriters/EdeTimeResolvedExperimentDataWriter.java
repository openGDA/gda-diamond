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

import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.data.scan.datawriter.AsciiMetadataConfig;
import gda.data.scan.datawriter.FindableAsciiDataWriterConfiguration;
import gda.device.detector.StripDetector;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.scan.EdeScan;
import gda.scan.ScanDataPoint;
import gda.scan.ede.datawriters.EdeDataConstants.TimingGroupMetaData;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.ArrayUtils;
import org.dawnsci.plotting.tools.profile.DataFileHelper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class EdeTimeResolvedExperimentDataWriter extends EdeExperimentDataWriter {

	private static final Logger logger = LoggerFactory.getLogger(EdeTimeResolvedExperimentDataWriter.class);

	public static final String NXDATA_LN_I0_IT_WITH_AVERAGED_I0 = "LnI0It_withAveragedI0";
	public static final String NXDATA_LN_I0_IT_WITH_FINAL_I0 = "LnI0It_withFinalI0";
	public static final String NXDATA_LN_I0_IT = "LnI0It";
	public static final String NXDATA_CYCLE_LN_I0_IT_WITH_AVERAGED = "LnI0It_averaged";

	public static final String IT_RAW_AVERAGEDI0_SUFFIX = "_It_raw_averagedi0";
	public static final String IT_RAW_FINALI0_SUFFIX = "_It_raw_finali0";
	public static final String IT_RAW_SUFFIX = "_It_raw";

	protected final EdeScan i0DarkScan;
	protected final EdeScan i0InitialLightScan;
	protected final EdeScan iRefDarkScan;
	protected final EdeScan iRefScan;
	protected final EdeScan itDarkScan;
	protected final EdeScan[] itScans; // one of these for each cycle (repetition)
	protected final EdeScan i0FinalLightScan;
	protected final EdeScan iRefFinalScan;

	private String i0Filename;
	private String iRefFilename;
	private String itFilename;
	private String itAveragedFilename;
	private String itFinalFilename;

	private final String nexusfileName;
	//private final TimeResolvedNexusFileHelper timeResolvedNexusFileHelper;

	public EdeTimeResolvedExperimentDataWriter(EdeScan i0DarkScan, EdeScan i0LightScan, EdeScan iRefScan,
			EdeScan iRefDarkScan, EdeScan itDarkScan, EdeScan[] itScans, EdeScan i0FinalScan, EdeScan iRefFinalScan,
			StripDetector theDetector, String nexusfileName) {
		super(i0DarkScan.extractEnergyDetectorDataSet());
		this.i0DarkScan = i0DarkScan;
		i0InitialLightScan = i0LightScan;
		this.iRefScan = iRefScan;
		this.iRefDarkScan = iRefDarkScan;
		this.itDarkScan = itDarkScan;
		this.itScans = itScans;
		i0FinalLightScan = i0FinalScan;
		this.iRefFinalScan = iRefFinalScan;
		this.theDetector = theDetector;
		this.nexusfileName = nexusfileName;
	}

	/**
	 * This method creates more than one ascii file. The filename it returns is for the It data.
	 */
	@Override
	public String writeDataFile() throws Exception {
		// it will be assumed that there is an I0 spectrum in both the initial and final data for every timing group in
		// the itData.
		validateData();
		//createI0File();
		TimeResolvedDataFileHelper timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(nexusfileName);

		// Writing out meta data
		TimingGroupMetaData[] i0ScanMetaData = createTimingGroupsMetaData(i0InitialLightScan.getScanParameters());
		TimingGroupMetaData[] itScanMetaData = createTimingGroupsMetaData(itScans[0].getScanParameters());
		TimingGroupMetaData[] irefScanMetaData = null;
		if (iRefScan != null) {
			irefScanMetaData = createTimingGroupsMetaData(iRefScan.getScanParameters());
		}
		// FIXME
		TimingGroupMetaData[] i0ForIRefScanMetaData = null;

		String scannablesConfiguration = getScannablesConfiguration();
		String energyCalibration = null;
		if (itScans[0].getDetector().isEnergyCalibrationSet()) {
			energyCalibration = itScans[0].getDetector().getEnergyCalibration().toString();
		}
		timeResolvedNexusFileHelper.createMetaDataEntries(i0ScanMetaData, itScanMetaData, i0ForIRefScanMetaData, irefScanMetaData, scannablesConfiguration, energyCalibration);

		timeResolvedNexusFileHelper.updateWithNormalisedData(true);

		return itFilename;
	}

	// FIXME
	private String getScannablesConfiguration() {
		ArrayList<Findable> configs = Finder.getInstance().listAllObjects(FindableAsciiDataWriterConfiguration.class.getSimpleName());
		if (configs == null) {
			return "";
		}
		StringBuilder configBuilder = new StringBuilder();
		try {
			if (!configs.isEmpty()) {
				AsciiDataWriterConfiguration config = (AsciiDataWriterConfiguration) configs.get(0);
				for (AsciiMetadataConfig line : config.getHeader()) {
					configBuilder.append(config.getCommentMarker() + " " + line.toString() + "\n");
				}
			}
		} catch (Exception e) {
			logger.error("Unable to get scannable configuration information", e);
		}
		return configBuilder.toString();
	}

	private EdeDataConstants.TimingGroupMetaData[] createTimingGroupsMetaData(EdeScanParameters scanParameters) {
		TimingGroupMetaData[] metaData = new TimingGroupMetaData[scanParameters.getGroups().size()];
		for (int i = 0; i < scanParameters.getGroups().size(); i++) {
			TimingGroup group = scanParameters.getGroups().get(i);
			metaData[i] = new TimingGroupMetaData(i, group.getNumberOfFrames(), group.getTimePerScan(),
					group.getTimePerFrame(), group.getPreceedingTimeDelay(), group.getNumberOfScansPerFrame());
		}
		return metaData;
	}

	private void validateData() throws Exception {
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

	private void createI0File() throws Exception {

		i0Filename = determineAsciiFilename("_I0_raw" + EdeDataConstants.ASCII_FILE_EXTENSION);
		File asciiFile = new File(i0Filename);
		if (asciiFile.exists()) {
			throw new Exception("File " + i0Filename + " already exists!");
		}
		asciiFile.createNewFile();

		FileWriter writer = null;
		try {
			writer = new FileWriter(asciiFile);
			log("Writing EDE format ascii file for I0 data: " + i0Filename);
			writerHeader(writer);
			writer.write("# Before_It\t" + EdeDataConstants.TIMINGGROUP_COLUMN_NAME + "\t"
					+ EdeDataConstants.STRIP_COLUMN_NAME + "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t"
					+ EdeDataConstants.I0_CORR_COLUMN_NAME + "\t" + EdeDataConstants.I0_RAW_COLUMN_NAME + "\t"
					+ EdeDataConstants.I0_DARK_COLUMN_NAME + "\n");
			int numberOfTimingGroups = getNumberOfTimingGroups();
			for (int timingGroup = 0; timingGroup < numberOfTimingGroups; timingGroup++) {
				DoubleDataset i0DarkDataSet = i0DarkScan.extractDetectorDataSet(timingGroup);
				DoubleDataset i0LightDataSet = i0InitialLightScan.extractDetectorDataSet(timingGroup);
				writeI0Spectrum(writer, timingGroup, i0DarkDataSet, i0LightDataSet, true);
			}
			for (int timingGroup = 0; timingGroup < numberOfTimingGroups; timingGroup++) {
				DoubleDataset i0DarkDataSet = i0DarkScan.extractDetectorDataSet(timingGroup);
				DoubleDataset i0FinalDataSet = i0FinalLightScan.extractDetectorDataSet(timingGroup);
				writeI0Spectrum(writer, timingGroup, i0DarkDataSet, i0FinalDataSet, false);
			}
		} finally {
			if (writer != null) {
				writer.close();
			}
		}
	}

	private void writerHeader(FileWriter writer) throws IOException {
		writeScan(writer, i0DarkScan, "Dark");
		if (iRefScan != null) {
			writeScan(writer, iRefScan, "IRef");
		}
		writeScan(writer, i0InitialLightScan, "I0");
		writeScan(writer, itScans[0], "It");
	}

	private void writeScan(FileWriter writer, EdeScan scan, String scanTitle) throws IOException {
		writer.write("#" + scanTitle + ":");
		writer.write(scan.getHeaderDescription());
		writer.write("\n");
	}

	private void writeI0Spectrum(FileWriter writer, int timingGroup, DoubleDataset i0DarkDataSet,
			DoubleDataset i0DataSet, boolean beforeIt) throws IOException {

		int i0_type_label = beforeIt ? 1 : 0;

		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
			Double i0Raw = i0DataSet.get(channel);
			Double i0DK = i0DarkDataSet.get(channel);
			Double i0_corrected = i0Raw - i0DK;

			StringBuffer stringToWrite = new StringBuffer(i0_type_label + "\t" + timingGroup + "\t" + channel + "\t");
			stringToWrite.append(String.format("%.2f", energyDataSet.getDouble(channel)) + "\t");
			stringToWrite.append(String.format("%.2f", i0_corrected) + "\t");
			stringToWrite.append(String.format("%.2f", i0Raw) + "\t");
			stringToWrite.append(String.format("%.2f", i0DK) + "\n");
			writer.write(stringToWrite.toString());
		}
	}

	private double[] writeIRefSpectrum(FileWriter writer, int timingGroup, DoubleDataset i0DataSet,
			DoubleDataset iRefDataSet, DoubleDataset i0DarkDataSet, DoubleDataset iRefDarkDataSet) throws IOException {

		double[] normalisedIRef = new double[theDetector.getNumberChannels()];

		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
			Double i0Raw = i0DataSet.get(channel);
			Double i0DK = i0DarkDataSet.get(channel);
			Double iRef = iRefDataSet.get(channel);
			Double iRefDK = iRefDarkDataSet.get(channel);
			Double i0_corrected = i0Raw - i0DK;
			Double iRef_corrected = iRef - iRefDK;
			Double lni0iref = calcLnI0It(i0_corrected, iRef_corrected);
			normalisedIRef[channel] = lni0iref;

			StringBuffer stringToWrite = new StringBuffer(timingGroup + "\t" + channel + "\t");
			stringToWrite.append(String.format("%.2f", energyDataSet.getDouble(channel)) + "\t");
			stringToWrite.append(String.format("%.2f", lni0iref) + "\n");
			writer.write(stringToWrite.toString());
		}
		return normalisedIRef;
	}


	private void createIRefFile() throws Exception {
		//		iRefFilename = determineAsciiFilename("_IRef" + EdeDataConstants.ASCII_FILE_EXTENSION);
		//		File asciiFile = new File(iRefFilename);
		//		if (asciiFile.exists()) {
		//			throw new Exception("File " + iRefFilename + " already exists!");
		//		}
		//		asciiFile.createNewFile();
		//
		//		FileWriter writer = null;
		//		try {
		//			writer = new FileWriter(asciiFile);
		//			log("Writing EDE format ascii file for IRef data: " + iRefFilename);
		//			writerHeader(writer);
		//
		//			writer.write("#" + EdeDataConstants.TIMINGGROUP_COLUMN_NAME + "\t" + EdeDataConstants.STRIP_COLUMN_NAME
		//					+ "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t" + EdeDataConstants.LN_I0_IREF_COLUMN_NAME
		//					+ "\n");
		//
		//			DoubleDataset i0DataSet = i0InitialLightScan.extractDetectorDataSet(0);
		//			DoubleDataset i0DarkDataSet = i0DarkScan.extractDetectorDataSet(0);
		//			DoubleDataset iRefDataSet = iRefScan.extractDetectorDataSet(0);
		//			DoubleDataset iRefDarkDataSet = iRefDarkScan.extractDetectorDataSet(0);
		//			double[] normalisedIRefSpectra = writeIRefSpectrum(writer, 0, i0DataSet, iRefDataSet, i0DarkDataSet,
		//					iRefDarkDataSet);
		//			timeResolvedNexusFileHelper.writeIRefToNexus(normalisedIRefSpectra, false);
		//
		//			i0DataSet = i0InitialLightScan.extractDetectorDataSet(0);
		//			i0DarkDataSet = i0DarkScan.extractDetectorDataSet(0);
		//			iRefDataSet = iRefFinalScan.extractDetectorDataSet(0);
		//			iRefDarkDataSet = iRefDarkScan.extractDetectorDataSet(0);
		//			normalisedIRefSpectra = writeIRefSpectrum(writer, 0, i0DataSet, iRefDataSet, i0DarkDataSet, iRefDarkDataSet);
		//			timeResolvedNexusFileHelper.writeIRefToNexus(normalisedIRefSpectra, true);
		//		} finally {
		//			if (writer != null) {
		//				writer.close();
		//			}
		//		}
	}

	private void createItFiles() throws Exception {
		//		double[] timeAxis = calculateTimeAxis();
		//		timeResolvedNexusFileHelper.createTimeAxisDataAndLink(timeAxis);
		//
		//		double[][] groupAxis = calculateGroupAxis();
		//		timeResolvedNexusFileHelper.createGroupAxisDataAndLink(groupAxis);
		//
		//		itFilename = createItFile(i0InitialLightScan, null, IT_RAW_SUFFIX);
		//		itFinalFilename = createItFile(i0FinalLightScan, null, IT_RAW_FINALI0_SUFFIX);
		//		itAveragedFilename = createItFile(i0InitialLightScan, i0FinalLightScan, IT_RAW_AVERAGEDI0_SUFFIX);
	}

	private String createItFile(EdeScan firstI0Scan, EdeScan secondI0Scan, String fileSuffix) throws Exception {
		String filename = determineAsciiFilename(fileSuffix + EdeDataConstants.ASCII_FILE_EXTENSION);
		//		File asciiFile = new File(filename);
		//		if (asciiFile.exists()) {
		//			throw new Exception("File " + filename + " already exists!");
		//		}
		//		asciiFile.createNewFile();
		//
		//		boolean includeRepetitionColumn = itScans.length > 1 ? true : false;
		//
		//		FileWriter writer = null;
		//		try {
		//			writer = new FileWriter(asciiFile);
		//			log("Writing EDE format ascii file for It data: " + filename);
		//
		//			writerHeader(writer);
		//			writeItColumns(writer, includeRepetitionColumn);
		//
		//			int numberOfSpectra = itScans[0].getNumberOfAvailablePoints();
		//			double[][][] normalisedItSpectra = new double[itScans.length][numberOfSpectra][];
		//			for (int repIndex = 0; repIndex < itScans.length; repIndex++) {
		//				for (int spectrumNum = 0; spectrumNum < numberOfSpectra; spectrumNum++) {
		//					DoubleDataset normalisedIt = deriveAndWriteItSpectrum(writer, spectrumNum, i0DarkScan, itDarkScan,
		//							itScans[repIndex], firstI0Scan, secondI0Scan, repIndex, includeRepetitionColumn);
		//					normalisedItSpectra[repIndex][spectrumNum] = normalisedIt.getData();
		//				}
		//			}
		//			timeResolvedNexusFileHelper.updateItDataToNexusFile(normalisedItSpectra, fileSuffix, includeRepetitionColumn);
		//		} catch (Exception ex) {
		//			logger.error("Unable to create data file", ex);
		//		} finally {
		//			if (writer != null) {
		//				writer.close();
		//			}
		//		}
		return filename;
	}


	//
	//	private double[] calculateTimeAxis() {
	//		EdeScanParameters scanParameters = itScans[0].getScanParameters();
	//		double[] timeValues = new double[scanParameters.getTotalNumberOfFrames()];
	//		int timeIndex = 0;
	//		double totalTime = 0;
	//		int numberOfSpectraPerCycle = itScans[0].getNumberOfAvailablePoints();
	//		for (int index = 0; index < numberOfSpectraPerCycle; index++) {
	//			double thisFrameTime = ExperimentLocationUtils.getFrameTime(scanParameters, index);
	//			timeValues[timeIndex] = thisFrameTime + totalTime;
	//			timeIndex++;
	//		}
	//		totalTime += ExperimentLocationUtils.getScanTime(scanParameters);
	//		return timeValues;
	//	}


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
		String timingGroup = sdpString.split(ScanDataPoint.delimiter)[indexOfGroup];
		return Integer.parseInt(timingGroup);
	}

	private int deriveFrameFromSpectrumIndex(int spectrumIndex) {
		ScanDataPoint sdp = itScans[0].getData().get(spectrumIndex);
		String sdpString = sdp.toDelimitedString();
		int indexOfGroup = ArrayUtils.indexOf(sdp.getScannableHeader(), "Frame");
		String timingGroup = sdpString.split(ScanDataPoint.delimiter)[indexOfGroup];
		return Integer.parseInt(timingGroup);
	}

	private DoubleDataset createNormalisedDataset(DoubleDataset i0DarkDataSet, DoubleDataset itDarkDataSet, DoubleDataset i0DataSet, DoubleDataset itDataSet) {
		int channels = itDataSet.getShape()[0];
		DoubleDataset normalisedIt = new DoubleDataset(channels);
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

	//	private DoubleDataset writeItSpectrum(FileWriter writer, int repetitionNumber, int timingGroup, int frameNumber,
	//			DoubleDataset i0DarkDataSet, DoubleDataset itDarkDataSet, DoubleDataset i0DataSet, DoubleDataset itDataSet,
	//			boolean includeRepetitionColumn) throws IOException {
	//		DoubleDataset normalisedIt = new DoubleDataset(theDetector.getNumberChannels());
	//		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
	//			Double i0Raw = i0DataSet.get(channel);
	//			Double i0Dark = i0DarkDataSet.get(channel);
	//			Double itRaw = itDataSet.get(channel);
	//			Double itDark = itDarkDataSet.get(channel);
	//			Double i0_corrected = i0Raw - i0Dark;
	//			Double it_corrected = itRaw - itDark;
	//			Double lni0it = calcLnI0It(i0_corrected, it_corrected);
	//			normalisedIt.set(lni0it, channel);

	//			StringBuffer stringToWrite = new StringBuffer();
	//			if (includeRepetitionColumn) {
	//				stringToWrite.append(repetitionNumber + "\t");
	//			}
	//			stringToWrite.append(timingGroup + "\t" + frameNumber + "\t" + channel + "\t");
	//			stringToWrite.append(String.format("%.2f", energyDataSet.getDouble(channel)) + "\t");
	//			stringToWrite.append(String.format("%.2f", it_corrected) + "\t");
	//			stringToWrite.append(String.format("%.2f", lni0it) + "\t");
	//			stringToWrite.append(String.format("%.2f", itRaw) + "\t");
	//			stringToWrite.append(String.format("%.2f", i0Dark) + "\t");
	//			stringToWrite.append(String.format("%.2f", itDark) + "\n");
	//			writer.write(stringToWrite.toString());
	//		}
	//
	//		return normalisedIt;
	//	}

	private String determineAsciiFilename(String suffix) {
		// the scans would have created Nexus files, so base an ascii file on this plus any template, if supplied
		String itFilename = itScans[0].getDataWriter().getCurrentFileName();
		String folder = DataFileHelper.convertFromNexusToAsciiFolder(itFilename);
		String filename = FilenameUtils.getBaseName(itFilename);
		String asciiFilename = folder + filename + suffix;

		if (filenameTemplate != null && !filenameTemplate.isEmpty()) {
			asciiFilename = folder + String.format(filenameTemplate, filename) + suffix;
		}

		return asciiFilename;
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

	private void writeItColumns(FileWriter writer, boolean includeRepetitionColumn) throws IOException {
		StringBuffer colsHeader = new StringBuffer("#");

		if (includeRepetitionColumn) {
			colsHeader.append(EdeDataConstants.CYCLE_COLUMN_NAME + "\t");
		}

		colsHeader.append(EdeDataConstants.TIMINGGROUP_COLUMN_NAME + "\t" + EdeDataConstants.FRAME_COLUMN_NAME + "\t"
				+ EdeDataConstants.STRIP_COLUMN_NAME + "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t"
				+ EdeDataConstants.IT_CORR_COLUMN_NAME + "\t" + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "\t"
				+ EdeDataConstants.IT_RAW_COLUMN_NAME + "\t" + EdeDataConstants.I0_DARK_COLUMN_NAME + "\t"
				+ EdeDataConstants.IT_DARK_COLUMN_NAME + "\n");

		writer.write(colsHeader.toString());
	}
}
