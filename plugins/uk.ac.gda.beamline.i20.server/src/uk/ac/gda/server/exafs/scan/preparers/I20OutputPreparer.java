/*-
 * Copyright © 2015 Diamond Light Source Ltd.
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
package uk.ac.gda.server.exafs.scan.preparers;

import java.util.HashMap;
import java.util.List;

import org.apache.commons.lang.ArrayUtils;

import gda.configuration.properties.LocalProperties;
import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.scan.ScanPlotSettings;
import uk.ac.gda.beans.exafs.DetectorGroup;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.SignalParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;

public class I20OutputPreparer extends OutputPreparerBase {

	private AsciiDataWriterConfiguration datawriterconfig_xes;
	private TfgScalerWithFrames ionchambers;
//	private Xspress2Detector xspress2system;
	private Xmap xmapMca;
	private IDetectorParameters detectorBean;
	private I20OutputParameters i20OutputParams;
	private I20DetectorPreparer detectorPreparer;
	private IScanParameters scanBean;

	public I20OutputPreparer(AsciiDataWriterConfiguration datawriterconfig,
			AsciiDataWriterConfiguration datawriterconfig_xes, NXMetaDataProvider metashop, TfgScalerWithFrames ionchambers,
			Xmap xmapMca, I20DetectorPreparer detectorPreparer) {
		super(datawriterconfig, metashop);
		this.datawriterconfig_xes = datawriterconfig_xes;
		this.ionchambers = ionchambers;
//		this.xspress2system = xspress2system;
		this.xmapMca = xmapMca;
		this.detectorPreparer = detectorPreparer;
	}

	@Override
	public void configure(IOutputParameters outputParameters, IScanParameters scanBean, IDetectorParameters detectorBean, ISampleParameters sampleParameters)
			throws DeviceException {
		super.configure(outputParameters, scanBean, detectorBean, sampleParameters);
		this.detectorBean = detectorBean;
		this.scanBean = scanBean;
		this.i20OutputParams = (I20OutputParameters) outputParameters;
		// redefineNexusMetadata();
		// # Custom for I20, which is why it is here instead of the shared DetectorConfiguration.java classes.
		// # Set the output options for the fluo detectors. Hope that this output preparer has been called AFTER the
		// # detector preparer or these settings will be overwritten.
//		xspress2system.setOnlyDisplayFF(i20OutputParams.isXspressOnlyShowFF());
//		xspress2system.setAddDTScalerValuesToAscii(i20OutputParams.isXspressShowDTRawValues());
//		xspress2system.setSaveRawSpectrum(i20OutputParams.isXspressSaveRawSpectrum());
		xmapMca.setSaveRawSpectrum(i20OutputParams.isVortexSaveRawSpectrum());
		// return []
	}

	// #
	// # Determines the AsciiDataWriterConfiguration to use to format the header/footer of the ascii data files
	// #
	// # If this returns None, then let the Ascii Data Writer class find the config for itself.
	// #
	@Override
	public AsciiDataWriterConfiguration getAsciiDataWriterConfig(IScanParameters scanParameters) {
		if (scanParameters instanceof XesScanParameters) {
			// # will return None if not found
			// print "Ascii (.dat) files will have XES format header."
			return datawriterconfig_xes;
		}
		// # will return None if not found
		// print "Ascii (.dat) files will have XAS format header."
		return getDatawriterconfig();
	}

	// #
	// # For any specific plotting requirements based on all the options in this experiment
	// #
	@Override
	public ScanPlotSettings getPlotSettings() {
		String expType = detectorBean.getExperimentType();
		if (expType.equals(DetectorParameters.XES_TYPE)) {
			String axisName = scanBean.getScannableName();
			if (axisName != null && axisName.contains("XES")) {
				ScanPlotSettings sps = new ScanPlotSettings();
				sps.setXAxisName("XESEnergy");
				return sps;
			}
		} else if (expType.equals(DetectorParameters.FLUORESCENCE_TYPE)
				&& (detectorBean.getFluorescenceParameters().getDetectorType().equalsIgnoreCase(FluorescenceParameters.GERMANIUM_DET_TYPE))) {
			if (i20OutputParams.isXspressShowDTRawValues() || !i20OutputParams.isXspressOnlyShowFF()) {
				// # create a filter for the DT columns and return it
				LocalProperties.set("gda.scan.useScanPlotSettings", "true");
				ScanPlotSettings sps = new ScanPlotSettings();
				sps.setXAxisName("Energy");// # column will have be converted to this name

				String[] axes = createAxesList();

				String[] visibleAxes = new String[0];
				String[] invisibleAxes = new String[0];
				for (String axis : axes) {
					if (axis.startsWith("Element")) {
						invisibleAxes = (String[]) ArrayUtils.add(invisibleAxes, axis);
					} else {
						visibleAxes = (String[]) ArrayUtils.add(visibleAxes, axis);
					}
				}
				sps.setYAxesShown(visibleAxes);
				sps.setYAxesNotShown(invisibleAxes);
				// # if anything extra, such as columns added in the output parameters xml should also be plotted
				sps.setUnlistedColumnBehaviour(ScanPlotSettings.IGNORE);
				return sps;
			}
		}
		return null;
	}

	protected String[] createAxesList() {

		DetectorGroup fluoDetGroup = null;
		List<DetectorGroup> listDetectorGroups = detectorBean.getDetectorGroups();
		for (DetectorGroup detGroup : listDetectorGroups) {
			if (detGroup.getName().equals(FluorescenceParameters.GERMANIUM_DET_TYPE)) {
				fluoDetGroup = detGroup;
				break;
			}
		}

		if (fluoDetGroup == null)
			// the XML is inconsistent
			return new String[]{};

		HashMap<String, Detector> detectorsMap = createDetectorsMap();

		String[] axes = new String[0];
		for (String detName : fluoDetGroup.getDetector()) {
			Detector thisDet = detectorsMap.get(detName);
			if (thisDet != null) {
				String[] extraNames = thisDet.getExtraNames();
				axes = (String[]) ArrayUtils.addAll(axes, extraNames);
				// Add 'input' names as well (i.e. 'Time' for ionchambers). imh 27/7/2017
				String[] inputNames = thisDet.getInputNames();
				if (inputNames!=null && inputNames.length>0) {
					axes = (String[]) ArrayUtils.addAll(axes, inputNames);
				}
			}
		}

		List<SignalParameters> extraColumns = i20OutputParams.getSignalList();
		for (SignalParameters column : extraColumns) {
			axes = (String[]) ArrayUtils.add(axes, column.getLabel());
		}

		return axes;
	}

	protected HashMap<String, Detector> createDetectorsMap() {
		HashMap<String, Detector> detectorsMap = new HashMap<String, Detector>();
		List<Detector> detectors = detectorPreparer.getDetectors();
		for (Detector det : detectors) {
			detectorsMap.put(det.getName(), det);
		}
		return detectorsMap;
	}
}
