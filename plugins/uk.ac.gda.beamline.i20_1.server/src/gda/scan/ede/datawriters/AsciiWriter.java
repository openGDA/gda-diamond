/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.ArrayUtils;
import org.apache.commons.lang.StringUtils;
import org.eclipse.dawnsci.analysis.api.tree.Attribute;
import org.eclipse.dawnsci.analysis.api.tree.DataNode;
import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.january.dataset.ILazyDataset;
import org.eclipse.january.dataset.SliceND;
import org.eclipse.january.dataset.StringDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.extractor.NexusExtractor;
import gda.jython.InterfaceProvider;
import gda.scan.TurboXasNexusTree;
import gda.scan.TurboXasScan;

/**
 * Class to process Nexus files generated by {@link TurboXasScan}s and create ascii file.
 * Data is output in one block with the number of rows being number of energy points, and
 * different columns contain data for each spectrum for each data type.
 *
 */
public class AsciiWriter {

	private static final Logger logger = LoggerFactory.getLogger(AsciiWriter.class);

	private String[] detectorNames = null;
	private String[] dataToRead = {};
	private String nexusFilename;
	private String asciiFilename;
	private boolean ignoreNaNs = true;

	public AsciiWriter() {
	}

	/**
	 * Return list of all detectors in nexus file - names of group nodes that have 'NXData' for their 'NX_Class' attribute value
	 * @param file
	 * @return
	 * @throws NexusException
	 */
	private List<String> getDetectorNamesFromFile(String filename) throws NexusException {
		List<String> detectorNamesList = new ArrayList<>();

		try(NexusFile file = NexusFileHDF5.openNexusFileReadOnly(filename)) {
			Collection<String> nodeNames = file.getGroup("/entry1", false).getNames();
			for (String nodeName : nodeNames) {
				try {
					GroupNode groupNode = file.getGroup("/entry1/" + nodeName, false);
					Attribute attribute = groupNode.getAttribute(NexusFile.NXCLASS);
					String attributeVal = ((StringDataset) attribute.getValue()).get();
					logger.debug("Group = {}, NX_class = ", nodeName, attributeVal);
					if (NexusExtractor.NXDataClassName.equals(attributeVal)) {
						logger.debug("Adding detector node : {}", nodeName);
						detectorNamesList.add(nodeName);
					}
				} catch (NexusException ne) {
					logger.debug("Unable to get Nexus type for {} : {}", nodeName, ne.getMessage());
				}
			}
		}
		return detectorNamesList;
	}

	/**
	 * Load dataset from file; in case of exception, warning is sent to log panel and null reference is returned.
	 * @param file
	 * @param path
	 * @return
	 */
	private IDataset getDatasetFromFile(NexusFile file, String path) {
		try {
			return file.getData(path).getDataset().getSlice((SliceND)null);
		} catch (DatasetException | NexusException e) {
			logger.warn("Problem reading dataset {} from file {} : {}", path, file.getFilePath(), e.getMessage());
			return null;
		}
	}

	/**
	 * Returns a map of datasets in specified group that match specified shape
	 * @param file
	 * @param groupName
	 * @param expectedShape
	 * @return Map<path to datasete, ILazyDataset>
	 * @throws NexusException
	 * @throws DatasetException
	 */
	public Map<String, ILazyDataset> getDatasetsMatchingShape(NexusFile file, String groupName, int[] expectedShape ) throws NexusException, DatasetException {
		Map<String, ILazyDataset> datasetNames = new LinkedHashMap<>();

		// First attempt to get names for a group fails when group has link to MCA data (e.g. Xspress3).
		// Second attempt work though...
		try {
			file.getGroup(groupName, false).getNames();
		} catch(NexusException e) {
			logger.debug("possible problem getting dataset name for {} : {}.", groupName, e.getMessage());
		}
		try {
			List<DataNode> nodes = file.getGroup(groupName, false).getDataNodes();
			for(DataNode node : nodes) {
				ILazyDataset dataset = node.getDataset();
				if (ArrayUtils.isEquals(dataset.getShape(), expectedShape)) {
					String name = groupName + dataset.getName();
					datasetNames.put(name, dataset);
				}
			}
		}catch(NexusException ne) {
			logger.warn("Problem getting list of data for detector at {} : {}", groupName, ne.getMessage(), ne);
		}
		return datasetNames;
	}

	/**
	 * Return expected shape of 2d data.
	 * @param file
	 * @param bufScaler
	 * @return {numSpectra, numPointsPerSpectrum}
	 */
	private int[] getExpectedShape(NexusFile file, String bufScaler) {
		IDataset frameIndex = getDatasetFromFile(file, bufScaler+TurboXasNexusTree.FRAME_INDEX);
		IDataset motorParams = getDatasetFromFile(file, bufScaler+TurboXasNexusTree.MOTOR_PARAMS_COLUMN_NAME);
		if (frameIndex == null || motorParams == null) {
			logger.warn("Could not determine expecteded data shape using shapes of {} and {}", TurboXasNexusTree.FRAME_INDEX, TurboXasNexusTree.MOTOR_PARAMS_COLUMN_NAME);
			return null;
		}
		return new int[] {motorParams.getShape()[0], frameIndex.getShape()[0]};
	}

