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
import gda.device.DeviceException;
import gda.device.detector.ExperimentLocationUtils;
import gda.device.detector.StripDetector;
import gda.scan.EdeScan;
import gda.scan.ScanDataPoint;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.ArrayUtils;
import org.nexusformat.NXlink;
import org.nexusformat.NexusException;
import org.nexusformat.NexusFile;
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

	private final String nexusfileName;
	private GdaNexusFile nexusfile;

	protected String i0Filename;
	protected String iRefFilename;
	protected String itFilename;
	protected String itAveragedFilename;
	protected String itFinalFilename;

	private NXlink itGroupDataLink;
	private NXlink itTimeDataLink;
	private NXlink energyDataLink;

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

		nexusfile = new GdaNexusFile(nexusfileName, NexusFile.NXACC_RDWR);

		updateEnergyAndCreateLink();

		createI0File();

		nexusfile.openpath("/entry1");
		createItFiles();

		if (iRefScan != null) {
			createIRefFile();
		}

		nexusfile.closegroup(); // entry 1
		nexusfile.close();
		return itFilename;
	}

	private void updateEnergyAndCreateLink() throws NexusException, DeviceException {
		nexusfile.openpath(getEnergyPath());
		energyDataLink = nexusfile.getdataID();
		updateNexusFileEnergyWithPolynomialValue();
		nexusfile.closegroup();
	}

	private void updateNexusFileEnergyWithPolynomialValue() throws NexusException, DeviceException {
		if (theDetector.getEnergyCalibration() != null) {
			nexusfile.putattr("long_name", theDetector.getEnergyCalibration().toString().getBytes(), NexusFile.NX_CHAR);
		}
	}

	private String getEnergyPath() {
		return "/entry1/instrument/" + theDetector.getName() + "/" + EdeDataConstants.ENERGY_COLUMN_NAME;
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

	private void createIRefFile() throws Exception {
		iRefFilename = determineAsciiFilename("_IRef" + EdeDataConstants.ASCII_FILE_EXTENSION);
		File asciiFile = new File(iRefFilename);
		if (asciiFile.exists()) {
			throw new Exception("File " + iRefFilename + " already exists!");
		}
		asciiFile.createNewFile();

		FileWriter writer = null;
		try {
			writer = new FileWriter(asciiFile);
			log("Writing EDE format ascii file for IRef data: " + iRefFilename);
			writerHeader(writer);

			writer.write("#" + EdeDataConstants.TIMINGGROUP_COLUMN_NAME + "\t" + EdeDataConstants.STRIP_COLUMN_NAME
					+ "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t" + EdeDataConstants.LN_I0_IREF_COLUMN_NAME
					+ "\n");

			DoubleDataset i0DataSet = i0InitialLightScan.extractDetectorDataSet(0);
			DoubleDataset i0DarkDataSet = i0DarkScan.extractDetectorDataSet(0);
			DoubleDataset iRefDataSet = iRefScan.extractDetectorDataSet(0);
			DoubleDataset iRefDarkDataSet = iRefDarkScan.extractDetectorDataSet(0);
			double[] normalisedIRefSpectra = writeIRefSpectrum(writer, 0, i0DataSet, iRefDataSet, i0DarkDataSet,
					iRefDarkDataSet);

			writeIRefToNexus(normalisedIRefSpectra, false);

			i0DataSet = i0InitialLightScan.extractDetectorDataSet(0);
			i0DarkDataSet = i0DarkScan.extractDetectorDataSet(0);
			iRefDataSet = iRefFinalScan.extractDetectorDataSet(0);
			iRefDarkDataSet = iRefDarkScan.extractDetectorDataSet(0);
			normalisedIRefSpectra = writeIRefSpectrum(writer, 0, i0DataSet, iRefDataSet, i0DarkDataSet, iRefDarkDataSet);
			writeIRefToNexus(normalisedIRefSpectra, true);
		} finally {
			if (writer != null) {
				writer.close();
			}
		}
	}

	private void writeIRefToNexus(double[] normalisedIRefSpectra, boolean isFinalSpectrum) throws NexusException {

		String datagroupname = isFinalSpectrum ? "LnI0IRef_Final" : "LnI0IRef";

		nexusfile.makegroup(datagroupname, "NXdata");
		nexusfile.openpath(datagroupname);

		addSingleSpectrum(normalisedIRefSpectra, EdeDataConstants.ENERGY_COLUMN_NAME);

		addEnergyLink();
		nexusfile.closegroup(); // For datagroupname
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

	private void createItFiles() throws Exception {
		double[] timeAxis = calculateTimeAxis();
		addTimeAxisDataAndCreateLink(timeAxis);

		double[][] groupAxis = calculateGroupAxis();
		addGroupAxisDataAndCreateLink(groupAxis);

		itFilename = createItFile(i0InitialLightScan, null, IT_RAW_SUFFIX);
		itFinalFilename = createItFile(i0FinalLightScan, null, IT_RAW_FINALI0_SUFFIX);
		itAveragedFilename = createItFile(i0InitialLightScan, i0FinalLightScan, IT_RAW_AVERAGEDI0_SUFFIX);
	}

	private void addGroupAxisDataAndCreateLink(double[][] groupAxis) throws NexusException {
		nexusfile.makedata(EdeDataConstants.TIMINGGROUP_COLUMN_NAME, NexusFile.NX_FLOAT64, 2, new int[] { groupAxis.length,
				groupAxis[0].length });
		nexusfile.opendata(EdeDataConstants.TIMINGGROUP_COLUMN_NAME);
		itGroupDataLink = nexusfile.getdataID();
		nexusfile.putdata(groupAxis);
		nexusfile.closedata();
	}

	private void addTimeAxisDataAndCreateLink(double[] timeAxis) throws NexusException {
		nexusfile.makedata(EdeDataConstants.TIME_COLUMN_NAME, NexusFile.NX_FLOAT64, 1, new int[] { timeAxis.length });
		nexusfile.opendata(EdeDataConstants.TIME_COLUMN_NAME);
		nexusfile.putdata(timeAxis);
		nexusfile.putattr("axis", Integer.toString(1).getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("primary", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("units", "s".getBytes(), NexusFile.NX_CHAR);
		itTimeDataLink = nexusfile.getdataID();
		nexusfile.closedata();
	}

	private double[][] calculateGroupAxis() {

		EdeScanParameters scanParameters = itScans[0].getScanParameters();
		double[][] groupDetailsForEachCycle = new double[scanParameters.getTotalNumberOfFrames()][4];
		double groupIndex = 0;
		int groupDetailsIndex = 0;
		for (TimingGroup group : scanParameters.getGroups()) {
			for (int i = 0; i < group.getNumberOfFrames(); i++) {
				groupDetailsForEachCycle[groupDetailsIndex][0] = groupIndex;
				groupDetailsForEachCycle[groupDetailsIndex][1] = group.getTimePerFrame();
				groupDetailsForEachCycle[groupDetailsIndex][2] = group.getTimePerScan();
				groupDetailsForEachCycle[groupDetailsIndex][3] = group.getPreceedingTimeDelay();
				groupDetailsIndex++;
			}
			groupIndex++;
		}
		return groupDetailsForEachCycle;
	}

	private double[] calculateTimeAxis() {
		EdeScanParameters scanParameters = itScans[0].getScanParameters();
		double[] timeValues = new double[scanParameters.getTotalNumberOfFrames()];
		int timeIndex = 0;
		double totalTime = 0;
		int numberOfSpectraPerCycle = itScans[0].getNumberOfAvailablePoints();
		for (int index = 0; index < numberOfSpectraPerCycle; index++) {
			double thisFrameTime = ExperimentLocationUtils.getFrameTime(scanParameters, index);
			timeValues[timeIndex] = thisFrameTime + totalTime;
			timeIndex++;
		}
		totalTime += ExperimentLocationUtils.getScanTime(scanParameters);
		return timeValues;
	}

	private void writeItColumns(FileWriter writer, boolean includeRepetitionColumn) throws IOException {
		StringBuffer colsHeader = new StringBuffer("#");

		if (includeRepetitionColumn) {
			colsHeader.append(EdeDataConstants.REP_COLUMN_NAME + "\t");
		}

		colsHeader.append(EdeDataConstants.TIMINGGROUP_COLUMN_NAME + "\t" + EdeDataConstants.FRAME_COLUMN_NAME + "\t"
				+ EdeDataConstants.STRIP_COLUMN_NAME + "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t"
				+ EdeDataConstants.IT_CORR_COLUMN_NAME + "\t" + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "\t"
				+ EdeDataConstants.IT_RAW_COLUMN_NAME + "\t" + EdeDataConstants.I0_DARK_COLUMN_NAME + "\t"
				+ EdeDataConstants.IT_DARK_COLUMN_NAME + "\n");

		writer.write(colsHeader.toString());
	}

	private String deriveDatagroupName(String fileSuffix) {
		String datagroupname = "";
		switch (fileSuffix) {
		case IT_RAW_AVERAGEDI0_SUFFIX:
			datagroupname = NXDATA_LN_I0_IT_WITH_AVERAGED_I0;
			break;
		case IT_RAW_FINALI0_SUFFIX:
			datagroupname = NXDATA_LN_I0_IT_WITH_FINAL_I0;
			break;
		case IT_RAW_SUFFIX:
			datagroupname = NXDATA_LN_I0_IT;
			break;
		}
		return datagroupname;
	}

	private DoubleDataset deriveAndWriteItSpectrum(FileWriter writer, int spectrumIndex, EdeScan i0DarkScan,
			EdeScan itDarkScan, EdeScan transmissionScan, EdeScan firstI0Scan, EdeScan secondI0Scan,
			int repetitionNumber, boolean includeRepetitionColumn) throws IOException {
		int timingGroupNumber = deriveTimingGroupFromSpectrumIndex(spectrumIndex);
		int frameNumber = deriveFrameFromSpectrumIndex(spectrumIndex);
		DoubleDataset i0DarkDataSet = i0DarkScan.extractDetectorDataSet(timingGroupNumber);
		DoubleDataset i0FirstDataSet = firstI0Scan.extractDetectorDataSet(timingGroupNumber);
		DoubleDataset itDarkDataSet = itDarkScan.extractDetectorDataSet(timingGroupNumber);
		DoubleDataset itDataSet = transmissionScan.extractDetectorDataSet(spectrumIndex);
		if (secondI0Scan != null) {
			DoubleDataset i0SecondDataSet = secondI0Scan.extractDetectorDataSet(timingGroupNumber);
			DoubleDataset i0DataSet_averaged = i0FirstDataSet.iadd(i0SecondDataSet).idivide(2);
			i0FirstDataSet = i0DataSet_averaged;
		}
		return writeItSpectrum(writer, repetitionNumber, timingGroupNumber, frameNumber, i0DarkDataSet, itDarkDataSet,
				i0FirstDataSet, itDataSet, includeRepetitionColumn);
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

	private DoubleDataset writeItSpectrum(FileWriter writer, int repetitionNumber, int timingGroup, int frameNumber,
			DoubleDataset i0DarkDataSet, DoubleDataset itDarkDataSet, DoubleDataset i0DataSet, DoubleDataset itDataSet,
			boolean includeRepetitionColumn) throws IOException {

		DoubleDataset normalisedIt = new DoubleDataset(theDetector.getNumberChannels());
		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
			Double i0Raw = i0DataSet.get(channel);
			Double i0Dark = i0DarkDataSet.get(channel);
			Double itRaw = itDataSet.get(channel);
			Double itDark = itDarkDataSet.get(channel);
			Double i0_corrected = i0Raw - i0Dark;
			Double it_corrected = itRaw - itDark;
			Double lni0it = calcLnI0It(i0_corrected, it_corrected);
			normalisedIt.set(lni0it, channel);

			StringBuffer stringToWrite = new StringBuffer();
			if (includeRepetitionColumn) {
				stringToWrite.append(repetitionNumber + "\t");
			}
			stringToWrite.append(timingGroup + "\t" + frameNumber + "\t" + channel + "\t");
			stringToWrite.append(String.format("%.2f", energyDataSet.getDouble(channel)) + "\t");
			stringToWrite.append(String.format("%.2f", it_corrected) + "\t");
			stringToWrite.append(String.format("%.2f", lni0it) + "\t");
			stringToWrite.append(String.format("%.2f", itRaw) + "\t");
			stringToWrite.append(String.format("%.2f", i0Dark) + "\t");
			stringToWrite.append(String.format("%.2f", itDark) + "\n");
			writer.write(stringToWrite.toString());
		}

		return normalisedIt;
	}


	private String createItFile(EdeScan firstI0Scan, EdeScan secondI0Scan, String fileSuffix) throws Exception {

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
		} catch (Exception ex) {
			logger.error("Unable to create data file", ex);
		} finally {
			if (writer != null) {
				writer.close();
			}
		}

		return filename;
	}

	private void writeItToNexus(double[][] normalisedItSpectra, String fileSuffix, boolean includeRepetitionColumn)
			throws NexusException {

		String datagroupname = deriveDatagroupName(fileSuffix);

		if (includeRepetitionColumn) {
			addCyclicData(normalisedItSpectra, datagroupname);
		} else {
			nexusfile.makegroup(datagroupname, "NXdata");
			nexusfile.openpath(datagroupname);
			addMultipleSpectra(normalisedItSpectra, getAxisText());
			addGroupLink();
			addTimeLink();
			addEnergyLink();
			nexusfile.closegroup();
		}
	}

	private String getAxisText() {
		return EdeDataConstants.ENERGY_COLUMN_NAME + ":" + EdeDataConstants.TIME_COLUMN_NAME;
	}

	private void addCyclicData(double[][] normalisedItSpectra, String datagroupname)
			throws NexusException {

		String avDataGroupName = datagroupname + "_averaged";

		int numberCycles = itScans.length;
		int numberOfSpectraPerCycle = itScans[0].getNumberOfAvailablePoints();
		int numChannelsInMCA = normalisedItSpectra[0].length;
		double[][] averagednormalisedItSpectra = new double[numberOfSpectraPerCycle][numChannelsInMCA]; // spectrum, mca

		double[][][] cyclicNormalisedItSpectra = new double[numberCycles][numberOfSpectraPerCycle][numChannelsInMCA];
		// channel

		for (int cycle = 0; cycle < numberCycles; cycle++) {
			for (int spectrumNum = 0; spectrumNum < numberOfSpectraPerCycle; spectrumNum++) {
				for (int channelIndex = 0; channelIndex < numChannelsInMCA; channelIndex++) {
					int absoulteSpectrumNum = spectrumNum + (cycle * numberOfSpectraPerCycle);
					averagednormalisedItSpectra[spectrumNum][channelIndex] += normalisedItSpectra[absoulteSpectrumNum][channelIndex];
					cyclicNormalisedItSpectra[cycle][spectrumNum][channelIndex] = normalisedItSpectra[absoulteSpectrumNum][channelIndex];
				}
			}
		}

		for (int spectrumNum = 0; spectrumNum < numberOfSpectraPerCycle; spectrumNum++) {
			for (int channelIndex = 0; channelIndex < numChannelsInMCA; channelIndex++) {
				averagednormalisedItSpectra[spectrumNum][channelIndex] /= numberCycles;
			}
		}

		nexusfile.makegroup(datagroupname, "NXdata");
		nexusfile.openpath(datagroupname);
		addCycleMultipleSpectra(cyclicNormalisedItSpectra, getAxisText());
		addGroupLink();
		addTimeLink();
		addEnergyLink();
		nexusfile.closegroup();

		nexusfile.makegroup(avDataGroupName, "NXdata");
		nexusfile.openpath(avDataGroupName);
		addMultipleSpectra(averagednormalisedItSpectra, getAxisText());
		addGroupLink();
		addTimeLink();
		addEnergyLink();
		nexusfile.closegroup();
	}

	private void addGroupLink() throws NexusException {
		nexusfile.makenamedlink(EdeDataConstants.TIMINGGROUP_COLUMN_NAME, itGroupDataLink);
	}

	private void addTimeLink() throws NexusException {
		nexusfile.makenamedlink(EdeDataConstants.TIME_COLUMN_NAME, itTimeDataLink);
	}

	private void addEnergyLink() throws NexusException {
		nexusfile.makenamedlink(EdeDataConstants.ENERGY_COLUMN_NAME, energyDataLink);
	}

	private void addSingleSpectrum(double[] normalisedItSpectra, String axes) throws NexusException {
		nexusfile.makedata(EdeDataConstants.DATA_COLUMN_NAME, NexusFile.NX_FLOAT64, 1,
				new int[] { theDetector.getNumberChannels() });
		nexusfile.opendata(EdeDataConstants.DATA_COLUMN_NAME);
		nexusfile.putdata(normalisedItSpectra);
		nexusfile.putattr("signal", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("interpretation", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("axes", axes.getBytes(), NexusFile.NX_CHAR);
		nexusfile.closedata();
	}

	private void addCycleMultipleSpectra(double[][][] normalisedItSpectra, String axes)
			throws NexusException {
		nexusfile.makedata(EdeDataConstants.DATA_COLUMN_NAME, NexusFile.NX_FLOAT64, 3, new int[] {
				normalisedItSpectra.length, normalisedItSpectra[0].length, theDetector.getNumberChannels() });
		nexusfile.opendata(EdeDataConstants.DATA_COLUMN_NAME);
		nexusfile.putdata(normalisedItSpectra);
		nexusfile.putattr("signal", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("interpretation", "2".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("axes", axes.getBytes(), NexusFile.NX_CHAR);
		nexusfile.closedata();
	}

	private void addMultipleSpectra(double[][] normalisedItSpectra, String axes)
			throws NexusException {
		nexusfile.makedata(EdeDataConstants.DATA_COLUMN_NAME, NexusFile.NX_FLOAT64, 2, new int[] {
				normalisedItSpectra.length, theDetector.getNumberChannels() });
		nexusfile.opendata(EdeDataConstants.DATA_COLUMN_NAME);
		nexusfile.putdata(normalisedItSpectra);
		nexusfile.putattr("signal", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("interpretation", "2".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("axes", axes.getBytes(), NexusFile.NX_CHAR);
		nexusfile.closedata();
	}

	private String determineAsciiFilename(String suffix) {
		// the scans would have created Nexus files, so base an ascii file on this plus any template, if supplied
		String itFilename = itScans[0].getDataWriter().getCurrentFileName();
		String folder = convertFromNexusToAsciiFolder(itFilename);
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

}
