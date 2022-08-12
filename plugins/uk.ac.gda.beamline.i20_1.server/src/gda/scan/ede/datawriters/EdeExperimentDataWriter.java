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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.dawnsci.ede.EdeDataConstants;
import org.dawnsci.ede.EdeDataConstants.TimingGroupMetadata;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.data.scan.datawriter.AsciiMetadataConfig;
import gda.device.Scannable;
import gda.device.detector.EdeDetector;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import uk.ac.gda.ede.data.AlignmentParametersBean;
import uk.ac.gda.ede.data.ClientConfig;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public abstract class EdeExperimentDataWriter {

	private static final Logger logger = LoggerFactory.getLogger(EdeExperimentDataWriter.class);

	protected String filenameTemplate = "";
	protected EdeDetector theDetector;
	private String sampleDetails;

	protected final DoubleDataset energyDataSet;

	protected Collection<Scannable> extraScannables = null;
	protected String nexusfileName;

	public abstract String getAsciiFilename();

	public EdeExperimentDataWriter(DoubleDataset energyDataSet, String nexusFileName) {
		this.energyDataSet = energyDataSet;
		this.nexusfileName = nexusFileName;
	}

	public static Double calcLnI0It(Double i0_corrected, Double it_corrected) {
		Double lni0it = Math.log(i0_corrected / it_corrected);
		if (lni0it.isNaN() || lni0it.isInfinite() /*|| lni0it < 0.0*/) {
			lni0it = .0;
		}
		return lni0it;
	}

	public static DoubleDataset normaliseDatasset(DoubleDataset itRaw, DoubleDataset i0Raw, DoubleDataset dark) {

		double[] itRawArray = itRaw.getData();
		double[] i0RawArray = i0Raw.getData();
		double[] darkArray = dark.getData();

		double[] itNormaliseArray = new double[itRawArray.length];

		for (int channel = 0; channel < itNormaliseArray.length; channel++) {
			itNormaliseArray[channel] = calcLnI0It(i0RawArray[channel]-darkArray[channel],itRawArray[channel]-darkArray[channel]);
		}

		return DatasetFactory.createFromObject(DoubleDataset.class, itNormaliseArray);
	}

	public static DoubleDataset normaliseDatasset(DoubleDataset it, DoubleDataset i0) {

		double[] itArray = it.getData();
		double[] i0Array = i0.getData();
		double[] itNormaliseArray = new double[itArray.length];

		for (int channel = 0; channel < itNormaliseArray.length; channel++) {
			itNormaliseArray[channel] = calcLnI0It(i0Array[channel],itArray[channel]);
		}

		return DatasetFactory.createFromObject(DoubleDataset.class, itNormaliseArray);

	}

	public abstract String writeDataFile(EdeDetector detector) throws Exception;

	protected EdeDataConstants.TimingGroupMetadata[] createTimingGroupsMetaData(EdeScanParameters scanParameters) {
		return createTimingGroupsMetaData(scanParameters, 0);
	}

	protected EdeDataConstants.TimingGroupMetadata[] createTimingGroupsMetaData(EdeScanParameters scanParameters, double accumulationReadoutTime) {
		TimingGroupMetadata[] metaData = new TimingGroupMetadata[scanParameters.getGroups().size()];
		for (int i = 0; i < scanParameters.getGroups().size(); i++) {
			TimingGroup group = scanParameters.getGroups().get(i);
			double timePerFrame = group.getTimePerFrame();
			if (accumulationReadoutTime > 0) {
				timePerFrame = (group.getTimePerScan() + accumulationReadoutTime)*group.getNumberOfScansPerFrame();
			}
			metaData[i] = new TimingGroupMetadata(i, group.getNumberOfFrames(), group.getTimePerScan(),
					timePerFrame, group.getPreceedingTimeDelay(), group.getNumberOfScansPerFrame());
		}
		return metaData;
	}

	// FIXME
	protected String getScannablesConfiguration() {
		List<AsciiDataWriterConfiguration> configs = Finder.listFindablesOfType(AsciiDataWriterConfiguration.class);
		if (configs == null) {
			return "";
		}
		StringBuilder configBuilder = new StringBuilder();
		try {
			if (!configs.isEmpty()) {
				// Adding scannables
				AsciiDataWriterConfiguration config = configs.get(0);
				for (AsciiMetadataConfig line : config.getHeader()) {
					configBuilder.append(config.getCommentMarker() + " " + line.toString() + "\n");
				}
			}
			// Adding alignment parameters
			Object result = InterfaceProvider.getJythonNamespace().getFromJythonNamespace(ClientConfig.ALIGNMENT_PARAMETERS_RESULT_BEAN_NAME);
			if (result != null && (result instanceof AlignmentParametersBean)) {
				configBuilder.append("# " + result.toString() + "\n");
			}
		} catch (Exception e) {
			logger.error("Unable to get scannable configuration information", e);
		}
		return configBuilder.toString();
	}

	protected void log(String message) {
		InterfaceProvider.getTerminalPrinter().print(message);
		logger.info(message);
	}

	public void setSampleDetails(String sampleDetails) {
		this.sampleDetails = sampleDetails;
	}

	public String getSampleDetails() {
		return sampleDetails;
	}

	public void setExtraScannables(Collection<Scannable> scannablesToMonitorDuringScan) {
		extraScannables = scannablesToMonitorDuringScan;
	}

	/**
	 * Get list of cycles that may be incomplete - a cycle is incomplete if it contains fewer
	 * frames than the cycle with the most frames.
	 *
	 * @return
	 */
	protected List<Integer> getIncompleteCycles() {
		logger.info("Trying to create list of incomplete cycles");
		try(NexusFile file = NexusFileHDF5.openNexusFile(nexusfileName)) {
			String detectorName = theDetector.getName();
			List<Integer> lightItIndices = getLightItIndices(file);
			if (lightItIndices == null) {
				return Collections.emptyList();
			}

			IDataset cycles = getDataset(file, detectorName, EdeDataConstants.CYCLE_COLUMN_NAME);

			// Determine total number of cycles and frames per cycle
			int numCycles = cycles.max(true).intValue()+1;
			int[] framesPerCycle = new int[numCycles];
			lightItIndices.stream()
				.map(cycles::getInt)
				.forEach(cycle -> framesPerCycle[cycle]++);

			// Max frames in a cycle is the expected number of frames per cycle.
			int expectedNumFrames = IntStream.of(framesPerCycle).max().getAsInt();

			logger.debug("Frames per cycle : {}", Arrays.toString(framesPerCycle));
			logger.debug("Expected number of frames per cycle : {}", expectedNumFrames);

			// Return indices of cycles that do not contain expected number of frames.
			return IntStream.range(0, numCycles)
					.boxed()
					.filter(i -> framesPerCycle[i] != expectedNumFrames)
					.collect(Collectors.toList());

		} catch (NexusException | DatasetException e) {
			logger.error("Problem creating list of incomplete cycles", e);
		}
		return Collections.emptyList();
	}

	/**
	 * Create datasets in detector group for the extra scannables.
	 * Values corresponding to 'light It' measurements are extracted and placed in the groups.
	 */
	protected void addDataForExtraScannables() {
		if (extraScannables == null || nexusfileName == null) {
			return;
		}

		try(NexusFile file = NexusFileHDF5.openNexusFile(nexusfileName)) {

			List<Integer> lightItIndices = getLightItIndices(file);
			if (lightItIndices == null) {
				logger.warn("Could not add 'extra scannable' information to processed data");
				return;
			}

			// Names of all the detector groups
			final String[] detectorGroupList = { EdeDataConstants.LN_I0_IT_COLUMN_NAME, EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME,
					EdeDataConstants.LN_I0_IT_FINAL_I0_COLUMN_NAME, EdeDataConstants.LN_I0_IT_INTERP_I0S_COLUMN_NAME };

			String detectorName = theDetector.getName();

			for(Scannable scn : extraScannables) {

				logger.debug("Adding data for scannable {}...", scn.getName());

				for(String datasetName : scn.getInputNames()) {
					logger.debug("   Adding dataset {}", datasetName);

					// Extract values from the 'raw' dataset corresponding to the 'light It' spectra
					IDataset rawData = getDataset(file, detectorName, datasetName);
					List<Double> values = lightItIndices.stream()
							.map(rawData::getDouble)
							.collect(Collectors.toList());

					// Create new dataset and add it to the first detector group ((lnI0It)
					Dataset scannableValues = DatasetFactory.createFromList(values);
					addDataset(file, detectorGroupList[0], datasetName, scannableValues);

					// Add links to the dataset in the other groups
					String source = "/entry1/"+detectorGroupList[0]+"/"+datasetName;
					for(int i=1; i<detectorGroupList.length; i++) {
						String pathToGroup = "/entry1/"+detectorGroupList[i];
						if (file.isPathValid(pathToGroup)) {
							file.link(source, "/entry1/"+detectorGroupList[i]+"/"+datasetName);
						}
					}
				}

			}
		} catch (NexusException | DatasetException e) {
			logger.warn("Problem adding processed data to nexus file {} for 'extra scannables'", nexusfileName, e);
		}
	}

	/**
	 * Make list of which indices in raw data (darkI0, darkIt, lightI0, lightIt ...)
	 * correspond to 'light It' measurements
	 * @param file
	 * @return Dataset
	 * @throws NexusException
	 * @throws DatasetException
	 */
	private List<Integer> getLightItIndices(NexusFile file) throws NexusException, DatasetException {
		String detectorName = theDetector.getName();
		// Load dataset with 'beam in/out' and 'It' indices from Nexus file :
		IDataset beamInOutDataset = getDataset(file, detectorName, EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME);
		IDataset itDataset = getDataset(file, detectorName, EdeDataConstants.IT_COLUMN_NAME);
		if (beamInOutDataset.getShape()[0] != itDataset.getShape()[0]) {
			logger.warn("'in beam' and 'it' index dataset dimensions do not match.");
			return null;
		}

		// Make dataset of which spectra correspond to 'light It' measurements (light It=1, otherwise 0)
		int totalNumSpectra = itDataset.getShape()[0];
		List<Integer> lightItIndices = new ArrayList<>();
		for(int i=0; i<totalNumSpectra; i++) {
			if ( beamInOutDataset.getInt(i)==1 && itDataset.getInt(i) == 1 ) {
				lightItIndices.add(i);
			}
		}
		return lightItIndices;
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
}
