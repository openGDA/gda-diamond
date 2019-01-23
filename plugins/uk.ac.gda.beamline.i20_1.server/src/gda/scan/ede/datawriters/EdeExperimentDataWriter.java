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

import java.util.List;

import org.dawnsci.ede.EdeDataConstants;
import org.dawnsci.ede.EdeDataConstants.TimingGroupMetadata;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.data.scan.datawriter.AsciiMetadataConfig;
import gda.data.scan.datawriter.FindableAsciiDataWriterConfiguration;
import gda.device.detector.EdeDetector;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public abstract class EdeExperimentDataWriter {

	private static final Logger logger = LoggerFactory.getLogger(EdeExperimentDataWriter.class);

	protected String filenameTemplate = "";
	protected EdeDetector theDetector;
	private String sampleDetails;

	protected final DoubleDataset energyDataSet;

	public abstract String getAsciiFilename();

	public EdeExperimentDataWriter(DoubleDataset energyDataSet) {
		this.energyDataSet = energyDataSet;
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
			double realTimePerSpectrum = (group.getTimePerScan() + accumulationReadoutTime)*group.getNumberOfScansPerFrame();
			metaData[i] = new TimingGroupMetadata(i, group.getNumberOfFrames(), group.getTimePerScan(),
					realTimePerSpectrum, group.getPreceedingTimeDelay(), group.getNumberOfScansPerFrame());
		}
		return metaData;
	}

	// FIXME
	protected String getScannablesConfiguration() {
		List<Findable> configs = Finder.getInstance().listAllObjects(FindableAsciiDataWriterConfiguration.class.getSimpleName());
		if (configs == null) {
			return "";
		}
		StringBuilder configBuilder = new StringBuilder();
		try {
			if (!configs.isEmpty()) {
				// Adding scannables
				AsciiDataWriterConfiguration config = (AsciiDataWriterConfiguration) configs.get(0);
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
}