	/**
	 * Return new map of datasets; datasets with specified name are put into new map.
	 * @param datasetNames - full path of each dataset required
	 * @param allValidDatasets - all valid datasets (key=full path to dataset, value=dataset).
	 * @return
	 * @throws DatasetException
	 */
	private Map<String, IDataset> getValidDatasets(String[] datasetNames, Map<String, ILazyDataset> allValidDatasets) {
		Map<String, IDataset> datasets = new LinkedHashMap<>();
		for (String datasetName : datasetNames) {
			if (allValidDatasets.containsKey(datasetName)) {
				try {
					logger.info("Adding dataset {}", datasetName);
					IDataset dataset = allValidDatasets.get(datasetName).getSlice((SliceND) null);
					datasets.put(datasetName, dataset);
				} catch (DatasetException de) {
					logger.warn("Problem adding dataset {}. {}", datasetName, de.getMessage(), de);
				}
			} else {
				logger.warn("Not adding dataset {} - it does not match required shape", datasetName);
			}
		}
		return datasets;
	}

	public String createHeaderString() {
		String header = "";
		header += "# Ascii file created from TurboXas scan : "+nexusFilename+"\n";
		String date = new SimpleDateFormat("HH:mm:ss, EE FF MMMM, yyyy").format(new Date());
		header += "# Date : "+date+"\n#\n#\n";
		return header;
	}

	/**
	 * Create list of data in each column and column index. Position and energy are the first two columns,
	 * @param file NexusFile
	 * @param datasets - datasets to be listed
	 * @param stringBuilder
	 * @return
	 */
	public List<String> createColumnInfo(NexusFile file, Collection<String> datasetNames, StringBuilder stringBuilder) {
		String detectorEntry = "/entry1/"+detectorNames[0]+"/";

		IDataset spectrumIndex = getDatasetFromFile(file, detectorEntry+TurboXasNexusTree.SPECTRUM_INDEX);
		IDataset spectrumGroup = getDatasetFromFile(file, detectorEntry+TurboXasNexusTree.SPECTRUM_GROUP);

		int numSpectra = spectrumIndex.getShape()[0];

		// Make list of column names
		List<String> columnNames = new ArrayList<>();
		columnNames.add("#Index");
		columnNames.add(TurboXasNexusTree.POSITION_COLUMN_NAME);
		columnNames.add(TurboXasNexusTree.ENERGY_COLUMN_NAME);
		for(int i=0; i<numSpectra; i++) {
			for (String datasetName : datasetNames) {
				columnNames.add(String.format("%s_(%d,%d)", datasetName.replace("/entry1/",""), spectrumGroup.getInt(i), spectrumIndex.getInt(i)));
			}
		}

		// Print header list of column indices and dataset names
		stringBuilder.append("# Column index and name of dataset; dataset name appended with _(group number, spectrum number):\n");
		int columnNumber = 1;
		for(String columnName : columnNames) {
			stringBuilder.append(String.format("#\t%d : %s \n", columnNumber++, columnName));
		}
		stringBuilder.append("#"+System.lineSeparator());

		return columnNames;
	}

