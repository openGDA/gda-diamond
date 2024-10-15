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
import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.scan.ScanPlotSettings;
import uk.ac.gda.beans.exafs.DetectorGroup;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.SignalParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;

public class I20OutputPreparer extends OutputPreparerBase {

	private static final Logger logger = LoggerFactory.getLogger(I20OutputPreparer.class);


	private AsciiDataWriterConfiguration datawriterconfig_xes;
	private Xmap xmap;
	private IDetectorParameters detectorBean;
	private I20OutputParameters i20OutputParams;
	private I20DetectorPreparer detectorPreparer;
	private IScanParameters scanBean;

	private String xesEnergyAxisName ="";

	public I20OutputPreparer(AsciiDataWriterConfiguration datawriterconfig,
			AsciiDataWriterConfiguration datawriterconfig_xes, NXMetaDataProvider metashop, TfgScalerWithFrames ionchambers,
			I20DetectorPreparer detectorPreparer) {
		super(datawriterconfig, metashop);
		this.datawriterconfig_xes = datawriterconfig_xes;
		this.detectorPreparer = detectorPreparer;
	}

	@Override
	public void configure(IOutputParameters outputParameters, IScanParameters scanBean, IDetectorParameters detectorBean, ISampleParameters sampleParameters)
			throws DeviceException {
		super.configure(outputParameters, scanBean, detectorBean, sampleParameters);
		this.detectorBean = detectorBean;
		this.scanBean = scanBean;
		this.i20OutputParams = (I20OutputParameters) outputParameters;
		if (xmap != null) {
			xmap.setSaveRawSpectrum(i20OutputParams.isVortexSaveRawSpectrum());
		}
	}

	@Override
	public AsciiDataWriterConfiguration getAsciiDataWriterConfig(IScanParameters scanParameters) {
		if (scanParameters instanceof XesScanParameters || detectorPreparer.isXesMode()) {
			return datawriterconfig_xes;
		}
		return getDatawriterconfig();
	}

	@Override
	public ScanPlotSettings getPlotSettings() {
		if (detectorPreparer.isXesMode()) {

			if (StringUtils.isEmpty(xesEnergyAxisName)) {
				logger.warn("XES energy axis name has not been set");
				return null;
			}

			ScanPlotSettings sps = new ScanPlotSettings();
			sps.setXAxisName(xesEnergyAxisName);
			return sps;

		} else if (scanBean instanceof XasScanParameters || scanBean instanceof XanesScanParameters) {

			if (detectorBean.getFluorescenceParameters() == null ||
				!detectorBean.getFluorescenceParameters().getDetectorType().equalsIgnoreCase(FluorescenceParameters.GERMANIUM_DET_TYPE)) {
				return null;
			}

			if (i20OutputParams.isXspressShowDTRawValues() || !i20OutputParams.isXspressOnlyShowFF()) {
				// Create a filter for the DT columns and return it
				LocalProperties.set("gda.scan.useScanPlotSettings", "true");

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

				ScanPlotSettings sps = new ScanPlotSettings();
				sps.setYAxesShown(visibleAxes);
				sps.setYAxesNotShown(invisibleAxes);
				// if anything extra, such as columns added in the output parameters xml should also be plotted
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

		if (fluoDetGroup == null) {
			// the XML is inconsistent
			return new String[]{};
		}

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

	public void setXesEnergyAxisName(String axisName) {
		this.xesEnergyAxisName = axisName;
	}

	public void setXMap(Xmap xmapMca) {
		this.xmap = xmapMca;
	}
}
