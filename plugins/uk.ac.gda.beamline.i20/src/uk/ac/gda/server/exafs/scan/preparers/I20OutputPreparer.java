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

import gda.configuration.properties.LocalProperties;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.scan.ScanPlotSettings;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.apache.commons.lang.ArrayUtils;

import uk.ac.gda.beans.exafs.DetectorGroup;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.SignalParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.server.exafs.scan.Metadata;
import uk.ac.gda.server.exafs.scan.OutputPreparer;

public class I20OutputPreparer implements OutputPreparer {

	private AsciiDataWriterConfiguration datawriterconfig;
	private AsciiDataWriterConfiguration datawriterconfig_xes;
	private IScanParameters scanParameters;
	private IOutputParameters outputParameters;
	private TfgScalerWithFrames ionchambers;
	private Xspress2Detector xspress2system;
	private Xmap xmapMca;
	private Metadata meta;
	private IDetectorParameters detectorBean;
	private I20OutputParameters i20OutputParams;
	private I20DetectorPreparer detectorPreparer;

	public I20OutputPreparer(AsciiDataWriterConfiguration datawriterconfig,
			AsciiDataWriterConfiguration datawriterconfig_xes, TfgScalerWithFrames ionchambers,
			Xspress2Detector xspress2system, Xmap xmapMca, I20DetectorPreparer detectorPreparer) {
		this.datawriterconfig = datawriterconfig;
		this.datawriterconfig_xes = datawriterconfig_xes;
		this.ionchambers = ionchambers;
		this.xspress2system = xspress2system;
		this.xmapMca = xmapMca;
		this.detectorPreparer = detectorPreparer;

		resetNexusStaticMetadataList();
	}

	@Override
	public void configure(IOutputParameters outputParameters, IScanParameters scanBean, IDetectorParameters detectorBean)
			throws DeviceException {

		this.detectorBean = detectorBean;
		i20OutputParams = (I20OutputParameters) outputParameters;
		this.scanParameters = scanBean;
		// redefineNexusMetadata();
		ionchambers.setOutputLogValues(true);
		// # Custom for I20, which is why it is here instead of the shared DetectorConfiguration.java classes.
		// # Set the output options for the fluo detectors. Hope that this output preparer has been called AFTER the
		// # detector preparer or these settings will be overwritten.
		xspress2system.setOnlyDisplayFF(i20OutputParams.isXspressOnlyShowFF());
		xspress2system.setAddDTScalerValuesToAscii(i20OutputParams.isXspressShowDTRawValues());
		xspress2system.setSaveRawSpectrum(i20OutputParams.isXspressSaveRawSpectrum());
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
		return datawriterconfig;
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		resetNexusStaticMetadataList();
	}

	@Override
	public void resetNexusStaticMetadataList() {
		// This class talks directly to the shared metadata system, through the Finder.
		// Create a new objects whose defaults are based on the current scan type
		meta = new Metadata(getAsciiDataWriterConfig(this.scanParameters));
		
		// remove everything outside of this list
		meta.removeNexusMetadataList(getXasNexusMetadataList());
		meta.removeNexusMetadataList(getXesNexusMetadataList());
	}

	private List<String> getXasNexusMetadataList() {
		ArrayList<String> addListXas = new ArrayList<String>();
		addListXas.add("atn5_filter5_name");
		addListXas.add("atn5_filter5");
		addListXas.add("atn5_filter6_name");
		addListXas.add("atn5_filter6");
		addListXas.add("atn5_filter7_name");
		addListXas.add("atn5_filter7");
		addListXas.add("atn5_filter8_name");
		addListXas.add("atn5_filter8");
		addListXas.add("i0_stanford_offset_current");
		addListXas.add("i0_stanford_offset");
		addListXas.add("i0_stanford_offset_units");
		addListXas.add("i0_stanford_sensitivity");
		addListXas.add("i0_stanford_sensitivity_units");
		addListXas.add("iref_stanford_offset_current");
		addListXas.add("iref_stanford_offset");
		addListXas.add("iref_stanford_offset_units");
		addListXas.add("iref_stanford_sensitivity");
		addListXas.add("iref_stanford_sensitivity_units");
		addListXas.add("it_stanford_offset_current");
		addListXas.add("it_stanford_offset");
		addListXas.add("it_stanford_offset_units");
		addListXas.add("it_stanford_sensitivity");
		addListXas.add("it_stanford_sensitivity_units");
		return addListXas;
	}

	private List<String> getXesNexusMetadataList() {
		ArrayList<String> addListXas = new ArrayList<String>();
		addListXas.add("i1_stanford_offset_current");
		addListXas.add("i1_stanford_offset");
		addListXas.add("i1_stanford_offset_units");
		addListXas.add("i1_stanford_sensitivity");
		addListXas.add("i1_stanford_sensitivity_units");
		return addListXas;
	}

	// #
	// # For any specific plotting requirements based on all the options in this experiment
	// #
	@Override
	public ScanPlotSettings getPlotSettings() {
		if (detectorBean.getExperimentType().equals("Fluorescence")
				&& (detectorBean.getFluorescenceParameters().getDetectorType().equalsIgnoreCase("Germanium"))) {
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
			if (detGroup.getName().equals("Germanium")) {
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
			}
		}
		
		List<SignalParameters> extraColumns = outputParameters.getSignalList();
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