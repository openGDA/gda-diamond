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
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.lang.ArrayUtils;
import org.dawnsci.ede.DataFileHelper;
import org.dawnsci.ede.EdeDataConstants;
import org.dawnsci.ede.EdeDataConstants.TimingGroupMetadata;
import org.dawnsci.ede.TimeResolvedDataFileHelper;
import org.eclipse.dawnsci.analysis.api.tree.DataNode;
import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.january.dataset.IntegerDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Scannable;
import gda.device.detector.EdeDetector;
import gda.scan.EdeScan;
import gda.scan.EnergyDispersiveExafsScan;
import gda.scan.ScanDataPoint;

public class EdeTimeResolvedExperimentDataWriter extends EdeExperimentDataWriter {

	private static final Logger logger = LoggerFactory.getLogger(EdeTimeResolvedExperimentDataWriter.class);

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

	private final String nexusfileName;
	private boolean writeAsciiData   = true;
	private boolean writeInNewThread = false;


	public EdeTimeResolvedExperimentDataWriter(EnergyDispersiveExafsScan i0DarkScan, EnergyDispersiveExafsScan i0LightScan, EnergyDispersiveExafsScan iRefScan,
			EnergyDispersiveExafsScan iRefDarkScan, EnergyDispersiveExafsScan itDarkScan, EnergyDispersiveExafsScan[] itScans, EnergyDispersiveExafsScan i0FinalScan, EnergyDispersiveExafsScan iRefFinalScan,
			EdeDetector theDetector, String nexusfileName) {
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
	public String writeDataFile(EdeDetector detector) throws Exception {
		//		validateData(detector);
		TimeResolvedDataFileHelper timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(nexusfileName);

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
		String sampleDetails = getSampleDetails();
		timeResolvedNexusFileHelper.setDetectorName4Node(itScans[0].getDetector().getName());
		timeResolvedNexusFileHelper.createMetaDataEntries(i0ScanMetaData, itScanMetaData, i0ForIRefScanMetaData, irefScanMetaData, scannablesConfiguration, energyCalibration, sampleDetails);
		timeResolvedNexusFileHelper.updateWithNormalisedData(writeAsciiData, writeInNewThread);

		addDataForExtraScannables();

		return itFilename;
	}

	/**
	 * Get Dataset from Nexus file
	 * @param file
	 * @param groupName name of group to read ( /entry1)
	 * @param dataName
	 * @return
	 * @throws NexusException
	 * @throws DatasetException
	 */
	private IDataset getDataset(NexusFile file, String groupName, String dataName) throws NexusException, DatasetException {
		GroupNode group = file.getGroup("/entry1/" + groupName, false);
		DataNode d = file.getData(group, dataName);
		return d.getDataset().getSlice(null, null, null);
	}

	private void addDataset(NexusFile file, String groupName, String dataName, Dataset dataset) throws NexusException {
		DataNode dataNode = file.createData("/entry1/"+groupName, dataName, dataset, true);
	}

	/**
	 * Create datasets in detector group for the extra scannables.
	 * Values corresponding to 'light It' measurements are extracted and placed in the groups.
	 */
	private void addDataForExtraScannables() {
		if (extraScannables == null) {
			return;
		}

		try(NexusFile file = NexusFileHDF5.openNexusFile(nexusfileName)) {

			// Load dataset with 'beam in/out' and 'It' indices from Nexus file :
			String detectorName = itScans[0].getDetector().getName();
			IDataset beamInOutDataset = getDataset(file, detectorName, EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME);
			IDataset itDataset = getDataset(file, detectorName, EdeDataConstants.IT_COLUMN_NAME);
			if (beamInOutDataset.getShape()[0] != itDataset.getShape()[0]) {
				logger.warn("'in beam' and 'it' index datasets do not match, not adding processed 'extra scannable' data");
				return;
			}

			// Make dataset of which spectra correspond to 'light It' measurements (light It=1, otherwise 0)
			int totalNumSpectra = itDataset.getShape()[0];
			Dataset lightIt = DatasetFactory.zeros(IntegerDataset.class, totalNumSpectra);
			for(int i=0; i<totalNumSpectra; i++) {
				if ( beamInOutDataset.getInt(i)==1 && itDataset.getInt(i) == 1 ) {
					lightIt.set(1, i);
				}
			}

			// Names of all the detector groups
			final String[] detectorGroupList = { EdeDataConstants.LN_I0_IT_COLUMN_NAME, EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME,
					EdeDataConstants.LN_I0_IT_FINAL_I0_COLUMN_NAME, EdeDataConstants.LN_I0_IT_INTERP_I0S_COLUMN_NAME };

			for(Scannable scn : extraScannables) {

				logger.debug("Adding data for scannable {}", scn.getName());

				// Extract values from the 'raw' dataset corresponding to the 'light It' spectra
				String scannableName = scn.getName();
				IDataset rawData = getDataset(file, detectorName, scannableName);
				List<Double> values = new ArrayList<>();
				for(int i=0; i<totalNumSpectra; i++) {
					if (lightIt.getInt(i) == 1) {
						values.add( rawData.getDouble(i));
					}
				}

				// Create new dataset and add it to the first detector group ((lnI0It)
				Dataset scannableValues = DatasetFactory.createFromList(values);
				addDataset(file, detectorGroupList[0], scannableName, scannableValues);

				// Add links to the dataset in the other groups
				String source = "/entry1/"+detectorGroupList[0]+"/"+scannableName;
				for(int i=1; i<detectorGroupList.length; i++) {
					file.link(source, "/entry1/"+detectorGroupList[i]+"/"+scannableName);
				}

			}
		} catch (NexusException | DatasetException e) {
			logger.warn("Problem adding processed data for 'extra scannables'", e);
		}
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

	private List<Scannable> extraScannables = null;
	public void setExtraScannables(List<Scannable> scannablesToMonitorDuringScan) {
		extraScannables = scannablesToMonitorDuringScan;
	}

}
