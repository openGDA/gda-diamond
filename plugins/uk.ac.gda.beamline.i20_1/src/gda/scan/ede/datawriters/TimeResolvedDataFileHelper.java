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

import gda.scan.ede.EdeScanType;
import gda.scan.ede.datawriters.EdeDataConstants.ItMetadata;
import gda.scan.ede.datawriters.EdeDataConstants.RangeData;
import gda.scan.ede.datawriters.EdeDataConstants.TimingGroupMetadata;
import gda.scan.ede.position.EdePositionType;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import org.dawnsci.plotting.tools.profile.DataFileHelper;
import org.eclipse.dawnsci.analysis.api.dataset.IDataset;
import org.eclipse.dawnsci.analysis.dataset.impl.Dataset;
import org.eclipse.dawnsci.analysis.dataset.impl.DatasetUtils;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.eclipse.dawnsci.hdf5.H5Utils;
import org.eclipse.dawnsci.hdf5.HierarchicalDataFactory;
import org.eclipse.dawnsci.hdf5.HierarchicalDataFileUtils;
import org.eclipse.dawnsci.hdf5.IHierarchicalDataFile;
import org.eclipse.dawnsci.hdf5.Nexus;
import org.eclipse.dawnsci.hdf5.nexus.NexusUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.calibration.data.CalibrationDetails;

public class TimeResolvedDataFileHelper {

	private static final String EXCLUDED_CYCLE_ATTRIBUTE_NAME = "excluded";
	private static final String AVG_ATTRIBUTE_NAME = "avg";
	private static final String ENERGY_POLYNOMIAL = "polynomial";

	private static final String NEXUS_ROOT_ENTRY_NAME = "/entry1/";