	/**
	 * Create main table of data.
	 * @return
	 * @throws Exception
	 */
	public String createDataString() throws Exception {
		try(NexusFile file = NexusFileHDF5.openNexusFileReadOnly(nexusFilename)) {

			if (detectorNames==null || detectorNames.length==0) {
				logger.warn("Names of detectors to read data from in Nexus file have not been set.\n"+
							"Try using setDetectorNames(\"scaler_for_zebra\", \"buffered_xspress3\"");

				return "# No detector names have been set.";
			}
			String detectorEntry = "/entry1/"+detectorNames[0]+"/";

			// Expected shape of the 2D data to be written
			int[] expectedShape = getExpectedShape(file, detectorEntry);

			// Make map of all 'valid' datasets available for each detector (i.e. datasets with shape matching expectedShape)
			// (key = full path to dataset, value = IDataset )
			Map<String, ILazyDataset> allDatasetsWithCorrectShape = new LinkedHashMap<>();
			for(String detectorName : detectorNames) {
				Map<String, ILazyDataset> datasetPaths = getDatasetsMatchingShape(file, "/entry1/"+detectorName+"/", expectedShape);
				allDatasetsWithCorrectShape.putAll(datasetPaths);
			}

			// If no dataset names have been set, add names of *all* valid datasets
			if (dataToRead.length == 0) {
				dataToRead = allDatasetsWithCorrectShape.keySet().toArray(new String[] {});
			}

			// Make map from specified dataset name to the dataset to be written to file
			Map<String, IDataset> datasets = getValidDatasets(dataToRead, allDatasetsWithCorrectShape);

			// String, number formats; fixed length format to try and keep things aligned in columns.
			final String numFormat = "%25.5e\t";
			final String intFormat = "%25d\t";
			final String strFormat = "%25s\t";

			// Print the list of column name and indices ...
			StringBuilder strBuilder = new StringBuilder();
			List<String> columnNames = createColumnInfo(file, datasets.keySet(), strBuilder);
			for(String columnName : columnNames) {
				strBuilder.append(String.format(strFormat, columnName));
			}
			strBuilder.append(System.lineSeparator());

			// Print the rows of column data ...
			IDataset positionDataset = getDatasetFromFile(file, detectorEntry+TurboXasNexusTree.POSITION_COLUMN_NAME);
			IDataset energyDataset = getDatasetFromFile(file, detectorEntry+TurboXasNexusTree.ENERGY_COLUMN_NAME);
			int numSpectra = expectedShape[0];
			int numReadouts = expectedShape[1];
			for(int i=0; i<numReadouts; i++) {

				// Build row of values of detector data, record if the row contains any NaNs
				boolean hasNaNs = false;
				StringBuilder spectraValues = new StringBuilder();
				for(int j=0; j<numSpectra; j++) {
					for(IDataset dataset : datasets.values()) {
						double value = dataset.getDouble(j, i);
						spectraValues.append(String.format(numFormat, value));
						if (Double.isNaN(value) ) {
							hasNaNs = true;
						}
					}
				}

				if (hasNaNs && ignoreNaNs) {
					logger.debug("Missing out row {} - contains NaNs", i);
					continue;
				}

				// energy position index, position, energy values
				strBuilder.append(String.format(intFormat, i));
				strBuilder.append(String.format(numFormat, positionDataset.getDouble(i)));
				strBuilder.append(String.format(numFormat, energyDataset.getDouble(i)));
				strBuilder.append(spectraValues);

				strBuilder.append(System.lineSeparator());
			}

			return strBuilder.toString();

		} catch (NexusException e) {
			logger.error("Problem reading from Nexus file {}", nexusFilename, e);
			throw new Exception(e);
		}
	}

	/**
	 * Generate Ascii output file based on currently set Nexus file using default name for Ascii file.
	 * @throws Exception
	 */
	public void writeAsciiFile() throws Exception {
		// Set the ascii filename based on Nexus file...
		if (StringUtils.isEmpty(asciiFilename)) {
			asciiFilename = FilenameUtils.getFullPath(nexusFilename) + FilenameUtils.getBaseName(nexusFilename)+"_ascii.dat";
		}
		writeAsciiFile(asciiFilename);
	}


	/**
	 * Generate Ascii output file based on currently set Nexus file.
	 * @param outputFile Name of output file for ascii data
	 * @throws Exception
	 */
	public void writeAsciiFile(String outputFile) throws Exception {
		File nexusFile = new File(nexusFilename);
		if (!nexusFile.exists()) {
			String message = String.format("Nexus file '%s' was not found - cannot generate ascii file!", nexusFilename);
			logger.warn(message);
			InterfaceProvider.getTerminalPrinter().print(message);
			return;
		}

		if (ArrayUtils.isEmpty(detectorNames)) {
			logger.info("No detector names have been set, attempting to set detector names automagically..");
			List<String> names = getDetectorNamesFromFile(nexusFilename);
			if (!names.isEmpty()) {
				detectorNames = names.toArray(new String[] {});
				logger.info("Setting detector names to {}", Arrays.toString(detectorNames));
			}
		}

		logger.info("Writing ascii file {} from data in {}", outputFile, nexusFilename);
		try(BufferedWriter bufWriter = new BufferedWriter(new FileWriter(outputFile))) {
			bufWriter.write(createHeaderString());
			bufWriter.write(createDataString());
			logger.info("Finished writing to {}", outputFile);
		}
	}

	public String getNexusFilename() {
		return nexusFilename;
	}

	public void setNexusFilename(String nexusFilename) {
		this.nexusFilename = nexusFilename;
	}

	public String[] getDetectorNames() {
		return detectorNames;
	}

	public void setDetectorNames(String[] detectorNames) {
		this.detectorNames = detectorNames;
	}

	public String[] getDataToRead() {
		return dataToRead;
	}

	public void setDataToRead(String[] dataToRead) {
		this.dataToRead = dataToRead;
	}

	public String getAsciiFilename() {
		return asciiFilename;
	}

	public void setAsciiFilename(String asciiFilename) {
		this.asciiFilename = asciiFilename;
	}

	public boolean isIgnoreNaNs() {
		return ignoreNaNs;
	}

	public void setIgnoreNaNs(boolean ignoreNaNs) {
		this.ignoreNaNs = ignoreNaNs;
	}
}
