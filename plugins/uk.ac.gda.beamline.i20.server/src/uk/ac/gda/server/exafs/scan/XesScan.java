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

package uk.ac.gda.server.exafs.scan;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;

import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.Scannable;
import gda.device.detector.NXDetector;
import gda.device.detector.nxdetector.plugin.areadetector.ADRoiCountsI0;
import gda.device.scannable.TwoDScanPlotter;
import gda.device.scannable.XESEnergyScannable;
import gda.exafs.xes.IXesOffsets;
import gda.factory.Finder;
import gda.jython.scriptcontroller.logging.LoggingScriptController;
import uk.ac.gda.beans.exafs.IDetectorConfigurationParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.ScanColourType;
import uk.ac.gda.beans.exafs.SignalParameters;
import uk.ac.gda.beans.exafs.SpectrometerScanParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.server.exafs.scan.preparers.I20DetectorPreparer;
import uk.ac.gda.server.exafs.scan.preparers.I20OutputPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class XesScan extends XasScanBase implements XasScan {

	private static Logger logger = LoggerFactory.getLogger(XesScan.class);


	private Scannable mono_energy;
	private EnergyScan xas;
	private XesScanParameters xesScanParameters;
	private TwoDScanPlotter twodplotter = new TwoDScanPlotter();
	private I20OutputParameters i20OutputParameters;
	private String monoAxisLabel = "bragg1 energy [eV]";
	private String xesAxisLabel = "XESEnergy [eV]";
	private List<IXesOffsets> xesOffsetsList;

	// Scannable that move XESBraggUpper and XESBraggLower to the same position
	private Scannable analyserAngleBoth;

	// Scannable that moves XESEnergyUpper and XESEnergyLower to the same position
	private Scannable xesEnergyBoth;

	@Override
	public String getScanType() {
		return "XES";
	}

	@Override
	public void configureCollection(ISampleParameters sampleBean, IScanParameters scanBean, IDetectorParameters detectorBean,
			IOutputParameters outputBean, IDetectorConfigurationParameters detectorConfigurationBean,
			String experimentFullPath, int numRepetitions) throws Exception {

		xesScanParameters = (XesScanParameters) scanBean;
		i20OutputParameters = (I20OutputParameters) outputBean;
		this.numRepetitions = numRepetitions;
		this.experimentFullPath = experimentFullPath;
		this.detectorConfigurationBean = detectorConfigurationBean;
		this.outputBean = outputBean;
		this.detectorBean = detectorBean;
		this.sampleBean = sampleBean;
		this.scanBean = scanBean;

		setXmlFileNames("", "", "", "", "");
		determineExperimentPath(experimentFullPath);
		scan_unique_id = LoggingScriptController.createUniqueID(getScanType());
	}

	Map<IXesOffsets, String> appliedOffsets = Collections.emptyMap();

	@Override
	public void doCollection() throws Exception {
		xesScanParameters = (XesScanParameters) scanBean;
		i20OutputParameters = (I20OutputParameters) outputBean;

		// Generate default spectrometer settings list if not present
		if (!xesScanParameters.hasSpectrometerList()) {
			xesScanParameters.generateSpectrometerList();
			xesScanParameters.getSpectrometerParamsForRow(0).setScannableName("XESEnergyUpper");
			xesScanParameters.getSpectrometerParamsForRow(1).setScannableName("XESEnergyLower");
		}

		applyOffsets();

		if (analyserAngleBoth.isBusy()) {
			analyserAngleBoth.waitWhileBusy();
		}

		// Set XES mode on detector preparer so appropriate setup can be done
		// for ionchambers/I1
		if (xas.getDetectorPreparer() instanceof I20DetectorPreparer detPreparer) {
			detPreparer.setXesMode(true);
		}

		int innerScanType = xesScanParameters.getScanType();
		if (innerScanType == XesScanParameters.FIXED_XES_SCAN_XAS ||
			innerScanType == XesScanParameters.FIXED_XES_SCAN_XANES ||
			innerScanType == XesScanParameters.SCAN_XES_REGION_FIXED_MONO) {
			doXASScan();
			return;
		}

		try {
			super.doCollection();
		} finally {
			// make sure the plotter is switched off
			twodplotter.atScanEnd();
		}
	}

	private void applyOffsets() throws IOException {
		appliedOffsets = new HashMap<>();
		// Set the offsets for each row of the spectrometer
		for(var entry : xesScanParameters.getActiveSpectrometerParameters().entrySet() ) {
			SpectrometerScanParameters specParams = entry.getValue();
			String scnName = xesScanParameters.getSpectrometerScannableForRow(entry.getKey());

			// Name of the offset store
			String offsetStoreName = specParams.getOffsetsStoreName();
			if (StringUtils.isEmpty(offsetStoreName)) {
				logger.info("Not setting offsets for {} - no offset file has been set", scnName);
				continue;
			}

			// get the XesOffset object to use with the XESEnergy scannable
			Optional<IXesOffsets> xesOffsets = xesOffsetsList
					.stream()
					.filter(offset -> offset.getXesEnergyScannableName().equals(scnName))
					.findFirst();

			if (xesOffsets.isPresent()) {
				logger.info("Setting offsets on {}", scnName);
				xesOffsets.get().saveToTemp(); // save current offsets to temporary files, so they can be reset at the end
				xesOffsets.get().apply(offsetStoreName);
				appliedOffsets.put(xesOffsets.get(), offsetStoreName);
			} else {
				throw new IllegalArgumentException("Could not find XesOffsets object required to set offsets for "+scnName);
			}
		}
	}
	@Override
	protected void finishRepetitions() throws Exception {
		super.finishRepetitions();

		// Apply the original XES offsets
		if (!appliedOffsets.isEmpty()) {
			for(var offsets : appliedOffsets.keySet()) {
				logger.info("Restoring original offset values on {}", offsets.getXesEnergyScannableName());
				offsets.applyFromTemp();
			}
		}
		appliedOffsets.clear();

	}

	private XESEnergyScannable getEnergyScannable(String scannableName) {
		Optional<XESEnergyScannable> scn = Finder.findOptionalOfType(scannableName, XESEnergyScannable.class);
		if (scn.isPresent()) {
			return scn.get();
		}
		throw new IllegalArgumentException("Could not find XESEnergy object "+scannableName+" required to run XES scan");
	}

	private SpectrometerScanParameters getSpectrometerScanParams(XesScanParameters scanParams) {
		if (scanParams.getScanColourType() == ScanColourType.TWO_COLOUR) {
			throw new IllegalArgumentException("Two colour scans are not not supported");
		}
		return scanParams.getActiveSpectrometerParameters().values().iterator().next();
	}

	private Scannable getXesEnergyScannable(XesScanParameters scanParams) throws Exception {
		if (scanParams.getScanColourType() == ScanColourType.ONE_COLOUR) {
			return xesEnergyBoth;
		}
		return getEnergyScannable(getSpectrometerScanParams(scanParams).getScannableName());
	}

	private Scannable getXesAngleScannable(Scannable s) {
		if (s instanceof XESEnergyScannable xesScn) {
			return xesScn.getXes();
		}
		return analyserAngleBoth;
	}

	// args do run a single concurrentscan
	@Override
	public Object[] createScanArguments(String sampleName, List<String> descriptions) throws Exception {

		int innerScanType = xesScanParameters.getScanType();

		if (xesScanParameters.getScanColourType() == ScanColourType.TWO_COLOUR) {
			throw new IllegalArgumentException("Two colour mode is not supported for 2-dimensional XES scans");
		}

		// This will change depending on colour type (1 colour, 1 colour row1, 1 colour row2)
		SpectrometerScanParameters specParameters = getSpectrometerScanParams(xesScanParameters);
		Scannable xesEnergyScannable = getXesEnergyScannable(xesScanParameters);
		Scannable xesBraggScannable = getXesAngleScannable(xesEnergyScannable);

		Detector[] detList = getDetectors();

		List<Object> xesScanArguments = new ArrayList<>();

		if (innerScanType == XesScanParameters.SCAN_XES_FIXED_MONO) {
			List<Object> scanParams = Arrays.asList(xesEnergyScannable, specParameters.getInitialEnergy(),
					specParameters.getFinalEnergy(), specParameters.getStepSize(), mono_energy,
					xesScanParameters.getMonoEnergy(), xesBraggScannable);
			xesScanArguments.addAll(scanParams);
			setXesEnergyAxisName(xesEnergyScannable);
		} else if (innerScanType == XesScanParameters.SCAN_XES_SCAN_MONO) {

			List<Object> spectrometerScanParams = Arrays.asList(xesEnergyScannable, specParameters.getInitialEnergy(),
					specParameters.getFinalEnergy(), specParameters.getStepSize());

			List<Object> monoScanParams = Arrays.asList(mono_energy, xesScanParameters.getMonoInitialEnergy(),
					xesScanParameters.getMonoFinalEnergy(), xesScanParameters.getMonoStepSize());

			if (xesScanParameters.getLoopChoice().equals(XesScanParameters.EF_OUTER_MONO_INNER)) {
				xesScanArguments.addAll(spectrometerScanParams);
				xesScanArguments.addAll(monoScanParams);
				twodplotter.setXArgs(xesScanParameters.getMonoInitialEnergy(), xesScanParameters.getMonoFinalEnergy(),
						xesScanParameters.getMonoStepSize());
				twodplotter.setYArgs(specParameters.getInitialEnergy(), specParameters.getFinalEnergy(),
						specParameters.getStepSize());
				twodplotter.setXAxisName(monoAxisLabel);
				twodplotter.setYAxisName(xesEnergyScannable.getName()+" [eV]");
				setXesEnergyAxisName(mono_energy);
			} else {
				xesScanArguments.addAll(monoScanParams);
				xesScanArguments.addAll(spectrometerScanParams);
				twodplotter.setXArgs(specParameters.getInitialEnergy(), specParameters.getFinalEnergy(),
						specParameters.getStepSize());
				twodplotter.setYArgs(xesScanParameters.getMonoInitialEnergy(), xesScanParameters.getMonoFinalEnergy(),
						xesScanParameters.getMonoStepSize());
				twodplotter.setXAxisName(xesEnergyScannable.getName()+" [eV]");
				twodplotter.setYAxisName(monoAxisLabel);
				setXesEnergyAxisName(xesEnergyScannable);
			}
			// Add XESBragg angle
			xesScanArguments.add(xesBraggScannable);

			// Try to set the name of the z axis quantity automatically
			// (the stream name from the ADROiCountsI0 plugin on the medipix detector)
			Optional<String> ffName = Stream.of(detList)
					.map(this::getFFI1Name)
					.filter(Optional::isPresent)
					.findFirst()
					.orElse(Optional.empty());

			if (ffName.isPresent()) {
				logger.debug("Setting name of Z axis to : {}", ffName.get());
				twodplotter.setZ_colName(ffName.get());
			} else {
				twodplotter.setZ_colName("FFI1");
			}
			xesScanArguments.add(twodplotter);
		}

		xesScanArguments.addAll(Arrays.asList(detList));

		return xesScanArguments.toArray();
	}

	/**
	 * Name of the x-axis in the scan plot
	 * (i.e. name of object being scanned for the particular scan type)
	 * @param name
	 */
	private void setXesEnergyAxisName(Scannable scannable) {
		if (getOutputPreparer() instanceof I20OutputPreparer prep) {
			if (scannable == xesEnergyBoth) {
				prep.setXesEnergyAxisName(scannable.getExtraNames()[0]);
			} else {
				prep.setXesEnergyAxisName(scannable.getName());
			}
		}
	}

	public Optional<String> getFFI1Name(Detector detector) {
		if (detector instanceof NXDetector nxDetector) {
			return nxDetector.getAdditionalPluginList()
					.stream()
					.filter(ADRoiCountsI0.class::isInstance)
					.map(ADRoiCountsI0.class::cast)
					.map(ADRoiCountsI0::getStreamName)
					.findFirst();
		}
		return Optional.empty();
	}

	/**
	 * Set name of scannable in scan bean to match the one to be moved (not essential, but useful to have it recorded in XML)
	 * @param scanParams
	 * @param nameOfScannableToMove
	 */
	private void setXasXanesScannable(IScanParameters scanParams, String nameOfScannableToMove) {
		logger.info("Updating name of scannable in Xas/Xanes/Region parameter file to {}", nameOfScannableToMove);

		if (scanParams instanceof XasScanParameters xasScanParams) {
			xasScanParams.setScannableName(nameOfScannableToMove);
		} else if (scanParams instanceof XanesScanParameters xanesScanParams) {
			xanesScanParams.setScannableName(nameOfScannableToMove);
		}
	}

	/**
	 * Do Xas or Xanes scan moving either the mono or Xes energy scannable.
	 * The non scanning energy scannable stays fixed for the duration of the scan.
	 * @throws Exception
	 */
	private void doXASScan() throws Exception {

		Scannable movingScannable;
		String xasRegionFileName = "";


		List<SignalParameters> extraOutputs = new ArrayList<>();

		Scannable xesEnergyScannable;

		logger.info("Starting Xas/Xanes scan");

		// Set the scannable to be moved during scan, and non
		if (xesScanParameters.getScanType() == XesScanParameters.SCAN_XES_REGION_FIXED_MONO) {
			// TWO_COLOUR is not allowed for this type of scan!

			SpectrometerScanParameters specParams = getSpectrometerScanParams(xesScanParameters);
			xesEnergyScannable = getXesEnergyScannable(xesScanParameters);

			// Add the XES energy and Bragg angle as extra outputs
			if (xesScanParameters.getScanColourType() == ScanColourType.ONE_COLOUR) {
				for(var p : xesScanParameters.getSpectrometerScanParameters()) {
					var energyScannable = getEnergyScannable(p.getScannableName());
					extraOutputs.add(createSignal(energyScannable.getName()));
					extraOutputs.add(createSignal(energyScannable.getXes().getName()));
				}
			} else {
				extraOutputs.add(createSignal(xesEnergyScannable));
				extraOutputs.add(createSignal(getXesAngleScannable(xesEnergyScannable)));
			}

			xasRegionFileName = specParams.getScanFileName();

			// Scan XES using XANES parameters, fixed mono
			movingScannable = xesEnergyScannable;

			Scannable fixedScannable = mono_energy;
			double fixedEnergy = xesScanParameters.getMonoEnergy();

			logger.info("Moving {} to initial position {} eV", fixedScannable.getName(), fixedEnergy);
			fixedScannable.waitWhileBusy();
			fixedScannable.moveTo(fixedEnergy);

			// Add the mono energy as extra outputs
			extraOutputs.add(createSignal(fixedScannable));
		} else {
			// TWO_COLOUR is ok here

			// Scan mono using Xanes/Xas parameters, fixed XES
			movingScannable = mono_energy;
			xasRegionFileName = xesScanParameters.getScanFileName();

			// Move the spectrometer rows to the intitial position(s)
			Map<Integer, SpectrometerScanParameters> activeSpecParams = xesScanParameters.getActiveSpectrometerParameters();
			for(var params : activeSpecParams.entrySet()) {
				String scnName = xesScanParameters.getSpectrometerScannableForRow(params.getKey());
				double pos = params.getValue().getFixedEnergy();

				Scannable energyScannable = getEnergyScannable(scnName);
				logger.info("Moving {} to initial position {}", scnName, pos);
				getEnergyScannable(scnName).moveTo(pos);

				// Add the XES energy and bragg angle as extra outputs
				extraOutputs.add(createSignal(energyScannable));
				extraOutputs.add(createSignal(getXesAngleScannable(energyScannable)));
			}
		}

		extraOutputs.forEach(i20OutputParameters::addSignal);

		IScanParameters xasScanParams = (IScanParameters) XMLHelpers.getBeanObject(experimentFullPath + "/", xasRegionFileName);

		logger.info("Scan parameters loaded from {}", xasRegionFileName);
		setXasXanesScannable(xasScanParams, movingScannable.getName());

		// Set the name of the x-axis to be used for the scan plot
		setXesEnergyAxisName(movingScannable);

		// Set scannable object to be moved during scan
		xas.setEnergyScannable(movingScannable);

		xas.configureCollection(sampleBean, xasScanParams, detectorBean, outputBean, detectorConfigurationBean,
				experimentFullPath, numRepetitions);

		// Set the names of the XML bean files so they get written to the 'before_scan' meta data.
		String[] filenames = getXmlFileNames();
		xas.setXmlFileNames(filenames[0], xasRegionFileName, filenames[2], filenames[3], filenames[4]);

		xas.doCollection();
	}

	private SignalParameters createSignal(Scannable scn) {
		return new SignalParameters(scn.getName(), scn.getName(), 2, scn.getName(), scn.getName());
	}

	private SignalParameters createSignal(String name) {
		return new SignalParameters(name, name, 2, name, name);
	}
	public Scannable getAnalyserAngleBoth() {
		return analyserAngleBoth;
	}

	public void setXesBraggBoth(Scannable analyserAngleBoth) {
		this.analyserAngleBoth = analyserAngleBoth;
	}

	public Scannable getXesEnergyBoth() {
		return xesEnergyBoth;
	}

	public void setXesEnergyBoth(Scannable xesEnergyBoth) {
		this.xesEnergyBoth = xesEnergyBoth;
	}

	public Scannable getMono_energy() {
		return mono_energy;
	}

	public void setMono_energy(Scannable mono_energy) {
		this.mono_energy = mono_energy;
	}

	public XasScan getXas() {
		return xas;
	}

	public void setXas(EnergyScan xas) {
		this.xas = xas;
	}

	public List<IXesOffsets> getXesOffsets() {
		return xesOffsetsList;
	}

	public void setXesOffsetsList(List<IXesOffsets> xesOffsetsList) {
		this.xesOffsetsList = xesOffsetsList;
	}

	public TwoDScanPlotter getTwoDPlotter() {
		return twodplotter;
	}

	public void setTwoDPlotter(TwoDScanPlotter twodplotter) {
		this.twodplotter = twodplotter;
	}
}
