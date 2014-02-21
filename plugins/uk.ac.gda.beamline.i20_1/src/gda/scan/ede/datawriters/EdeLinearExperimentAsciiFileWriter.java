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

import gda.data.nexus.GdaNexusFile;
import gda.device.detector.ExperimentLocationUtils;
import gda.device.detector.StripDetector;
import gda.scan.EdeScan;
import gda.scan.ScanDataPoint;
import gda.scan.ede.EdeExperiment;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.ArrayUtils;
import org.nexusformat.NexusException;
import org.nexusformat.NexusFile;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class EdeLinearExperimentAsciiFileWriter extends EdeAsciiFileWriter {

	public static final String NXDATA_LN_I0_IT_WITH_AVERAGED_I0 = "LnI0It_withAveragedI0";
	public static final String NXDATA_LN_I0_IT_WITH_FINAL_I0 = "LnI0It_withFinalI0";
	public static final String NXDATA_LN_I0_IT = "LnI0It";
	public static final String IT_RAW_AVERAGEDI0_SUFFIX = "_It_raw_averagedi0";
	public static final String IT_RAW_FINALI0_SUFFIX = "_It_raw_finali0";
	public static final String IT_RAW_SUFFIX = "_It_raw";

	private final EdeScan i0DarkScan;
	private final EdeScan i0InitialLightScan;
	private final EdeScan iRefScan;
	private final EdeScan itDarkScan;
	private final EdeScan[] itScans; // one of these for each cycle (repetition)
	private final EdeScan i0FinalLightScan;
	private final String nexusfile;

	private String i0Filename;
	private String iRefFilename;
	private String itFilename;
	private String itAveragedFilename;
	private String itFinalFilename;

	public EdeLinearExperimentAsciiFileWriter(EdeScan i0DarkScan, EdeScan i0LightScan, EdeScan iRefScan,
			EdeScan itDarkScan, EdeScan[] itScans, EdeScan i0FinalScan, StripDetector theDetector, String nexusfile) {
		super(i0DarkScan.extractEnergyDetectorDataSet());
		this.i0DarkScan = i0DarkScan;
		i0InitialLightScan = i0LightScan;
		this.iRefScan = iRefScan;
		this.itDarkScan = itDarkScan;
		this.itScans = itScans;
		i0FinalLightScan = i0FinalScan;
		this.theDetector = theDetector;
		this.nexusfile = nexusfile;
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

		if (iRefScan != null) {
			createIRefFile();
		}

		createItFiles();

		return itFilename;
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

		i0Filename = determineAsciiFilename("_I0_raw" + ASCII_FILE_EXTENSION);
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
			writer.write("# Before_It\t" + EdeExperiment.TIMINGGROUP_COLUMN_NAME + "\t"
					+ EdeExperiment.STRIP_COLUMN_NAME + "\t" + EdeExperiment.ENERGY_COLUMN_NAME + "\t"
					+ EdeExperiment.I0_CORR_COLUMN_NAME + "\t" + EdeExperiment.I0_RAW_COLUMN_NAME + "\t"
					+ EdeExperiment.I0_DARK_COLUMN_NAME + "\n");
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
		iRefFilename = determineAsciiFilename("_IRef" + ASCII_FILE_EXTENSION);
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

			writer.write("#" + EdeExperiment.TIMINGGROUP_COLUMN_NAME + "\t" + EdeExperiment.STRIP_COLUMN_NAME + "\t"
					+ EdeExperiment.ENERGY_COLUMN_NAME + "\t" + EdeExperiment.LN_I0_IREF_COLUMN_NAME + "\n");
			int numberOfTimingGroups = getNumberOfTimingGroups();
			for (int timingGroup = 0; timingGroup < numberOfTimingGroups; timingGroup++) {
				DoubleDataset i0DataSet = i0InitialLightScan.extractDetectorDataSet(timingGroup);
				DoubleDataset i0DarkDataSet = i0DarkScan.extractDetectorDataSet(timingGroup);
				DoubleDataset i0RefDataSet = iRefScan.extractDetectorDataSet(timingGroup);
				writeIRefSpectrum(writer, timingGroup, i0DataSet, i0RefDataSet, i0DarkDataSet);
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

	private void writeIRefSpectrum(FileWriter writer, int timingGroup, DoubleDataset i0DataSet,
			DoubleDataset iRefDataSet, DoubleDataset i0DarkDataSet) throws IOException {

		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++) {
			Double i0Raw = i0DataSet.get(channel);
			Double i0DK = i0DarkDataSet.get(channel);
			Double iRef = iRefDataSet.get(channel);
			Double i0_corrected = i0Raw - i0DK;
			// Check this is right!
			Double iRef_corrected = iRef - i0DK;
			Double lni0iref = calcLnI0It(i0_corrected, iRef_corrected);

			StringBuffer stringToWrite = new StringBuffer(timingGroup + "\t" + channel + "\t");
			stringToWrite.append(String.format("%.2f", energyDataSet.getDouble(channel)) + "\t");
			stringToWrite.append(String.format("%.2f", lni0iref) + "\n");
			writer.write(stringToWrite.toString());
		}
	}

	private void createItFiles() throws Exception {
		itFilename = createItFile(i0InitialLightScan, null, IT_RAW_SUFFIX);
		itFinalFilename = createItFile(i0FinalLightScan, null, IT_RAW_FINALI0_SUFFIX);
		itAveragedFilename = createItFile(i0InitialLightScan, i0FinalLightScan, IT_RAW_AVERAGEDI0_SUFFIX);
	}

	private String createItFile(EdeScan firstI0Scan, EdeScan secondI0Scan, String fileSuffix) throws Exception {

		String filename = determineAsciiFilename(fileSuffix + ASCII_FILE_EXTENSION);
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

	private double[][] calculateGroupAxis() {

		//
		// double[][] groupDetails = new double[scanParameters.getTotalNumberOfFrames()][4];
		// double groupIndex = 0;
		// int j = 0;
		// for (TimingGroup group : scanParameters.getGroups()) {
		// for (int i = 0; i < group.getNumberOfFrames(); i++) {
		// groupDetails[j][0] = groupIndex;
		// groupDetails[j][1] = group.getTimePerFrame();
		// groupDetails[j][2] = group.getTimePerScan();
		// groupDetails[j][3] = group.getPreceedingTimeDelay();
		// j++;
		// }
		// groupIndex++;
		// }
		// return groupDetails;

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
		if (itScans.length == 1) {
			return groupDetailsForEachCycle;
		}

		double[][] groupDetailsAllCycles = new double[][] {};
		for (int cycle = 0; cycle < itScans.length; cycle++) {
			groupDetailsAllCycles = (double[][]) ArrayUtils.addAll(groupDetailsAllCycles, groupDetailsForEachCycle);
		}
		return groupDetailsAllCycles;
	}

	private double[] calculateTimeAxis() {
		EdeScanParameters scanParameters = itScans[0].getScanParameters();
		double[] timeValues = new double[scanParameters.getTotalNumberOfFrames() * itScans.length];
		int timeIndex = 0;
		double totalTime = 0;
		int numberOfSpectraPerCycle = itScans[0].getNumberOfAvailablePoints();
		for (int cycle = 0; cycle < itScans.length; cycle++) {
			for (int index = 0; index < numberOfSpectraPerCycle; index++) {
				double thisFrameTime = ExperimentLocationUtils.getFrameTime(scanParameters, index);
				timeValues[timeIndex] = thisFrameTime + totalTime;
				timeIndex++;
			}
			totalTime += ExperimentLocationUtils.getScanTime(scanParameters);

		}
		return timeValues;
	}

	private void writeItColumns(FileWriter writer, boolean includeRepetitionColumn) throws IOException {
		StringBuffer colsHeader = new StringBuffer("#");

		if (includeRepetitionColumn) {
			colsHeader.append(EdeExperiment.REP_COLUMN_NAME + "\t");
		}

		colsHeader.append(EdeExperiment.TIMINGGROUP_COLUMN_NAME + "\t" + EdeExperiment.FRAME_COLUMN_NAME + "\t"
				+ EdeExperiment.STRIP_COLUMN_NAME + "\t" + EdeExperiment.ENERGY_COLUMN_NAME + "\t"
				+ EdeExperiment.IT_CORR_COLUMN_NAME + "\t" + EdeExperiment.LN_I0_IT_COLUMN_NAME + "\t"
				+ EdeExperiment.IT_RAW_COLUMN_NAME + "\t" + EdeExperiment.I0_DARK_COLUMN_NAME + "\t"
				+ EdeExperiment.IT_DARK_COLUMN_NAME + "\n");

		writer.write(colsHeader.toString());
	}

	private void writeItToNexus(double[][] normalisedItSpectra, String fileSuffix, boolean includeRepetitionColumn)
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
		double[] energyAxis = extractEnergyAxis(file);

		file.makegroup(datagroupname, "NXdata");
		file.openpath(datagroupname);

		String axes = includeRepetitionColumn ? "energy:time:cycle:group" : "energy:time:group";

		addData(normalisedItSpectra, file, axes);

		addTimeAxis(timeAxis, file);
		addGroupAxis(groupAxis, file);
		addEnergyAxis(energyAxis, file);

		if (includeRepetitionColumn) {
			double[] cycleAxis = calculateCycleAxis();
			file.makedata("cycle", NexusFile.NX_FLOAT64, 1, new int[] { normalisedItSpectra.length });
			file.opendata("cycle");
			file.putdata(cycleAxis);
			file.putattr("axis", "1".getBytes(), NexusFile.NX_CHAR);
			file.putattr("primary", "3".getBytes(), NexusFile.NX_CHAR);
			file.closedata();

			file.closegroup(); // move out of <datagroupname> before writing the averaged data
			averageCyclesAndInsert(normalisedItSpectra, datagroupname, file);
			int numberOfSpectraPerCycle = itScans[0].getNumberOfAvailablePoints();
			addTimeAxis(ArrayUtils.subarray(timeAxis, 0, numberOfSpectraPerCycle), file);
			addGroupAxis((double[][]) ArrayUtils.subarray(groupAxis, 0, numberOfSpectraPerCycle), file);
			addEnergyAxis(energyAxis, file);
		}

		file.close();
	}

	private void addData(double[][] normalisedItSpectra, GdaNexusFile file, String axes) throws NexusException {
		file.makedata("data", NexusFile.NX_FLOAT64, 2,
				new int[] { normalisedItSpectra.length, theDetector.getNumberChannels() });
		file.opendata("data");
		file.putdata(normalisedItSpectra);
		file.putattr("signal", "1".getBytes(), NexusFile.NX_CHAR);
		file.putattr("interpretation", "2".getBytes(), NexusFile.NX_CHAR);
		file.putattr("axes", axes.getBytes(), NexusFile.NX_CHAR);
		file.closedata();
	}

	private void addEnergyAxis(double[] energyAxis, GdaNexusFile file) throws NexusException {
		file.makedata("energy", NexusFile.NX_FLOAT64, 1, new int[] { energyAxis.length });
		file.opendata("energy");
		file.putdata(energyAxis);
		file.putattr("axis", "2".getBytes(), NexusFile.NX_CHAR);
		file.putattr("primary", "1".getBytes(), NexusFile.NX_CHAR);
		file.putattr("units", "eV".getBytes(), NexusFile.NX_CHAR);
		file.closedata();
	}

	private void addGroupAxis(double[][] groupAxis, GdaNexusFile file/* , EdeScanParameters scanParameters */)
			throws NexusException {

		file.makedata("group", NexusFile.NX_FLOAT64, 2, new int[] { groupAxis.length, groupAxis[0].length });
		file.opendata("group");
		file.putdata(groupAxis);
		// file.putattr("axis", "1".getBytes(), NexusFile.NX_CHAR);
		// file.putattr("primary", "2".getBytes(), NexusFile.NX_CHAR);
		file.closedata();
	}

	private void addTimeAxis(double[] timeAxis, GdaNexusFile file) throws NexusException {
		file.makedata("time", NexusFile.NX_FLOAT64, 1, new int[] { timeAxis.length });
		file.opendata("time");
		file.putdata(timeAxis);
		file.putattr("axis", "1".getBytes(), NexusFile.NX_CHAR);
		file.putattr("primary", "1".getBytes(), NexusFile.NX_CHAR);
		file.putattr("units", "s".getBytes(), NexusFile.NX_CHAR);
		file.closedata();
	}

	private double[] calculateCycleAxis() {
		EdeScanParameters scanParameters = itScans[0].getScanParameters();
		double[] cycleAxis = new double[scanParameters.getTotalNumberOfFrames() * itScans.length];

		int axisIndex = 0;
		for (int cycle = 0; cycle < itScans.length; cycle++) {
			for (TimingGroup group : scanParameters.getGroups()) {
				for (int i = 0; i < group.getNumberOfFrames(); i++) {
					cycleAxis[axisIndex] = cycle;
					axisIndex++;
				}
			}
		}

		return cycleAxis;
	}

	private double[] extractEnergyAxis(GdaNexusFile file) throws NexusException {
		file.openpath("/entry1/instrument/" + theDetector.getName() + "/Energy");
		int[] iDim = new int[20];
		int[] iStart = new int[2];
		file.getinfo(iDim, iStart);
		final int rank = iStart[0];
		int[] shape = Arrays.copyOf(iDim, rank);
		DoubleDataset ds = new DoubleDataset(shape);
		ds.fill(0.0);
		file.getdata(ds.getBuffer());
		file.closegroup();
		file.closegroup(); // back up to /entry1 level
		return (double[]) ds.getBuffer();
	}

	private void averageCyclesAndInsert(double[][] normalisedItSpectra, String datagroupname, GdaNexusFile file)
			throws NexusException {

		String avDataGroupName = datagroupname + "_averaged";

		int numberCycles = itScans.length;
		int numberOfSpectraPerCycle = itScans[0].getNumberOfAvailablePoints();
		// int totalNumberOfSpectra = normalisedItSpectra.length;
		int numChannelsInMCA = normalisedItSpectra[0].length;
		double[][] averagednormalisedItSpectra = new double[numberOfSpectraPerCycle][numChannelsInMCA]; // spectrum, mca
		// channel

		for (int cycle = 0; cycle < numberCycles; cycle++) {
			for (int spectrumNum = 0; spectrumNum < numberOfSpectraPerCycle; spectrumNum++) {
				for (int channelIndex = 0; channelIndex < numChannelsInMCA; channelIndex++) {
					int absoulteSpectrumNum = spectrumNum + (cycle * numberOfSpectraPerCycle);
					averagednormalisedItSpectra[spectrumNum][channelIndex] += normalisedItSpectra[absoulteSpectrumNum][channelIndex];
				}
			}
		}

		for (int spectrumNum = 0; spectrumNum < numberOfSpectraPerCycle; spectrumNum++) {
			for (int channelIndex = 0; channelIndex < numChannelsInMCA; channelIndex++) {
				averagednormalisedItSpectra[spectrumNum][channelIndex] /= numberCycles;
			}
		}

		file.makegroup(avDataGroupName, "NXdata");
		file.openpath(avDataGroupName);

		String axes = "energy:time:group";

		addData(averagednormalisedItSpectra, file, axes);
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

	private String determineAsciiFilename(String suffix) {
		// the scans would have created Nexus files, so base an ascii file on this plus any template, if supplied
		String itFilename = itScans[0].getDataWriter().getCurrentFileName();
		String folder = convertFromNexusToAsciiFolder(itFilename);
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