	private static final String META_DATA_PATH = NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.META_DATA_NAME + "/";

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedDataFileHelper.class);

	private final String nexusfileName;

	private DoubleDataset itNormalisedWithI0iData = null;
	private DoubleDataset itNormalisedWithI0fData = null;
	private DoubleDataset itNormalisedWithAvgI0iAndI0fData = null;

	private DoubleDataset timeAxisData;
	private DoubleDataset groupAxisData;

	private DoubleDataset i0darkDataSet = null;

	private DoubleDataset i0iDataSet = null;
	private DoubleDataset i0iCorrectedDataSet = null;

	private DoubleDataset itDarkData = null;

	private DoubleDataset itCorrectedDataSet = null;
	private DoubleDataset itData = null;


	private DoubleDataset i0fData = null;
	private DoubleDataset i0fCorrectedDataSet = null;

	private DoubleDataset i0iAndI0fCorrectedAvgData = null;

	private DoubleDataset iRefDarkData = null;


	private DoubleDataset i0ForIRefData = null;
	private  DoubleDataset i0ForIRefCorrectedData = null;

	private DoubleDataset iRefidata = null;
	private DoubleDataset iRefiCorrecteddata = null;
	private DoubleDataset iReffdata = null;
	private DoubleDataset iReffCorrecteddata = null;
	private DoubleDataset iReffNormalisedData = null;
	private DoubleDataset iRefiNormalisedData = null;

	public TimeResolvedDataFileHelper(String nexusfileName) {
		this.nexusfileName = nexusfileName;
	}

	public void averageSpectrumAndReplace(RangeData[] spectrumToAvg) throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getWriter(nexusfileName);
		try {
			file.setAttribute(META_DATA_PATH + EdeDataConstants.IT_COLUMN_NAME, AVG_ATTRIBUTE_NAME, DataHelper.toString(spectrumToAvg));
		} finally {
			file.close();
		}
		updateWithNormalisedData(false);
	}

	public void excludeCyclesInData(int[] cyclesToExclude) throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getWriter(nexusfileName);
		try {
			file.setAttribute(META_DATA_PATH + EdeDataConstants.IT_COLUMN_NAME, EXCLUDED_CYCLE_ATTRIBUTE_NAME, DataHelper.toString(cyclesToExclude));
		} finally {
			file.close();
		}
		updateWithNormalisedData(false);
	}

	public void createMetaDataEntries(TimingGroupMetadata[] i0TimingGroupMetaData, TimingGroupMetadata[] itTimingGroupMetaData,
			TimingGroupMetadata[] i0ForRefTimingGroupMetaData, TimingGroupMetadata[] iRefTimingGroupMetaData, String scannablesConfiguration, String energyCalibrationDetails) throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getWriter(nexusfileName);
		try {
			String parent = HierarchicalDataFileUtils.createParentEntry(file, META_DATA_PATH, Nexus.DATA);
			// It
			DoubleDataset metadata = TimingGroupMetadata.toDataset(itTimingGroupMetaData);
			addDatasetToNexus(file, EdeDataConstants.IT_COLUMN_NAME, parent, metadata, null);

			// I0
			metadata = TimingGroupMetadata.toDataset(i0TimingGroupMetaData);
			addDatasetToNexus(file, EdeDataConstants.I0_COLUMN_NAME, parent, metadata, null);

			if (i0ForRefTimingGroupMetaData != null) {
				// I0ForIRef
				metadata = TimingGroupMetadata.toDataset(i0ForRefTimingGroupMetaData);
				addDatasetToNexus(file, EdeDataConstants.I0_IREF_DATA_NAME, parent, metadata, null);
			}

			if (iRefTimingGroupMetaData != null) {
				// I0ForIRef
				metadata = TimingGroupMetadata.toDataset(iRefTimingGroupMetaData);
				addDatasetToNexus(file, EdeDataConstants.IREF_DATA_NAME, parent, metadata, null);
			}

			file.setAttribute(parent, NexusUtils.LABEL, scannablesConfiguration);

			if (energyCalibrationDetails != null) {
				file.setAttribute(parent, ENERGY_POLYNOMIAL, energyCalibrationDetails);
			}
		} finally {
			file.close();
		}
	}

	public void updateWithNormalisedData(boolean generateAsciiFiles) throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getWriter(nexusfileName);
		try {
			deriveTimingGroupsAndGenerateNormalisedData(file);
			RangeData[] avgSpectraList = getAvgSpectra(file);
			int[] excludedCycles = getExcludedCycles(file);
			createAxisForNormalisedItData(file, avgSpectraList);
			updateNexusFileWithNormalisedData(file, avgSpectraList, excludedCycles);
			if (generateAsciiFiles) {
				createAsciiFiles(file);
			}
		} catch (Exception e) {
			logger.error("Updating the nexus file failed.", e);
		} finally {
			file.close();
		}
	}

	private int[] getExcludedCycles(IHierarchicalDataFile file) {
		Object excludedCyclesInfo = file.getAttributeValues(META_DATA_PATH + EdeDataConstants.IT_COLUMN_NAME).get(EXCLUDED_CYCLE_ATTRIBUTE_NAME);
		int[] excludedCycles = null;
		if (excludedCyclesInfo != null) {
			excludedCycles = DataHelper.toArray(((String[]) excludedCyclesInfo)[0]);
		}
		return excludedCycles;
	}

	private RangeData[] getAvgSpectra(IHierarchicalDataFile file) {
		Object avgSpectrumInfo = file.getAttributeValues(META_DATA_PATH + EdeDataConstants.IT_COLUMN_NAME).get(AVG_ATTRIBUTE_NAME);
		RangeData[] avgSpectraList = null;

		if (avgSpectrumInfo != null) {
			avgSpectraList = RangeData.toRangeDataList(((String[]) avgSpectrumInfo)[0]);
		}
		return avgSpectraList;
	}

	private DoubleDataset getAverageDataset(DoubleDataset cyclicDataset, int[] excludedCycles) {
		int[] shape = cyclicDataset.getShape();
		int noOfCycles = shape[0];
		int numberOfSpectrum = shape[1];
		int numberOfChannels = shape[2];
		DoubleDataset avgDataset = null;
		if (noOfCycles > 1) {
			avgDataset = new DoubleDataset(new int[]{0, numberOfChannels});
			for (int i = 0; i < numberOfSpectrum; i++) {
				Dataset tempDataset = cyclicDataset.getSlice(new int[]{0,i,0}, new int[]{noOfCycles, numberOfSpectrum, numberOfChannels}, new int[]{1, numberOfSpectrum, 1});
				if (excludedCycles != null && excludedCycles.length > 0) {
					tempDataset = DatasetUtils.take(tempDataset, excludedCycles, 0);
				}
				tempDataset.squeeze(true);
				if (tempDataset.getShape().length > 1) {
					tempDataset = tempDataset.mean(0);
				}
				tempDataset.setShape(new int[]{1, numberOfChannels});
				avgDataset = (DoubleDataset) DatasetUtils.append(avgDataset, tempDataset, 0);
			}
		} else {
			avgDataset = cyclicDataset.clone();
			avgDataset.setShape(new int[]{numberOfSpectrum, numberOfChannels});
		}
		return avgDataset;
	}

	private void createAsciiFiles(IHierarchicalDataFile file) throws Exception {
		File nexusFile = new File(nexusfileName);
		String assciiFolder = DataFileHelper.convertFromNexusToAsciiFolder(nexusfileName);

		DoubleDataset energyData = getDataFromFile(file, this.getDetectorDataPath() + EdeDataConstants.ENERGY_COLUMN_NAME);

		String scannablesDescription = file.getAttributeValue(NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.META_DATA_NAME + "@" + NexusUtils.LABEL);

		String energyCalibrationDetails = file.getAttributeValue(NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.META_DATA_NAME + "@" + ENERGY_POLYNOMIAL);

		if (energyCalibrationDetails != null) {
			scannablesDescription += "\n# " + energyCalibrationDetails;
		}

		// Create I0_raw
		DoubleDataset metaData = getDataFromFile(file, META_DATA_PATH + EdeDataConstants.I0_COLUMN_NAME);
		String filePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.I0_RAW_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
		FileWriter writer = new FileWriter(filePathName);
		try {
			writeMetaData(scannablesDescription, metaData, writer);
			writer.write("# index\t" + EdeDataConstants.STRIP_COLUMN_NAME + "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t"
					+ EdeDataConstants.I0_CORR_COLUMN_NAME + "\t" + EdeDataConstants.I0_RAW_COLUMN_NAME + "\t"
					+ EdeDataConstants.I0_DARK_COLUMN_NAME + "\n");
			int numberOfSpectra = i0iDataSet.getShape()[0];
			int numberOfChannels = i0iDataSet.getShape()[1];
			for (int i = 0; i < numberOfSpectra; i++) {
				for (int j = 0; j < numberOfChannels; j++) {
					writer.write(String.format("0%d\t%d\t%f\t%f\t%f\t%f\n", i, j, energyData.get(j), i0iCorrectedDataSet.get(i, j), i0iDataSet.get(i, j), i0darkDataSet.get(i, j)));
				}
			}
			if (i0fCorrectedDataSet != null) {
				numberOfSpectra = i0fData.getShape()[0];
				numberOfChannels = i0fData.getShape()[1];
				for (int i = 0; i < numberOfSpectra; i++) {
					for (int j = 0; j < numberOfChannels; j++) {
						writer.write(String.format("1%d\t%d\t%f\t%f\t%f\t%f\n", i, j, energyData.get(j), i0fCorrectedDataSet.get(i, j), i0fCorrectedDataSet.get(i, j), i0darkDataSet.get(i, j)));
					}
				}
			}
		} catch (Exception e) {
			logger.error("Unable to create " + filePathName, e);
		} finally {
			writer.close();
		}
		itNormalisedWithI0iData.getShape();
		DoubleDataset avgLogI0It = getDataFromFile(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "/" + EdeDataConstants.DATA_COLUMN_NAME);
		int numberOfSpectra = avgLogI0It.getShape()[0];
		int numberOfChannels = avgLogI0It.getShape()[1];
		// Create It_raw
		metaData = getDataFromFile(file, META_DATA_PATH + EdeDataConstants.IT_COLUMN_NAME);
		filePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.IT_RAW_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
		writer = new FileWriter(filePathName);
		try {
			writeMetaData(scannablesDescription, metaData, writer);
			writer.write("# index\t" + EdeDataConstants.STRIP_COLUMN_NAME + "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t"
					+ EdeDataConstants.IT_CORR_COLUMN_NAME + "\t" + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "\t" + EdeDataConstants.IT_RAW_COLUMN_NAME + "\t"
					+ EdeDataConstants.IT_DARK_COLUMN_NAME + "\n");
			DoubleDataset itiAvgData = getAverageDataset(itData, null);
			DoubleDataset itiCorrectedAvgData = getAverageDataset(itCorrectedDataSet, null);

			for (int i = 0; i < numberOfSpectra; i++) {
				for (int j = 0; j < numberOfChannels; j++) {
					writer.write(String.format("%d\t%d\t%f\t%f\t%f\t%f\t%f\n", i, j, energyData.get(j), itiCorrectedAvgData.get(i,j) , avgLogI0It.get(i, j), itiAvgData.get(i,j) , itDarkData.get(0, j)));
				}
			}
		} catch (Exception e) {
			logger.error("Unable to create " + filePathName, e);
		} finally {
			writer.close();
		}

		String itiFilePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.IT_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
		String itFFilePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.LN_I0_IT__FINAL_I0_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
		String itAvgFileFPathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);

		FileWriter itiWriter = new FileWriter(itiFilePathName);
		FileWriter itffWriter = new FileWriter(itFFilePathName);
		FileWriter itavgWriter = new FileWriter(itAvgFileFPathName);
		try {
			writeMetaData(scannablesDescription, metaData, itiWriter);
			writeMetaData(scannablesDescription, metaData, itffWriter);
			writeMetaData(scannablesDescription, metaData, itavgWriter);
			String header = "# index\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t" + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "\n";
			itiWriter.write(header);
			itffWriter.write(header);
			itavgWriter.write(header);
			DoubleDataset i0f = getDataFromFile(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT__FINAL_I0_COLUMN_NAME + "/" + EdeDataConstants.DATA_COLUMN_NAME);
			DoubleDataset i0avg = getDataFromFile(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME + "/" + EdeDataConstants.DATA_COLUMN_NAME);
			for (int i = 0; i < numberOfSpectra; i++) {
				for (int j = 0; j < numberOfChannels; j++) {
					itiWriter.write(String.format("%d\t%f\t%f\n", i, energyData.get(j), avgLogI0It.get(i, j)));
					itffWriter.write(String.format("%d\t%f\t%f\n", i, energyData.get(j), i0f.get(i, j)));
					itavgWriter.write(String.format("%d\t%f\t%f\n", i, energyData.get(j), i0avg.get(i, j)));
				}
			}
		} catch (Exception e) {
			logger.error("Unable to create " + filePathName, e);
		} finally {
			itiWriter.close();
			itffWriter.close();
			itavgWriter.close();
		}

		if (iRefiNormalisedData != null) {
			// Create IRef_raw
			numberOfSpectra = iRefiNormalisedData.getShape()[0];
			numberOfChannels = iRefiNormalisedData.getShape()[1];
			metaData = getDataFromFile(file, META_DATA_PATH + EdeDataConstants.IREF_DATA_NAME);
			filePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.IREF_RAW_DATA_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
			writer = new FileWriter(filePathName);
			try {
				writeMetaData(scannablesDescription, metaData, writer);
				writer.write("# index\t" + EdeDataConstants.STRIP_COLUMN_NAME + "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t"
						+ EdeDataConstants.IREF_DATA_NAME + "\t" + EdeDataConstants.LN_I0_IREF_COLUMN_NAME + "\t" + EdeDataConstants.IREF_RAW_DATA_NAME + "\t"
						+ EdeDataConstants.IT_DARK_COLUMN_NAME + "\n");
				for (int i = 0; i < numberOfSpectra; i++) {
					for (int j = 0; j < numberOfChannels; j++) {
						writer.write(String.format("%d\t%d\t%f\t%f\t%f\t%f\t%f\n", i, j, energyData.get(j), iRefiCorrecteddata.get(i,j) , iRefiNormalisedData.get(i, j), iRefidata.get(i,j) , iRefDarkData.get(i, j)));
					}
				}
			} catch (Exception e) {
				logger.error("Unable to create " + filePathName, e);
			} finally {
				writer.close();
			}
			// Create IRef
			filePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.IREF_DATA_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
			writer = new FileWriter(filePathName);
			try {
				writeMetaData(scannablesDescription, metaData, writer);
				writer.write("# index\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t"
						+ EdeDataConstants.LN_I0_IREF_COLUMN_NAME + "\n");
				for (int i = 0; i < numberOfSpectra; i++) {
					for (int j = 0; j < numberOfChannels; j++) {
						writer.write(String.format("0%d\t%f\t%f\n", i, energyData.get(j), iRefiNormalisedData.get(i, j)));
					}
				}
			} catch (Exception e) {
				logger.error("Unable to create " + filePathName, e);
			} finally {
				writer.close();
			}
			if (iReffNormalisedData != null) {
				filePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.IREF_FINAL_DATA_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
				writer = new FileWriter(filePathName);
				try {
					writeMetaData(scannablesDescription, metaData, writer);
					writer.write("# index\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t"
							+ EdeDataConstants.LN_I0_IREF_COLUMN_NAME + "\n");
					for (int i = 0; i < numberOfSpectra; i++) {
						for (int j = 0; j < numberOfChannels; j++) {
							writer.write(String.format("1%d\t%f\t%f\n", i, energyData.get(j), iReffNormalisedData.get(i, j)));
						}
					}
				} catch (Exception e) {
					logger.error("Unable to create " + filePathName, e);
				} finally {
					writer.close();
				}
			}
		}
	}

	private void writeMetaData(String scannablesDescription, DoubleDataset metaData, FileWriter writer)
			throws IOException {
		writer.write("# " + scannablesDescription + "\n");
		writer.write("# \n");
		writer.write("# " + TimingGroupMetadata.toMetadataString(metaData).replace("\n", "\n# ") + "\n#\n");
	}

	private void updateNexusFileWithNormalisedData(IHierarchicalDataFile file, RangeData[] avgSpectraList, int[] excludedCycles) throws Exception {
		Map<String, String> attributes = new HashMap<String, String>();

		// Adding Axis
		attributes.put(NexusUtils.AXIS, "1");
		String parent = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME, Nexus.DATA);
		addDatasetToNexus(file, EdeDataConstants.TIMINGGROUP_COLUMN_NAME, parent, groupAxisData, attributes);

		attributes.clear();
		attributes.put(NexusUtils.AXIS, "1");
		attributes.put(NexusUtils.PRIM, "1");
		attributes.put(NexusUtils.UNIT, "s");
		addDatasetToNexus(file, EdeDataConstants.TIME_COLUMN_NAME, parent, timeAxisData, attributes);

		attributes.clear();
		attributes.put(NexusUtils.SIGNAL, "1");

		String targetPath = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "/", Nexus.DATA);
		checkCyclicDataAndAddData(file, targetPath, avgSpectraList, excludedCycles, itNormalisedWithI0iData, attributes);
		addLinks(file, targetPath);

		targetPath = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT__FINAL_I0_COLUMN_NAME + "/", Nexus.DATA);
		checkCyclicDataAndAddData(file, targetPath, avgSpectraList, excludedCycles, itNormalisedWithI0fData, attributes);
		addLinks(file, targetPath);

		targetPath = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME + "/", Nexus.DATA);
		checkCyclicDataAndAddData(file, targetPath, avgSpectraList, excludedCycles, itNormalisedWithAvgI0iAndI0fData, attributes);
		addLinks(file, targetPath);

		if (iRefiNormalisedData != null) {
			targetPath = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IREF_COLUMN_NAME + "/", Nexus.DATA);
			addDatasetToNexus(file, EdeDataConstants.DATA_COLUMN_NAME, targetPath, iRefiNormalisedData, attributes);
		}
	}

	private void checkCyclicDataAndAddData(IHierarchicalDataFile file, String fullPath, RangeData[] avgSpectraList, int[] excludedCycles, DoubleDataset data, Map<String, String> attributes) throws Exception {
		DoubleDataset dataToAdd = null;
		if (data.getShape()[0] == 1) {
			data.setShape(new int[]{data.getShape()[1], data.getShape()[2]});
			dataToAdd = data;
		} else {
			addDatasetToNexus(file, EdeDataConstants.DATA_RAW_COLUMN_NAME, fullPath, data, attributes);
			dataToAdd = getAverageDataset(data, excludedCycles);
		}
		if (avgSpectraList != null) {
			int noOfSpectrum = dataToAdd.getShape()[0];
			int noOfChannels = dataToAdd.getShape()[1];
			DoubleDataset dataToAvgAndAdd = new DoubleDataset(0, noOfChannels);
			int j = 0;
			for (int i = 0; i < avgSpectraList.length; i++) {
				RangeData avgInfo = avgSpectraList[i];
				DoubleDataset avgDataItem = (DoubleDataset) dataToAdd.getSlice(new int[]{avgInfo.getStartIndex(), 0}, new int[]{avgInfo.getEndIndex() + 1, noOfChannels}, null).mean(0);
				avgDataItem.setShape(new int[]{1, noOfChannels});
				if (avgInfo.getStartIndex() - j > 0) {
					Dataset sliceToAppend = dataToAdd.getSlice(new int[]{j, 0}, new int[]{avgInfo.getStartIndex(), noOfChannels}, null);
					dataToAvgAndAdd = (DoubleDataset) DatasetUtils.append(dataToAvgAndAdd, sliceToAppend, 0);
				}
				dataToAvgAndAdd = (DoubleDataset) DatasetUtils.append(dataToAvgAndAdd, avgDataItem, 0);
				j = avgSpectraList[i].getEndIndex() + 1;
			}
			if (j < noOfSpectrum) {
				DoubleDataset sliceToAppend = (DoubleDataset) dataToAdd.getSlice(new int[]{j, 0}, new int[]{noOfSpectrum, noOfChannels}, null);
				dataToAvgAndAdd = (DoubleDataset) DatasetUtils.append(dataToAvgAndAdd, sliceToAppend, 0);
			}
			dataToAdd = dataToAvgAndAdd;
			if (avgSpectraList.length > 0) {
				attributes.put(AVG_ATTRIBUTE_NAME, DataHelper.toString(avgSpectraList));
			}
		}
		if (excludedCycles != null && excludedCycles.length > 0) {
			attributes.put(EXCLUDED_CYCLE_ATTRIBUTE_NAME, DataHelper.toString(excludedCycles));
		}

		addDatasetToNexus(file, EdeDataConstants.DATA_COLUMN_NAME, fullPath, dataToAdd, attributes);
	}

	private void addLinks(IHierarchicalDataFile file, String targetPath)
			throws Exception {
		file.createLink(targetPath, EdeDataConstants.TIME_COLUMN_NAME, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.TIME_COLUMN_NAME);
		file.createLink(targetPath, EdeDataConstants.TIMINGGROUP_COLUMN_NAME, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.TIMINGGROUP_COLUMN_NAME);
		file.createLink(targetPath, EdeDataConstants.ENERGY_COLUMN_NAME, this.getDetectorDataPath() + EdeDataConstants.ENERGY_COLUMN_NAME);
	}

	private void addDatasetToNexus(IHierarchicalDataFile file, String dataName, String fullPath, DoubleDataset data, Map<String, String> attributes) throws Exception {
		long[] shape = H5Utils.getLong(data.getShape());
		String insertedData = file.replaceDataset(dataName, Dataset.FLOAT64, shape, data.getBuffer(), fullPath);
		if (attributes == null) {
			return;
		}
		for (Entry<String, String> entry : attributes.entrySet()) {
			file.setAttribute(insertedData, entry.getKey(), entry.getValue());
		}
	}

	private DoubleDataset getDetectorDataFromFile(IHierarchicalDataFile file, String path) throws Exception {
		String detectorPath = getDetectorDataPath();
		return getDataFromFile(file, detectorPath + path);
	}

	private DoubleDataset getDataFromFile(IHierarchicalDataFile file, String path)
			throws Exception {
		return (DoubleDataset) H5Utils.getSet(file, path);
		//		ncsa.hdf.object.Dataset dataset = (ncsa.hdf.object.Dataset) file.getData(path);
		//		int[] dimension = new int[dataset.getDims().length];
		//		long[] oriDimension = dataset.getDims();
		//		for (int i = 0; i < dimension.length; i++) {
		//			dimension[i] = (int) oriDimension[i];
		//		}
		//		double[] data = (double[]) dataset.getData();
		//		return new DoubleDataset(data, dimension);
	}

	private String getDetectorDataPath() {
		return NEXUS_ROOT_ENTRY_NAME + getDetectorNodeName() + "/";
	}

	// FIXME
	private String getDetectorNodeName() {
		return "xstrip";
	}

	private static class Index {
		public final int start;
		public Index(int start) {
			end = this.start = start;
		}
		public int end;
	}

	private void deriveTimingGroupsAndGenerateNormalisedData(IHierarchicalDataFile file) throws Exception {
		DoubleDataset rawDataset = getDetectorDataFromFile(file, EdeDataConstants.DATA_COLUMN_NAME);
		DoubleDataset frameDataset = getDetectorDataFromFile(file, EdeDataConstants.FRAME_COLUMN_NAME);
		DoubleDataset timmingDataset = getDetectorDataFromFile(file, EdeDataConstants.TIMINGGROUP_COLUMN_NAME);
		DoubleDataset cycleDataset = getDetectorDataFromFile(file, EdeDataConstants.CYCLE_COLUMN_NAME);
		DoubleDataset beamInOutDataset = getDetectorDataFromFile(file, EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME);
		DoubleDataset itDataset = getDetectorDataFromFile(file, EdeDataConstants.IT_COLUMN_NAME);
		if (rawDataset.getShape()[0] != frameDataset.getShape()[0] ||
				rawDataset.getShape()[0] != timmingDataset.getShape()[0] ||
				rawDataset.getShape()[0] != cycleDataset.getShape()[0] ||
				rawDataset.getShape()[0] != beamInOutDataset.getShape()[0]) {
			throw new Exception("Incompatible datasets");
		}

		Index i0darkDataSetIndex = null;

		Index i0iDataSetIndex = null;

		Index itDarkDataSetIndex = null;

		Index itRawDataSetIndex = null;

		Index i0fDataSetIndex = null;

		Index iRefdarkDataSetIndex = null;

		Index i0ForIRefDataSetIndex = null;

		Index iRefidataSetIndex = null;

		Index iReffdataSetIndex = null;

		int cycleCount = 0;
		double cycleIndexValue = -1d;
		int[] timingGroups = null;

		int frameIndex = -1;

		for (int i = 0; i < rawDataset.getShape()[0]; i++) {
			if (beamInOutDataset.get(i) == EdeScanType.DARK.getValue()) {
				if (itDataset.get(i) == EdePositionType.OUTBEAM.getValue()) { // I0
					if (i0darkDataSetIndex == null) {
						i0darkDataSetIndex = new Index(i);
					} else {
						i0darkDataSetIndex.end = i;
					}
				} else if (itDataset.get(i) == EdePositionType.INBEAM.getValue()) { // It
					if (itDarkDataSetIndex == null) {
						itDarkDataSetIndex = new Index(i);
					} else {
						itDarkDataSetIndex.end = i;
					}
				} else { // For EdePositionType.REFERENCE IRef
					if (iRefdarkDataSetIndex == null) { // I0 light is collected, so it is IRefDark
						iRefdarkDataSetIndex = new Index(i);
					} else {
						iRefdarkDataSetIndex.end = i;
					}
				}
			} else { // For EdeScanType.LIGHT
				if (itDataset.get(i) == EdePositionType.OUTBEAM.getValue()) {
					if (itRawDataSetIndex == null) {
						if (i0iDataSetIndex == null) { // Must be before i, so it is I0Initial
							i0iDataSetIndex = new Index(i);
						} else {
							i0iDataSetIndex.end = i;
						}
					} else {
						if (i0fDataSetIndex == null) { // Must be after it now, so it is I0final
							i0fDataSetIndex = new Index(i);
						} else {
							i0fDataSetIndex.end = i;
						}
					}
				} else if (itDataset.get(i) == EdePositionType.INBEAM.getValue()) {
					if (itRawDataSetIndex == null) {
						itRawDataSetIndex = new Index(i);
					} else {
						itRawDataSetIndex.end = i;
					}
					if (cycleDataset.get(i) > cycleIndexValue) {
						cycleIndexValue = cycleDataset.get(i);
						cycleCount++;
					}
					// TODO Refactor to make it clear
					// Deriving number of timingGroups and number of spectrum per group using i0iDataSet,
					// assuming the there is one spectrum per group was collected for I0,
					// since all cycles are the same we only need to do the first cycle
					if (cycleCount == 1) {
						if (timingGroups == null && i0iDataSetIndex != null) {
							int derivedNumOfGroups = i0iDataSetIndex.end - i0iDataSetIndex.start + 1;
							timingGroups = new int[derivedNumOfGroups];
						}
						if (timingGroups != null) {
							if (frameDataset.get(i) == 0.0) {
								frameIndex++;
							}
							timingGroups[frameIndex] = (int) frameDataset.get(i) + 1;
						}
					}
				} else if (itDataset.get(i) == EdePositionType.REFERENCE.getValue()) {
					if (itRawDataSetIndex == null) {
						if (iRefidataSetIndex == null) {
							iRefidataSetIndex = new Index(i);
						} else {
							iRefidataSetIndex.end = i;
						}
					} else {
						if (iReffdataSetIndex == null) {
							iReffdataSetIndex = new Index(i);
						} else {
							iReffdataSetIndex.end = i;
						}

					}
				} else if (itDataset.get(i) == EdePositionType.OUTBEAM_REFERENCE.getValue()) {
					if (i0ForIRefDataSetIndex == null) {
						i0ForIRefDataSetIndex = new Index(i);
					} else {
						i0ForIRefDataSetIndex.end = i;
					}
				}
			}
		}

		if (i0darkDataSetIndex != null) {
			i0darkDataSet = getSlice(rawDataset, i0darkDataSetIndex);
		}
		i0iDataSet = getSlice(rawDataset, i0iDataSetIndex);
		i0iCorrectedDataSet = i0iDataSet.clone().isubtract(i0darkDataSet);

		if (itDarkDataSetIndex !=null) {
			itDarkData = getSlice(rawDataset, itDarkDataSetIndex);
		}

		// IRef
		if (iRefdarkDataSetIndex != null && i0ForIRefDataSetIndex != null && iRefidataSetIndex != null) {
			iRefDarkData = getSlice(rawDataset, iRefdarkDataSetIndex);
			i0ForIRefData = getSlice(rawDataset, i0ForIRefDataSetIndex);
			i0ForIRefCorrectedData = i0ForIRefData.clone().isubtract(iRefDarkData);
			iRefidata = getSlice(rawDataset, iRefidataSetIndex);
			iRefiCorrecteddata = iRefidata.clone().isubtract(iRefDarkData);
			iRefiNormalisedData = createNormalisedIRefData(i0ForIRefCorrectedData, iRefiCorrecteddata);
			if (iReffdataSetIndex != null) {
				iReffdata = getSlice(rawDataset, iRefidataSetIndex);
				iReffCorrecteddata = iReffdata.clone().isubtract(iRefDarkData);
				iReffNormalisedData = createNormalisedIRefData(i0ForIRefCorrectedData, iReffCorrecteddata);
			}
		}

		itData = getSlice(rawDataset, itRawDataSetIndex);
		convertToCycledData(itData, cycleCount);
		itCorrectedDataSet = itData.clone();
		correctItData(itDarkData, itCorrectedDataSet, timingGroups);
		itNormalisedWithI0iData = createNormalisedItData(i0iCorrectedDataSet, itCorrectedDataSet, timingGroups);
		if(i0fDataSetIndex != null) {
			i0fData = getSlice(rawDataset, i0fDataSetIndex);
			i0fCorrectedDataSet = i0fData.clone().isubtract(i0darkDataSet);
			itNormalisedWithI0fData = createNormalisedItData(i0fCorrectedDataSet, itCorrectedDataSet, timingGroups);
			i0iAndI0fCorrectedAvgData = i0iCorrectedDataSet.clone().iadd(i0fCorrectedDataSet).idivide(2);
			itNormalisedWithAvgI0iAndI0fData = createNormalisedItData(i0iAndI0fCorrectedAvgData, itCorrectedDataSet, timingGroups);
		}

	}

	private void createAxisForNormalisedItData(IHierarchicalDataFile file, RangeData[] avgSpectraList) throws Exception {
		DoubleDataset metaDataset = getDataFromFile(file, META_DATA_PATH + EdeDataConstants.IT_COLUMN_NAME);
		TimingGroupMetadata[] timingGroupMetaData = TimingGroupMetadata.toTimingGroupMetaData(metaDataset);
		int totalSpectra = 0;
		int noOfGroups = timingGroupMetaData.length;
		for (int i = 0; i < noOfGroups; i++) {
			totalSpectra += timingGroupMetaData[i].getNoOfFrames();
		}
		int totalAvgSpectra  = totalSpectra;
		if (avgSpectraList != null) {
			for (int i = 0; i < avgSpectraList.length; i++) {
				totalAvgSpectra -= avgSpectraList[i].getEndIndex() - avgSpectraList[i].getStartIndex();
			}
		}
		timeAxisData = new DoubleDataset(new int[]{totalAvgSpectra});
		groupAxisData = new DoubleDataset(new int[]{totalAvgSpectra});
		int currentGroupIndex = 0;
		int j = 0;
		int k = 0;
		int l = 0;
		RangeData avgRange = null;
		double time = 0.0d;
		int totalSpectraUptoCurrentGroup = timingGroupMetaData[currentGroupIndex].getNoOfFrames();
		for (int i = 0; i < totalSpectra; i++) {
			timeAxisData.set(time, k++);
			if (avgSpectraList != null && j < avgSpectraList.length) {
				avgRange = avgSpectraList[j];
				if (avgRange.getStartIndex() == i) {
					while(i < avgRange.getEndIndex()) {
						time += timingGroupMetaData[currentGroupIndex].getTimePerSpectrum();
						i++;
						if (i == totalSpectraUptoCurrentGroup) {
							currentGroupIndex++;
							totalSpectraUptoCurrentGroup += timingGroupMetaData[currentGroupIndex].getNoOfFrames();
						}
					}
					j++;
				}
			}
			time += timingGroupMetaData[currentGroupIndex].getTimePerSpectrum();
			groupAxisData.set(currentGroupIndex, l++);
			if (i == totalSpectraUptoCurrentGroup) {
				currentGroupIndex++;
				totalSpectraUptoCurrentGroup += timingGroupMetaData[currentGroupIndex].getNoOfFrames();
			}
		}
	}

	private void correctItData(DoubleDataset itDarkData, DoubleDataset itData, int[] timingGroups) {
		int[] shape = itData.getShape();
		int noOfCycles = shape[0];
		int numberOfChannels = shape[2];
		int spectrumInCycle = 0;
		int spectrum = 0;
		for (int cycle = 0; cycle < noOfCycles; cycle++) {
			for (int groupIndex = 0; groupIndex < timingGroups.length; groupIndex++) {
				DoubleDataset darkDataset = ((DoubleDataset) itDarkData.getSlice(new int[]{groupIndex, 0},new int[]{groupIndex + 1, numberOfChannels}, null).squeeze());
				spectrumInCycle += timingGroups[groupIndex];
				for (int spectrumIndex = spectrum; spectrumIndex < spectrumInCycle; spectrumIndex++) {
					DoubleDataset itDataset = ((DoubleDataset) itData.getSliceView(new int[]{cycle, spectrumIndex, 0}, new int[]{cycle + 1, spectrumIndex + 1, numberOfChannels}, null).squeeze());
					itDataset.isubtract(darkDataset);
				}
				spectrum += timingGroups[groupIndex];
			}
			spectrumInCycle = 0;
			spectrum = 0;
		}
	}

	private DoubleDataset createNormalisedItData(DoubleDataset i0CorrectedDataSet, DoubleDataset itCorrectedCycledData, int[] timingGroups) {
		int[] shape = itCorrectedCycledData.getShape();
		int noOfCycles = shape[0];
		int numberOfChannels = shape[2];
		int spectrumInCycle = 0;
		int spectrum = 0;
		DoubleDataset normalisedData = new DoubleDataset(itCorrectedCycledData.getShape());
		for (int cycle = 0; cycle < noOfCycles; cycle++) {
			for (int groupIndex = 0; groupIndex < timingGroups.length; groupIndex++) {
				DoubleDataset i0Dataset = ((DoubleDataset) i0CorrectedDataSet.getSlice(new int[]{groupIndex, 0},new int[]{groupIndex + 1, numberOfChannels}, null).squeeze());
				spectrumInCycle += timingGroups[groupIndex];
				for (int spectrumIndex = spectrum; spectrumIndex < spectrumInCycle; spectrumIndex++) {
					DoubleDataset itDataset = ((DoubleDataset) itCorrectedCycledData.getSliceView(new int[]{cycle, spectrumIndex, 0}, new int[]{cycle + 1, spectrumIndex + 1, numberOfChannels}, null).squeeze());
					for (int channel = 0; channel < numberOfChannels; channel++) {
						double value = calcLnI0It(i0Dataset.getDouble(channel), itDataset.getDouble(channel));
						normalisedData.set(value, new int[]{cycle, spectrumIndex, channel});
					}
				}
				spectrum = timingGroups[groupIndex];
			}
			spectrumInCycle = 0;
			spectrum = 0;
		}
		return normalisedData;
	}

	private DoubleDataset createNormalisedIRefData(DoubleDataset i0ForRefCorrectedDataSet, DoubleDataset iRefCorrectedData) {
		int[] shape = iRefCorrectedData.getShape();
		int numberOfChannels = shape[1];
		DoubleDataset normalisedData = new DoubleDataset(new int[]{1,numberOfChannels});
		for (int channel = 0; channel < numberOfChannels; channel++) {
			double value = calcLnI0It(i0ForRefCorrectedDataSet.get(0, channel), iRefCorrectedData.get(0, channel));
			normalisedData.set(value, 0, channel);
		}
		return normalisedData;
	}

	private double calcLnI0It(Double i0_corrected, Double it_corrected) {
		Double lni0it = Math.log(i0_corrected / it_corrected);
		if (lni0it.isNaN() || lni0it.isInfinite() /*|| lni0it < 0.0*/) {
			lni0it = .0;
		}
		return lni0it.doubleValue();
	}

	private void convertToCycledData(DoubleDataset itRawDataSet, int cycleCount) {
		int framesPerCycle = itRawDataSet.getShape()[0] / cycleCount;
		int noOfChannels = itRawDataSet.getShape()[1];
		itRawDataSet.setShape(new int[]{cycleCount, framesPerCycle, noOfChannels});
	}

	private DoubleDataset getSlice(DoubleDataset rawDataset, Index index) {
		return (DoubleDataset) rawDataset.getSlice(new int[]{index.start, 0}, new int[]{index.end + 1, rawDataset.getShape()[1]}, null);
	}

	public boolean isTimeResolvedDataFile() throws Exception {
		IHierarchicalDataFile file = null;
		try {
			file = HierarchicalDataFactory.getReader(nexusfileName);
			return file.isDataset(NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.TIME_COLUMN_NAME);
		} finally {
			if (file != null) {
				file.close();
			}
		}
	}

	public DoubleDataset getGroupData() throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getReader(nexusfileName);
		try {
			return getDataFromFile(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.TIMINGGROUP_COLUMN_NAME);
		}
		finally {
			file.close();
		}
	}

	public DoubleDataset getTimeData() throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getReader(nexusfileName);
		try {
			return getDataFromFile(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.TIME_COLUMN_NAME);
		}
		finally {
			file.close();
		}
	}

	public IDataset getEnergy() throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getReader(nexusfileName);
		try {
			return getDataFromFile(file, this.getDetectorDataPath() + EdeDataConstants.ENERGY_COLUMN_NAME);
		}
		finally {
			file.close();
		}
	}

	// TODO Replace with model
	public int[] getCyclesInfo() throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getReader(nexusfileName);
		try {
			String fullDataPath = NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "/" + EdeDataConstants.DATA_RAW_COLUMN_NAME;
			boolean dataAvailable = file.isDataset(fullDataPath);
			if (dataAvailable) {
				int[] excludedCycles = null;
				Object excludedCyclesInfo = file.getAttributeValues(META_DATA_PATH + EdeDataConstants.IT_COLUMN_NAME).get(EXCLUDED_CYCLE_ATTRIBUTE_NAME);
				if (excludedCyclesInfo != null) {
					excludedCycles = DataHelper.toArray(((String[]) excludedCyclesInfo)[0]);
				}
				int[] dimension = file.getDatasetShapes(Dataset.FLOAT64).get(fullDataPath);
				int[] cyclesInfo = new int[dimension[0]];
				int j = 0;
				for (int i = 0; i < dimension[0]; i++) {
					if (excludedCycles != null && j < excludedCycles.length && i == excludedCycles[j]) {
						cyclesInfo[i] = 1;
						j++;
					} else {
						cyclesInfo[i] = 0;
					}
				}
				return cyclesInfo;
			}
			return new int[]{};
		}
		finally {
			file.close();
		}
	}

	public void replaceEnergy(String energyCalibration, double[] value) throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getWriter(nexusfileName);
		try {
			DoubleDataset data = new DoubleDataset(value, new int[]{value.length});
			String targetPath = HierarchicalDataFileUtils.createParentEntry(file, getDetectorDataPath(), Nexus.DATA);
			addDatasetToNexus(file, EdeDataConstants.ENERGY_COLUMN_NAME, targetPath, data, null);
			String parent = HierarchicalDataFileUtils.createParentEntry(file, META_DATA_PATH, Nexus.DATA);
			file.setAttribute(parent, ENERGY_POLYNOMIAL, energyCalibration, true);
		}
		finally {
			file.close();
		}
	}

	public ItMetadata getItMetadata() throws Exception {
		IHierarchicalDataFile file = HierarchicalDataFactory.getReader(nexusfileName);
		try {
			DoubleDataset data = getDataFromFile(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.META_DATA_NAME + "/" + EdeDataConstants.IT_COLUMN_NAME);
			TimingGroupMetadata[] timingGroupMetadata = TimingGroupMetadata.toTimingGroupMetaData(data);
			RangeData[] avgSpectraList = getAvgSpectra(file);
			int[] excludedCycles = getExcludedCycles(file);
			ItMetadata metadata = new ItMetadata(timingGroupMetadata, avgSpectraList, excludedCycles);
			String energyCalibrationDetails = file.getAttributeValue(NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.META_DATA_NAME + "@" + ENERGY_POLYNOMIAL);
			if (energyCalibrationDetails != null && !energyCalibrationDetails.isEmpty()) {
				energyCalibrationDetails = energyCalibrationDetails.replaceAll("^\\[|\\]$", ""); // This is a hack to remove "[" and "]" because it is loaded as array
				metadata.setCalibrationDetails(CalibrationDetails.toObject(energyCalibrationDetails));
			}
			return metadata;
		}
		finally {
			file.close();
		}
	}
}
