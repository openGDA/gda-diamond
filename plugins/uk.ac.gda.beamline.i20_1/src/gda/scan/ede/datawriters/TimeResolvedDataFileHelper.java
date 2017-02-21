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
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.commons.lang.StringUtils;
import org.dawnsci.plotting.tools.profile.DataFileHelper;
import org.eclipse.dawnsci.hdf.object.H5Utils;
import org.eclipse.dawnsci.hdf.object.HierarchicalDataFactory;
import org.eclipse.dawnsci.hdf.object.HierarchicalDataFileUtils;
import org.eclipse.dawnsci.hdf.object.IHierarchicalDataFile;
import org.eclipse.dawnsci.hdf.object.Nexus;
import org.eclipse.dawnsci.hdf.object.nexus.NexusUtils;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DatasetUtils;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.IDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.InterfaceProvider;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.datawriters.EdeDataConstants.ItMetadata;
import gda.scan.ede.datawriters.EdeDataConstants.RangeData;
import gda.scan.ede.datawriters.EdeDataConstants.TimingGroupMetadata;
import gda.scan.ede.position.EdePositionType;
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
	private DoubleDataset itNormalisedWithInterpolatedI0iAndI0fData = null;

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
	private String detectorName4Node;

	public String getDetectorName4Node() {
		return detectorName4Node;
	}

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
			TimingGroupMetadata[] i0ForRefTimingGroupMetaData, TimingGroupMetadata[] iRefTimingGroupMetaData, String scannablesConfiguration,
			String energyCalibrationDetails, String sampleDetails) throws Exception {
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
			if (StringUtils.isNotEmpty(sampleDetails)) {
				file.setAttribute(parent, EdeDataConstants.SAMPLE_DETAILS_NAME, sampleDetails);
			}
			if (energyCalibrationDetails != null) {
				file.setAttribute(parent, ENERGY_POLYNOMIAL, energyCalibrationDetails);
			}
		} finally {
			file.close();
		}
	}


	/**
	 * Run NeXuS file update and Ascii file writing.
	 * This can be done in new thread, so that another scan can be started whilst
	 * data from previous scan is being written. Works ok provided we don't attempt
	 * to write ascii data from two scans simultaneously.
	 * @param generateAsciiFiles whether to generate Ascii files
	 * @param runInThread run in new thread
	 * @since 20/1/2016
	 */
	public void updateWithNormalisedData(boolean generateAsciiFiles, boolean runInThread ) throws Exception {
		if ( !runInThread ) {
			updateWithNormalisedData( generateAsciiFiles );
			return;
		}

		final IHierarchicalDataFile file = HierarchicalDataFactory.getWriter(nexusfileName);

		final boolean genAscii = generateAsciiFiles;
		Thread fileWritingThread = new Thread(new Runnable() {
			@Override
			public void run() {
				try {
					String threadInfo = "NeXuS update and Ascii file writing thread";
					InterfaceProvider.getTerminalPrinter().print(threadInfo + " started...");
					logger.info(threadInfo + " started");

					long startTime = System.nanoTime();

					// TODO Test if it's safe to update NeXuS file inside thread while next scan starts up (seems ok).
					deriveTimingGroupsAndGenerateNormalisedData(file);
					RangeData[] avgSpectraList = getAvgSpectra(file);
					int[] excludedCycles = getExcludedCycles(file);
					createAxisForNormalisedItData(file, avgSpectraList);
					updateNexusFileWithNormalisedData(file, avgSpectraList, excludedCycles);
					// TODO Investigate why Ascii file writing in thread works ok as long as next scan does not also start writing ascii data.
					if (genAscii) {
						createAsciiFiles(file);
					}

					double timeTaken = ( System.nanoTime() - startTime )*1e-9;
					String endMessage = String.format("%s finished after %.2f seconds.\n", threadInfo, timeTaken);

					InterfaceProvider.getTerminalPrinter().print(endMessage);
					logger.info(endMessage);

				} catch (Exception e) {
					logger.error("Updating the nexus file failed.", e);
				}
			}
		} );
		fileWritingThread.start();
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
			avgDataset = DatasetFactory.zeros(DoubleDataset.class, 0, numberOfChannels);
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

	/**
	 * Add line of spectrum to a StringBuilder object using supplied Datasets.
	 * @param numberFormat -  formatter used to convert decimal values to String
	 * @param spectraNumber - channel (pixel number)
	 * @param showChannelNumber - prepend spectrum number
	 * @param energyData - energy values to use for each channel
	 * @param datasets - datasets to extract values from
	 * @since 19/1/2016
	 */
	private void addSpectraLine( StringBuilder strBuilder, DecimalFormat numberFormat, int spectraNumber, int channelNumber, boolean showChannelNumber, DoubleDataset energyData, DoubleDataset...datasets) {
		strBuilder.append( spectraNumber );

		if ( showChannelNumber ) {
			strBuilder.append( "\t" );
			strBuilder.append( channelNumber );
		}

		strBuilder.append( "\t" );
		strBuilder.append( numberFormat.format( energyData.get(channelNumber) ) );

		for ( DoubleDataset dataset : datasets ) {
			strBuilder.append( "\t" );
			strBuilder.append( numberFormat.format( dataset.get(spectraNumber, channelNumber) ) );
		}
		strBuilder.append("\n");
	}

	/**
	 * Write spectra to ascii file.
	 * @param writer
	 * @param showChannelNumber
	 * @param energyData
	 * @param datasets
	 * @throws Exception
	 * @since 19/1/2016
	 */
	private void writeSpectra( FileWriter writer, boolean showChannelNumber, DoubleDataset energyData, DoubleDataset...datasets) throws Exception {
		writeSpectra( writer, "", showChannelNumber,  energyData, datasets);
	}

	/**
	 * Write spectra to ascii file.
	 * Each spectrum is constructed as single String using Stringbuilder and written to file using single write call.
	 * This method is much faster (~8 times) than writing a line at a time using String.format(...)
	 * @param writer
	 * @param prefix
	 * @param showChannelNumber
	 * @param energyData
	 * @param datasets
	 * @throws Exception
	 * @since 19/1/2016
	 */
	private void writeSpectra( FileWriter writer, String prefix, boolean showChannelNumber, DoubleDataset energyData, DoubleDataset...datasets) throws Exception {

		if ( datasets.length == 0 ) {
			return;
		}

		int numSpectra = datasets[0].getShape()[0];
		int numChannels = energyData.getShape()[0];

		StringBuilder strBuilder = new StringBuilder();
		DecimalFormat decimalFormatter = new DecimalFormat(" 0.0000000000;-0.0000000000");

		for (int i = 0; i < numSpectra; i++) {
			for( int j = 0; j < numChannels; j++ ) {
				if ( prefix.length() > 0 ) {
					strBuilder.append( prefix );
				}
				addSpectraLine( strBuilder, decimalFormatter, i, j, showChannelNumber, energyData, datasets);
			}
			writer.write(strBuilder.toString());
			strBuilder.setLength(0);
		}
	}

	/**
	 * Write raw It spectra to ascii text file
	 * @param writer
	 * @param energyData
	 * @param itiCorrectedAvgData
	 * @param avgLogI0It
	 * @param itiAvgData
	 * @param itDarkData
	 * @throws Exception
	 * @since 19/1/2016
	 */
	private void writeItRawSpectra( FileWriter writer, DoubleDataset energyData, DoubleDataset itiCorrectedAvgData,
			DoubleDataset avgLogI0It, DoubleDataset itiAvgData,  DoubleDataset itDarkData ) throws Exception {

		int numSpectra = itiCorrectedAvgData.getShape()[0];
		int numChannels = energyData.getShape()[0];

		StringBuilder strBuilder = new StringBuilder();
		DecimalFormat decimalFormatter = new DecimalFormat(" 0.0000000000;-0.0000000000");

		for (int i = 0; i < numSpectra; i++) {
			for( int j = 0; j < numChannels; j++ ) {
				addSpectraLine( strBuilder, decimalFormatter, i, j, true, energyData, itiCorrectedAvgData, avgLogI0It, itiAvgData);
				// adjust length so we can overwrite the newline at end and append 'dark current' data...
				strBuilder.setLength( strBuilder.length() -1 );
				strBuilder.append( "\t" );
				strBuilder.append( decimalFormatter.format( itDarkData.get(0,j))) ;
				strBuilder.append( "\n" );
			}
			writer.write(strBuilder.toString());
			strBuilder.setLength(0);
		}
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
		String sampleDetails = file.getAttributeValue(NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.META_DATA_NAME + "@" + EdeDataConstants.SAMPLE_DETAILS_NAME);
		if (sampleDetails!=null) {
			scannablesDescription += "\n# Sample details : "+sampleDetails;
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

			writeSpectra( writer, "0", true, energyData,  i0iCorrectedDataSet, i0iDataSet, i0darkDataSet );

			if (i0fCorrectedDataSet != null) {
				// Originally, i0iCorrectedDataSet values appear in *two* columns, should it not be i0iCorrectedDataSet and i0fCorrectedDataSet instead?
				writeSpectra( writer, "1", true, energyData,  i0fCorrectedDataSet, i0fData, i0darkDataSet );
			}
		} catch (Exception e) {
			logger.error("Unable to create " + filePathName, e);
		} finally {
			writer.close();
		}
		itNormalisedWithI0iData.getShape();
		DoubleDataset avgLogI0It = getDataFromFile(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "/" + EdeDataConstants.DATA_COLUMN_NAME);

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

			long startTime = System.nanoTime();
			writeItRawSpectra( writer, energyData, itiCorrectedAvgData,  avgLogI0It, itiAvgData,  itDarkData );

			writer.close();
			long endTime = System.nanoTime();
			logger.info( String.format("Raw It data write to Ascii took %.2f secs\n",(endTime-startTime)*1e-9) );

		} catch (Exception e) {
			logger.error("Unable to create " + filePathName, e);
		} finally {
			writer.close();
		}

		String itiFilePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.IT_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
		String itFFilePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.LN_I0_IT__FINAL_I0_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
		String itAvgFileFPathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
		String header = "# index\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t" + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "\n";

		FileWriter itiWriter = new FileWriter(itiFilePathName);
		FileWriter itffWriter = new FileWriter(itFFilePathName);
		FileWriter itavgWriter = new FileWriter(itAvgFileFPathName);
		try {
			DoubleDataset i0f = getDataFromFile(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT__FINAL_I0_COLUMN_NAME + "/" + EdeDataConstants.DATA_COLUMN_NAME);
			DoubleDataset i0avg = getDataFromFile(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME + "/" + EdeDataConstants.DATA_COLUMN_NAME);

			long startTime = System.nanoTime();

			writeMetaData(scannablesDescription, metaData, itiWriter);
			itiWriter.write(header);
			writeSpectra( itiWriter, false, energyData, avgLogI0It );
			itiWriter.close();

			writeMetaData(scannablesDescription, metaData, itffWriter);
			itffWriter.write(header);
			writeSpectra( itffWriter, false, energyData, i0f );
			itffWriter.close();

			writeMetaData(scannablesDescription, metaData, itavgWriter);
			itavgWriter.write(header);
			writeSpectra( itavgWriter, false, energyData, i0avg );
			itavgWriter.close();

			long endTime = System.nanoTime();
			logger.info( String.format("Processed data write to Ascii took %.2f secs\n", (endTime-startTime)*1e-9) );
		} catch (Exception e) {
			logger.error("Unable to create " + filePathName, e);
		} finally {
			itiWriter.close();
			itffWriter.close();
			itavgWriter.close();
		}

		if (iRefiNormalisedData != null) {
			// Create IRef_raw
			metaData = getDataFromFile(file, META_DATA_PATH + EdeDataConstants.IREF_DATA_NAME);
			filePathName = assciiFolder + DataFileHelper.getFileNameWithSuffixAndExt(nexusFile, EdeDataConstants.IREF_RAW_DATA_NAME, EdeDataConstants.ASCII_FILE_EXTENSION);
			writer = new FileWriter(filePathName);
			try {
				writeMetaData(scannablesDescription, metaData, writer);
				writer.write("# index\t" + EdeDataConstants.STRIP_COLUMN_NAME + "\t" + EdeDataConstants.ENERGY_COLUMN_NAME + "\t"
						+ EdeDataConstants.IREF_DATA_NAME + "\t" + EdeDataConstants.LN_I0_IREF_COLUMN_NAME + "\t" + EdeDataConstants.IREF_RAW_DATA_NAME + "\t"
						+ EdeDataConstants.IT_DARK_COLUMN_NAME + "\n");

				writeSpectra( writer, true, energyData, iRefiCorrecteddata, iRefiNormalisedData, iRefidata, iRefDarkData);

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

				writeSpectra( writer, false, energyData, iRefiNormalisedData);

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

					writeSpectra( writer, false, energyData, iReffNormalisedData );

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
		String targetPath;

		if (itNormalisedWithI0iData != null) {
			targetPath = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_COLUMN_NAME + "/", Nexus.DATA);
			checkCyclicDataAndAddData(file, targetPath, avgSpectraList, excludedCycles, itNormalisedWithI0iData, attributes);
			addLinks(file, targetPath);
		}

		if (itNormalisedWithI0fData != null) {
			targetPath = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT__FINAL_I0_COLUMN_NAME + "/", Nexus.DATA);
			checkCyclicDataAndAddData(file, targetPath, avgSpectraList, excludedCycles, itNormalisedWithI0fData, attributes);
			addLinks(file, targetPath);
		}

		if (itNormalisedWithAvgI0iAndI0fData != null) {
			targetPath = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME + "/",	Nexus.DATA);
			checkCyclicDataAndAddData(file, targetPath, avgSpectraList, excludedCycles, itNormalisedWithAvgI0iAndI0fData, attributes);
			addLinks(file, targetPath);
		}

		if (itNormalisedWithInterpolatedI0iAndI0fData != null) {
			targetPath = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IT_INTERP_I0S_COLUMN_NAME + "/",	Nexus.DATA);
			checkCyclicDataAndAddData(file, targetPath, avgSpectraList, excludedCycles, itNormalisedWithInterpolatedI0iAndI0fData, attributes);
			addLinks(file, targetPath);
		}

		if (iRefiNormalisedData != null) {
			targetPath = HierarchicalDataFileUtils.createParentEntry(file, NEXUS_ROOT_ENTRY_NAME + EdeDataConstants.LN_I0_IREF_COLUMN_NAME + "/", Nexus.DATA);
			addDatasetToNexus(file, EdeDataConstants.DATA_COLUMN_NAME, targetPath, iRefiNormalisedData, attributes);
		}
	}

	private void checkCyclicDataAndAddData(IHierarchicalDataFile file, String fullPath, RangeData[] avgSpectraList, int[] excludedCycles, DoubleDataset data, Map<String, String> attributes) throws Exception {
		if (data == null)
			return;
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
			DoubleDataset dataToAvgAndAdd = DatasetFactory.zeros(DoubleDataset.class, 0, noOfChannels);
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
		file.createLink(targetPath, EdeDataConstants.PIXEL_COLUMN_NAME, this.getDetectorDataPath() + EdeDataConstants.PIXEL_COLUMN_NAME);
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
	}

	private String getDetectorDataPath() {
		return NEXUS_ROOT_ENTRY_NAME + getDetectorNodeName() + "/";
	}

	private String getDetectorNodeName() {
		return getDetectorName4Node();
	}

	private static class Index {
		public final int start;
		public int end;
		public Index(int start) {
			end = this.start = start;
		}
		public Index(int start, int end) {
			this.start = start;
			this.end = end;
		}
		public Index(List<Integer> list) {
			if (list!=null && list.size()>0) {
				this.start = list.get(0);
				this.end = list.get(list.size()-1);
			} else {
				this.start = this.end=-1;
			}
		}
	}

	private List<Integer> getIndicesOfMatchingValues(Dataset scanTypeData, Dataset posTypeData, EdeScanType scanType, EdePositionType posType ) {
		return getIndicesOfMatchingValues(scanTypeData, posTypeData, scanType.getValue(), posType.getValue());
	}

	private List<Integer> getIndicesOfMatchingValues(Dataset dataset1, Dataset dataset2, int val1, int val2) {
		List<Integer> indices = new ArrayList<Integer>();
		int maxIndex = Math.min(dataset1.getSize(), dataset2.getSize());
		for(int i=0; i<maxIndex; i++) {
			if (dataset1.getInt(i) == val1 && dataset2.getInt(i) == val2) {
				indices.add(i);
			}
		}
		return indices;
	}

	private Integer getLastItem(List<Integer> items) {
		if (items!=null) {
			return items.get(items.size() - 1);
		} else {
			return null;
		}
	}

	private void deriveTimingGroupsAndGenerateNormalisedData(IHierarchicalDataFile file) throws Exception {
		DoubleDataset rawDataset = getDetectorDataFromFile(file, EdeDataConstants.DATA_COLUMN_NAME);
		DoubleDataset frameDataset = getDetectorDataFromFile(file, EdeDataConstants.FRAME_COLUMN_NAME);
		DoubleDataset timingDataset = getDetectorDataFromFile(file, EdeDataConstants.TIMINGGROUP_COLUMN_NAME);
		DoubleDataset cycleDataset = getDetectorDataFromFile(file, EdeDataConstants.CYCLE_COLUMN_NAME);
		DoubleDataset beamInOutDataset = getDetectorDataFromFile(file, EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME);
		DoubleDataset itDataset = getDetectorDataFromFile(file, EdeDataConstants.IT_COLUMN_NAME);

		if (rawDataset.getShape()[0] != frameDataset.getShape()[0] ||
				rawDataset.getShape()[0] != timingDataset.getShape()[0] ||
				rawDataset.getShape()[0] != cycleDataset.getShape()[0] ||
				rawDataset.getShape()[0] != beamInOutDataset.getShape()[0]) {
			throw new Exception("Incompatible datasets");
		}

		// Set Iref Index to null (whether Iref data is present depends on scan type)
		Index iRefdarkDataSetIndex = null;
		Index i0ForIRefDataSetIndex = null;
		Index iRefidataSetIndex = null;
		Index iReffdataSetIndex = null;

		double cycleIndexValue = -1d;

		// Get indices in raw data of Light/Dark, Inbeam/Outbeam spectra...

		// Spectra collected before It...
		List<Integer> darkI0Indices = getIndicesOfMatchingValues(beamInOutDataset, itDataset, EdeScanType.DARK, EdePositionType.OUTBEAM);
		List<Integer> darkItIndices = getIndicesOfMatchingValues(beamInOutDataset, itDataset, EdeScanType.DARK, EdePositionType.INBEAM);
		List<Integer> darkIrefIndices = getIndicesOfMatchingValues(beamInOutDataset, itDataset, EdeScanType.DARK, EdePositionType.REFERENCE);
		// light I0 spectra before *and* after It collection
		List<Integer> lightI0Indices = getIndicesOfMatchingValues(beamInOutDataset, itDataset, EdeScanType.LIGHT, EdePositionType.OUTBEAM);

		// Main It spectra
		List<Integer> lightItIndices = getIndicesOfMatchingValues(beamInOutDataset, itDataset, EdeScanType.LIGHT, EdePositionType.INBEAM);
		// Reference spectra
		List<Integer> lightIrefIndices = getIndicesOfMatchingValues(beamInOutDataset, itDataset, EdeScanType.LIGHT, EdePositionType.REFERENCE);

		// Out of beam -> I0 for Iref
		List<Integer> lightIrefOutBeamIndices = getIndicesOfMatchingValues(beamInOutDataset, itDataset, EdeScanType.LIGHT, EdePositionType.OUTBEAM_REFERENCE);

		for (int i = 0; i < rawDataset.getShape()[0]; i++) {
			logger.info("Raw Dataset number: {}; Scan Type (0:DARK, 1:LIGHT): {}; Position Type (0:OUTBEAM, 1:INBEAM, 2:OUTBEAM_REFERENCE, 3:REFERENCE): {}.",i,beamInOutDataset.get(i), itDataset.get(i));
		}

		Index darkI0DataSetIndex = new Index(darkI0Indices);
		Index darkItDataSetIndex = new Index(darkItIndices);
		Index lightI0DataSetIndex = new Index(lightI0Indices.get(0));
		// Adjust light I0 end index for multiple timing groups
		int maxTimingGroupIndex = timingDataset.getInt( timingDataset.maxPos() );
		int numTimingGroups = maxTimingGroupIndex+1;
		lightI0DataSetIndex.end = lightI0DataSetIndex.start+numTimingGroups-1;

		// Light I0 final (no final measurement for single spectrum)
		Index lightI0FinalDataSetIndex = null;
		if(lightI0Indices.size()==2*numTimingGroups){
			lightI0FinalDataSetIndex = new Index(lightI0Indices.get(numTimingGroups));
			lightI0FinalDataSetIndex.end = lightI0FinalDataSetIndex.start+numTimingGroups-1;
		}

		// Iref indices ...
		if (darkIrefIndices.size()>0) {
			iRefdarkDataSetIndex = new Index(darkIrefIndices);
		}
		if (lightIrefOutBeamIndices.size()>0) {
			i0ForIRefDataSetIndex = new Index(lightIrefOutBeamIndices);
		}
		if (lightIrefIndices.size()==2) {
			iRefidataSetIndex = new Index(lightIrefIndices.get(0));
			iReffdataSetIndex = new Index(lightIrefIndices.get(1));
		}

		Index lightItDataSetIndex = new Index(lightItIndices.get(0), lightItIndices.get(lightItIndices.size()-1));


		// If only 1 timing group, check for multiple It collections
		if (numTimingGroups==1 && beamInOutDataset.getSize()>4) {
			// Determine number of times It collection is repeated
			int maxFrame = frameDataset.getInt(frameDataset.maxPos());
			List<Integer> maxFrameIndices = getIndicesOfMatchingValues(beamInOutDataset, frameDataset, EdeScanType.LIGHT.getValue(), maxFrame);
			int numRepeatedSpectra = maxFrameIndices.size();
			numTimingGroups = numRepeatedSpectra;
		}

		int[] timingGroups = new int[numTimingGroups];

		// Cycles
		int frameIndex = -1;
		int cycleCount = 0;
		int maxCycle = -1;
		for(Integer index : lightItIndices) {
			if (cycleDataset.getInt(index) > maxCycle) {
				maxCycle = cycleDataset.getInt(index);
				cycleCount++;
			}
			if (frameDataset.get(index) == 0.0) {
				frameIndex++;
			}
			if(frameIndex<timingGroups.length) {
				timingGroups[frameIndex] = (int) frameDataset.get(index) + 1;
			}
		}

		if (darkI0DataSetIndex != null) {
			i0darkDataSet = getSlice(rawDataset, darkI0DataSetIndex);
		}
		i0iDataSet = getSlice(rawDataset, lightI0DataSetIndex);
		i0iCorrectedDataSet = i0iDataSet.clone().isubtract(i0darkDataSet);

		if (darkItDataSetIndex !=null) {
			itDarkData = getSlice(rawDataset, darkItDataSetIndex);
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

		itData = getSlice(rawDataset, lightItDataSetIndex);
		convertToCycledData(itData, cycleCount);
		itCorrectedDataSet = itData.clone();

		// Null check added (so data from 'single spectrum' collection can also be written.
		if ( itDarkData != null ) {
			correctItData(itDarkData, itCorrectedDataSet, timingGroups);
		} else if ( i0darkDataSet != null ) {
			correctItData(i0darkDataSet, itCorrectedDataSet, timingGroups);
		}

		itNormalisedWithI0iData = createNormalisedItData(i0iCorrectedDataSet, itCorrectedDataSet, timingGroups);
		if(lightI0FinalDataSetIndex != null) {
			i0fData = getSlice(rawDataset, lightI0FinalDataSetIndex);
			i0fCorrectedDataSet = i0fData.clone().isubtract(i0darkDataSet);
			itNormalisedWithI0fData = createNormalisedItData(i0fCorrectedDataSet, itCorrectedDataSet, timingGroups);
			i0iAndI0fCorrectedAvgData = i0iCorrectedDataSet.clone().iadd(i0fCorrectedDataSet).idivide(2);
			itNormalisedWithAvgI0iAndI0fData = createNormalisedItData(i0iAndI0fCorrectedAvgData, itCorrectedDataSet, timingGroups);
			itNormalisedWithInterpolatedI0iAndI0fData = createNormalisedItDataInterpolated(i0iCorrectedDataSet, i0fCorrectedDataSet, itCorrectedDataSet, timingGroups);
		}
	}

	/**
	 * Create normalised lnI0It using I0 linear interpolation between initial and final I0 spectra for each spectrum.
	 * Interpolation fraction is indexOfCurrentSpectrum/sum(timingGroups).
	 * Probably only really meaningful for single timing group, and if I0 initial and I0 final are within same topup cycle.
	 * @param i0InitialCorrectedDataSet
	 * @param i0FinalCorrectedDataSet
	 * @param itCorrectedCycledData
	 * @param timingGroups
	 * @return
	 */
	private DoubleDataset createNormalisedItDataInterpolated(DoubleDataset i0InitialCorrectedDataSet, DoubleDataset i0FinalCorrectedDataSet, DoubleDataset itCorrectedCycledData, int[] timingGroups) {

		int[] shape = itCorrectedCycledData.getShape();
		int noOfCycles = shape[0];
		int numberOfChannels = shape[2];
		int totNumSpectraPerCycle = 0;
		for(int i=0; i<timingGroups.length; i++) {
			totNumSpectraPerCycle+=timingGroups[i];
		}

		DoubleDataset normalisedData = DatasetFactory.zeros(DoubleDataset.class, itCorrectedCycledData.getShape());
		for (int cycle = 0; cycle < noOfCycles; cycle++) {
			int spectraCountInCycle=0;
			int lastSpectrumInGroup = 0;
			int firstSpectrumInGroup = 0;
			for (int groupIndex = 0; groupIndex < timingGroups.length; groupIndex++) {

				int i0GroupIndexIndex = 0;
				if (groupIndex<i0InitialCorrectedDataSet.getShape()[0]) {
					i0GroupIndexIndex=groupIndex;
				}
				// Initial and final I0 for group :
				DoubleDataset i0Dataset, i0FinalDataset;
				i0Dataset = ((DoubleDataset) i0InitialCorrectedDataSet.getSlice(new int[]{i0GroupIndexIndex, 0},new int[]{i0GroupIndexIndex + 1, numberOfChannels}, null).squeeze());
				i0FinalDataset = ((DoubleDataset) i0FinalCorrectedDataSet.getSlice(new int[]{i0GroupIndexIndex, 0},new int[]{i0GroupIndexIndex + 1, numberOfChannels}, null).squeeze());

				// Change between initial and final I0 for each spectrum in cycle
				Dataset deltaI0PerSpectrum = DatasetFactory.createFromObject(i0FinalDataset);
				deltaI0PerSpectrum.isubtract(i0Dataset);

				lastSpectrumInGroup += timingGroups[groupIndex];
				for (int spectrumIndex = firstSpectrumInGroup; spectrumIndex < lastSpectrumInGroup; spectrumIndex++) {
					DoubleDataset itDataset = ((DoubleDataset) itCorrectedCycledData.getSliceView(new int[]{cycle, spectrumIndex, 0}, new int[]{cycle + 1, spectrumIndex + 1, numberOfChannels}, null).squeeze());
					double frac = (double)spectraCountInCycle/(totNumSpectraPerCycle-1.0);
					for (int channel = 0; channel < numberOfChannels; channel++) {
						// Get interpolated I0 value for channel :
						double i0Interpolated = i0Dataset.get(channel)+ frac*deltaI0PerSpectrum.getDouble(channel);
						double value = calcLnI0It(i0Interpolated, itDataset.getDouble(channel));
						normalisedData.set(value, new int[]{cycle, spectrumIndex, channel});
					}
					spectraCountInCycle++;
				}
				firstSpectrumInGroup = spectraCountInCycle;
			}
		}
		return normalisedData;
	}

	private void createAxisForNormalisedItData(IHierarchicalDataFile file, RangeData[] avgSpectraList) throws Exception {
		DoubleDataset metaDataset = getDataFromFile(file, META_DATA_PATH + EdeDataConstants.IT_COLUMN_NAME);
		TimingGroupMetadata[] timingGroupMetaData = TimingGroupMetadata.toTimingGroupMetaData(metaDataset);
		int totalSpectra = 0;
		int noOfGroups = timingGroupMetaData.length;
		for (int i = 0; i < noOfGroups; i++) {
			totalSpectra += timingGroupMetaData[i].getNoOfFrames();
		}
		int totNumLightItSpectra = itData.getShape()[1];
		totalSpectra = Math.max(totalSpectra, totNumLightItSpectra);

		int totalAvgSpectra  = totalSpectra;
		if (avgSpectraList != null) {
			for (int i = 0; i < avgSpectraList.length; i++) {
				totalAvgSpectra -= avgSpectraList[i].getEndIndex() - avgSpectraList[i].getStartIndex();
			}
		}
		timeAxisData = DatasetFactory.zeros(DoubleDataset.class, totalAvgSpectra);
		groupAxisData = DatasetFactory.zeros(DoubleDataset.class, totalAvgSpectra);
		int currentGroupIndex = 0;
		int j = 0;
		int k = 0;
		int l = 0;
		RangeData avgRange = null;
		boolean requireTimeZero=true;
		double time = 0.0d;
		int totalSpectraUptoCurrentGroup = timingGroupMetaData[currentGroupIndex].getNoOfFrames();
		if (getDetectorNodeName().equals("frelon")) {
			requireTimeZero=false;
		}
		for (int i = 0; i < totalSpectra; i++) {
			if (requireTimeZero) {
				timeAxisData.set(time, k++);
			}

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

			if ( !requireTimeZero ) {
				timeAxisData.set(time, k++);
			}

			if (i == totalSpectraUptoCurrentGroup) {
				currentGroupIndex++;
				if (currentGroupIndex>timingGroupMetaData.length-1) {
					currentGroupIndex=0;
				}
				totalSpectraUptoCurrentGroup += timingGroupMetaData[currentGroupIndex].getNoOfFrames();
			}
			groupAxisData.set(currentGroupIndex, l++);
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
				DoubleDataset darkDataset;
				if (groupIndex<itDarkData.getShape()[0]) {
					darkDataset = ((DoubleDataset) itDarkData.getSlice(new int[]{groupIndex, 0},new int[]{groupIndex + 1, numberOfChannels}, null).squeeze());
				} else {
					darkDataset = ((DoubleDataset) itDarkData.getSlice(new int[]{0, 0},new int[]{1, numberOfChannels}, null).squeeze());
				}
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
		DoubleDataset normalisedData = DatasetFactory.zeros(DoubleDataset.class, itCorrectedCycledData.getShape());
		for (int cycle = 0; cycle < noOfCycles; cycle++) {
			for (int groupIndex = 0; groupIndex < timingGroups.length; groupIndex++) {
				DoubleDataset i0Dataset;
				if (groupIndex<i0CorrectedDataSet.getShape()[0]) {
					i0Dataset = ((DoubleDataset) i0CorrectedDataSet.getSlice(new int[]{groupIndex, 0},new int[]{groupIndex + 1, numberOfChannels}, null).squeeze());
				} else {
					i0Dataset = ((DoubleDataset) i0CorrectedDataSet.getSlice(new int[]{0, 0},new int[]{1, numberOfChannels}, null).squeeze());
				}
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
		DoubleDataset normalisedData = DatasetFactory.zeros(DoubleDataset.class, 1, numberOfChannels);
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
		if (index.start>-1 && index.end>-1) {
			return (DoubleDataset) rawDataset.getSlice(new int[]{index.start, 0}, new int[]{index.end + 1, rawDataset.getShape()[1]}, null);
		} else
			return null;
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
			DoubleDataset data = DatasetFactory.createFromObject(DoubleDataset.class, value);
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

	public void setDetectorName4Node(String name) {
		detectorName4Node=name;

	}
}
