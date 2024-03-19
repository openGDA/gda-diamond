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
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;

import org.apache.commons.lang.StringUtils;
import org.python.core.PyTuple;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.Scannable;
import gda.device.detector.NXDetector;
import gda.device.detector.nxdetector.plugin.areadetector.ADRoiCountsI0;
import gda.device.scannable.TwoDScanPlotter;
import gda.device.scannable.XESEnergyScannable;
import gda.device.scannable.XasScannable;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.exafs.xes.IXesOffsets;
import gda.factory.Finder;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.ScanColourType;
import uk.ac.gda.beans.exafs.SpectrometerScanParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.server.exafs.scan.preparers.I20OutputPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class XesScan extends XasScanBase implements XasScan {

	private static final Logger logger = LoggerFactory.getLogger(XesScan.class);

	private Scannable mono_energy;
	private EnergyScan xas;
	private XesScanParameters xesScanParameters;
	private TwoDScanPlotter twodplotter = new TwoDScanPlotter();
	private String monoAxisLabel = "bragg1 energy [eV]";
	private List<IXesOffsets> xesOffsetsList;

	private Map<Scannable, Scannable> energyTransferScannables = new HashMap<>();
	private boolean scanEnergyTransfer;

	// Scannable group containing XESBraggUpper and XESBraggLower
	private Scannable xesBraggGroup;

	// Scannable group containing XESEnergyUpper and XESEnergyLower
	private Scannable xesEnergyGroup;

	// Scannable that moves XESEnergyUpper and XESEnergyLower to the same position
	private Scannable xesEnergyBoth;

	private Map<IXesOffsets, String> appliedOffsets = Collections.emptyMap();

	@Override
	public String getScanType() {
		return "XES";
	}

	@Override
	public void doCollection() throws Exception {
		xesScanParameters = (XesScanParameters) scanBean;

		// Generate default spectrometer settings list if not present
		if (!xesScanParameters.hasSpectrometerList()) {
			xesScanParameters.generateSpectrometerList();
			var params = xesScanParameters.getSpectrometerScanParameters();
			params.get(0).setScannableName("XESEnergyUpper");
			params.get(1).setScannableName("XESEnergyLower");
			xesScanParameters.setScanColourType(ScanColourType.ONE_COLOUR);
		}

		applyOffsets();

		if (xesBraggGroup.isBusy()) {
			xesBraggGroup.waitWhileBusy();
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
		for(int i=0; i<xesScanParameters.getSpectrometerScanParameters().size(); i++) {

			SpectrometerScanParameters specParams = xesScanParameters.getSpectrometerScanParameters().get(i);
			boolean useRow = xesScanParameters.getScanColourType() != null ? xesScanParameters.getScanColourType().useRow(i) : true;

			if (!useRow) {
				logger.info("Not applying offets to {} - it is not being used for the scan", specParams.getScannableName());
				continue;
			}

			String scnName = specParams.getScannableName();
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

	@Override
	public Object[] createScanArguments(String sampleName, List<String> descriptions) throws Exception {
		if (xesScanParameters.scanUsesXasXanesFile()) {
			return createScanArgumentsXasXanes();
		} else {
			return createScanArgumentsStepScan();
		}
	}

	/**
	 * Create scan arguments for 'scan xes, fixed mono' and 'scan xes, scan mono' step scans.
	 *
	 * @param sampleName
	 * @param descriptions
	 * @return
	 * @throws Exception
	 */
	private Object[] createScanArgumentsStepScan() throws Exception {

		SpectrometerScanParameters specParameters = xesScanParameters.getPrimarySpectrometerScanParams();
		SpectrometerScanParameters secondaryParams = xesScanParameters.getSecondarySpectrometerScanParams();

		Scannable xesEnergyScannable = getXesEnergyScannable(xesScanParameters);
		Scannable xesBraggScannable = getXesAngleScannable(xesEnergyScannable);

		Scannable spectrometerScanAxis;
		if (scanEnergyTransfer) {
			spectrometerScanAxis = getEnergyTransferScannable(xesEnergyScannable);
		} else {
			spectrometerScanAxis = xesEnergyScannable;
		}

		// Setup position provider that returns either single energy or two energy values
		// for each point in the scan
		XesScanPositionProvider positionProvider = new XesScanPositionProvider();
		positionProvider.createPrimaryPoints(specParameters.getInitialEnergy(), specParameters.getFinalEnergy(), specParameters.getStepSize());
		if (xesScanParameters.getScanColourType() == ScanColourType.ONE_COLOUR) {
			// One colour : second secondary points match the primary ones
			positionProvider.createSecondaryPoints(specParameters.getInitialEnergy(), specParameters.getStepSize());
		} else if (secondaryParams != null) {
			// Two colour : Secondary points set from secondary params
			positionProvider.createSecondaryPoints(secondaryParams.getInitialEnergy(), secondaryParams.getStepSize());
		}

		List<Object> xesScanArguments = new ArrayList<>();
		Detector[] detList = getDetectors();
		detList = getOrderedDetectors(detList);

		int innerScanType = xesScanParameters.getScanType();

		if (innerScanType == XesScanParameters.SCAN_XES_FIXED_MONO) {
			List<Object> scanParams = Arrays.asList(spectrometerScanAxis, positionProvider, mono_energy,
					xesScanParameters.getMonoEnergy(), xesBraggScannable);
			xesScanArguments.addAll(scanParams);
			if (scanEnergyTransfer) {
				xesScanArguments.add(xesEnergyScannable);
			}
			setXesEnergyAxisName(spectrometerScanAxis);
		} else if (innerScanType == XesScanParameters.SCAN_XES_SCAN_MONO) {

			List<Object> spectrometerScanParams = Arrays.asList(spectrometerScanAxis, positionProvider);

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
				twodplotter.setYAxisName(spectrometerScanAxis.getName()+" [eV]");
				setXesEnergyAxisName(mono_energy);
			} else {
				xesScanArguments.addAll(monoScanParams);
				xesScanArguments.addAll(spectrometerScanParams);
				twodplotter.setXArgs(specParameters.getInitialEnergy(), specParameters.getFinalEnergy(),
						specParameters.getStepSize());
				twodplotter.setYArgs(xesScanParameters.getMonoInitialEnergy(), xesScanParameters.getMonoFinalEnergy(),
						xesScanParameters.getMonoStepSize());
				twodplotter.setXAxisName(spectrometerScanAxis.getName()+" [eV]");
				twodplotter.setYAxisName(monoAxisLabel);
				setXesEnergyAxisName(spectrometerScanAxis);
			}
			// Add XESBragg angle
			xesScanArguments.add(xesBraggScannable);

			// add the spectrometer energy if doing scanning energy transfer
			if (scanEnergyTransfer) {
				xesScanArguments.add(xesEnergyScannable);
			}

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
			if (scannable.getExtraNames().length > 0) {
				prep.setXesEnergyAxisName(scannable.getExtraNames()[0]);
			} else {
				prep.setXesEnergyAxisName(scannable.getInputNames()[0]);
			}
		}
	}

	private Optional<String> getFFI1Name(Detector detector) {
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
	 * Create scan arguements for Xas or Xanes scan moving either the mono or Xes energy scannable.

	 * @throws Exception
	 */
	private Object[] createScanArgumentsXasXanes() throws Exception {

		logger.info("Creating parameters for XES scan using Xas/Xanes parameter file");

		Scannable movingScannable;
		Map<Scannable, Object> fixedScannablePositions = new LinkedHashMap<>();
		List<Scannable> extraOutputs = new ArrayList<>();

		// Set the scannable to be moved during scan, and non
		if (xesScanParameters.getScanType() == XesScanParameters.SCAN_XES_REGION_FIXED_MONO) {
			// TWO_COLOUR is not allowed for this type of scan!

			Scannable xesEnergyScannable = getXesEnergyScannable(xesScanParameters);
			if (xesScanParameters.getScanColourType() == ScanColourType.ONE_COLOUR) {
				xesEnergyScannable = xesEnergyBoth;
			}
			// Add the XES energy and Bragg angle as extra outputs
			if (xesScanParameters.getScanColourType() == ScanColourType.ONE_COLOUR) {
				for(var p : xesScanParameters.getSpectrometerScanParameters()) {
					var energyScannable = getEnergyScannable(p.getScannableName());
					extraOutputs.add(energyScannable);
					extraOutputs.add(energyScannable.getXes());
				}
			} else {
				extraOutputs.add(xesEnergyScannable);
				extraOutputs.add(getXesAngleScannable(xesEnergyScannable));
			}

			// Scan XES using XANES parameters, fixed mono
			movingScannable = xesEnergyScannable;

			logger.debug("Initial {} position : {} eV", mono_energy.getName(), xesScanParameters.getMonoEnergy());
			fixedScannablePositions.put(mono_energy, xesScanParameters.getMonoEnergy());

		} else {
			// TWO_COLOUR is ok here

			// Scan mono using Xanes/Xas parameters, fixed XES
			movingScannable = mono_energy;

			// Store the spectrometer row fixed position(s)
			for(var params : xesScanParameters.getActiveSpectrometerParameters().entrySet()) {
				var specParams = xesScanParameters.getSpectrometerScanParameters();
				int rowNum = params.getKey();
				if (rowNum >= specParams.size()) {
					logger.warn("Cannot move energy of spectrometer row {}. XesScanParameters only has settings for {} rows", rowNum+1, specParams.size());
					continue;
				}
				String scnName = xesScanParameters.getScannableNameForRow(params.getKey());
				double pos = params.getValue().getFixedEnergy();

				Scannable energyScannable = getEnergyScannable(scnName);
				logger.debug("Intitial {} position : {} eV", scnName, pos);

				fixedScannablePositions.put(energyScannable, pos);

				// Add the bragg angle as extra outputs
				extraOutputs.add(getXesAngleScannable(energyScannable));
			}
		}

		setXesEnergyAxisName(movingScannable);

		// Load the Xas/Xanes parameters bean from disk
		String xasRegionFileName = xesScanParameters.getXasXanesFileName();
		logger.info("Scan parameters loaded from {}", xasRegionFileName);
		IScanParameters xasScanParams = (IScanParameters) XMLHelpers.getBean(Paths.get(experimentFullPath).resolve(xasRegionFileName).toFile());

		// Get the detector objectrs to be used (in the correct order).
		Detector[] detList = getDetectors();
		detList = getOrderedDetectors(detList);

		// Create new XasScannable, to move the energy axis and set the detector collection time.
		XasScannable xasScannable = new XasScannable();
		xasScannable.setName("xas_scannable");
		xasScannable.setEnergyScannable(movingScannable);
		xasScannable.setDetectors(detList);

		// Assemble the scan argument list :
		List<Object> argList = new ArrayList<>();

		// XAS scannable and the list of (energy, time) values
		argList.add(xasScannable);
		argList.add(getEnergiesFromScanBean(xasScanParams));

		// Scannables at fixed position for the scan
		fixedScannablePositions.entrySet().stream().forEach(entry -> {
			argList.add(entry.getKey());
			argList.add(entry.getValue());
		});

		// Scannables whose positions should also be recorded (e.g. XESBragg scannables)
		argList.addAll(extraOutputs);

		// The detectors
		argList.addAll(List.of(detList));

		return argList.toArray();
	}

	private XESEnergyScannable getEnergyScannable(String scannableName) {
		Optional<XESEnergyScannable> scn = Finder.findOptionalOfType(scannableName, XESEnergyScannable.class);
		if (scn.isPresent()) {
			return scn.get();
		}
		throw new IllegalArgumentException("Could not find XESEnergy object "+scannableName+" required to run XES scan");
	}

	private Scannable getXesEnergyScannable(XesScanParameters scanParams) throws Exception {
		ScanColourType colour = scanParams.getScanColourType();
		if (colour == ScanColourType.ONE_COLOUR || colour == ScanColourType.TWO_COLOUR) {
			return xesEnergyGroup;
		}

		int index = colour == ScanColourType.ONE_COLOUR_ROW1 ? 0 : 1;
		String scnName = scanParams.getScannableNameForRow(index);
		return getEnergyScannable(scnName);
	}

	private Scannable getXesAngleScannable(Scannable s) {
		if (s instanceof XESEnergyScannable xesScn) {
			return xesScn.getXes();
		}
		return xesBraggGroup;
	}

	private PyTuple getEnergiesFromScanBean(IScanParameters paramBean) throws Exception {
		if (paramBean instanceof XanesScanParameters xaneParams) {
			return XanesScanPointCreator.calculateEnergies(xaneParams);
		} else if (paramBean instanceof XasScanParameters xasParams) {
			return ExafsScanPointCreator.calculateEnergies(xasParams);
		}
		throw new IllegalArgumentException("Cannot get scan energies from IScanParameters object of type "+scanBean.getClass().getCanonicalName());
	}

	public Scannable getBraggGroup() {
		return xesBraggGroup;
	}

	public void setXesBraggGroup(Scannable xesBraggGroup) {
		this.xesBraggGroup = xesBraggGroup;
	}

	public Scannable getXesEnergyGroup() {
		return xesEnergyGroup;
	}

	public void setXesEnergyGroup(Scannable xesEnergyGroup) {
		this.xesEnergyGroup = xesEnergyGroup;
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

	private Scannable getEnergyTransferScannable(Scannable xesScannable) {
		if (energyTransferScannables.containsKey(xesScannable)) {
			return energyTransferScannables.get(xesScannable);
		}
		throw new IllegalArgumentException("Energy transfer scannable was not fround for "+xesScannable.getName());
	}

	public Map<Scannable, Scannable> getEnergyTransferScannables() {
		return energyTransferScannables;
	}

	public void setEnergyTransferScannables(Map<Scannable, Scannable> energyTransferScannables) {
		this.energyTransferScannables = energyTransferScannables;
	}


	public boolean isScanEnergyTransfer() {
		return scanEnergyTransfer;
	}

	public void setScanEnergyTransfer(boolean scanEnergyTransfer) {
		this.scanEnergyTransfer = scanEnergyTransfer;
	}
}
