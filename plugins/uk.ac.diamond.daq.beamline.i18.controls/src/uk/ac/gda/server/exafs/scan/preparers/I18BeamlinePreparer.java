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

package uk.ac.gda.server.exafs.scan.preparers;

import java.util.Date;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.BeamMonitor;
import gda.device.scannable.DetectorFillingMonitorScannable;
import gda.device.scannable.TopupChecker;
import gda.jython.InterfaceProvider;
import gda.jython.commands.ScannableCommands;
import gda.util.converters.AutoRenameableConverter;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.server.exafs.scan.BeamlinePreparer;

/**
 * Configures beamline energy and scan monitors for each experiment.
 */
public class I18BeamlinePreparer implements BeamlinePreparer {

	private static Logger logger = LoggerFactory.getLogger(I18BeamlinePreparer.class);

	private final TopupChecker topupMonitor;
	private final BeamMonitor beamMonitor;
	private final DetectorFillingMonitorScannable detectorFillingMonitor;
	private final AutoRenameableConverter auto_mDeg_idGap_mm_converter;
	protected Scannable energyNoGap;
	protected Scannable energyWithGap;
	protected Scannable energyInUse;

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;
	private Date scanStart;

	public I18BeamlinePreparer(TopupChecker topupMonitor, BeamMonitor beamMonitor,
			DetectorFillingMonitorScannable detectorFillingMonitor,
			Scannable energyWithGap, Scannable energyNoGap, AutoRenameableConverter auto_mDeg_idGap_mm_converter) {
		this.topupMonitor = topupMonitor;
		this.beamMonitor = beamMonitor;
		this.detectorFillingMonitor = detectorFillingMonitor;
		this.energyWithGap = energyWithGap;
		this.energyNoGap = energyNoGap;
		this.energyInUse = energyWithGap;
		this.auto_mDeg_idGap_mm_converter = auto_mDeg_idGap_mm_converter;
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean,
			ISampleParameters sampleParameters, IOutputParameters outputBean, String experimentFullPath)
			throws Exception {
		this.scanBean = scanBean;
		this.detectorBean = detectorBean;
	}

	@Override
	public void prepareForExperiment() throws Exception {

		// only run fluorescence maps on I18, not transmission maps.
		if (scanBean instanceof MicroFocusScanParameters && detectorBean.getExperimentType().equals("Transmission")){
			throw new IllegalArgumentException("Need to set the detector parameters to be Fluorescence for maps. Cannot run this map.");
		}

		if (LocalProperties.get("gda.mode").equals("live")) {
			topupMonitor.setPauseBeforePoint(true);
			topupMonitor.setPauseBeforeLine(true);
			// set the topupMonitor to use the correct time before topup
			configureTopupMonitor();

			beamMonitor.setPauseBeforePoint(true);
			beamMonitor.setPauseBeforeLine(true);

			// if we are using the Ge detector, then add the detectorFillingMonitor
			if (detectorBean.getExperimentType().equals("Fluorescence")
					&& detectorBean.getFluorescenceParameters().getDetectorType().equals("Germanium")) {
				detectorFillingMonitor.setPauseBeforePoint(true);
				detectorFillingMonitor.setPauseBeforeLine(true);
				ScannableCommands.add_default(detectorFillingMonitor);
			} else {
				ScannableCommands.remove_default(detectorFillingMonitor);
			}

			setupHarmonic();
		}

		scanStart = new Date();
	}

	private void configureTopupMonitor() {
		if (scanBean instanceof MicroFocusScanParameters){
			// set to the point time
			double pointTime = ((MicroFocusScanParameters) scanBean).getCollectionTime();
			topupMonitor.setCollectionTime(pointTime);
		} else if (scanBean instanceof XasScanParameters) {
			// set to the longest time step
			XasScanParameters parameters = (XasScanParameters) scanBean;
			double maxTime = 0;
			if (parameters.getEdgeTime() > maxTime) maxTime = parameters.getEdgeTime();
			if (parameters.getPreEdgeTime() > maxTime) maxTime = parameters.getPreEdgeTime();
			if (parameters.getExafsTime() > maxTime) maxTime = parameters.getExafsTime();
			if (parameters.getExafsFromTime() > maxTime) maxTime = parameters.getExafsFromTime();
			if (parameters.getExafsToTime() > maxTime) maxTime = parameters.getExafsToTime();
			topupMonitor.setCollectionTime(maxTime);
		} else if (scanBean instanceof XanesScanParameters) {
			List<Region> regions = ((XanesScanParameters) scanBean).getRegions();
			double maxTime = 0;
			for(Region region : regions){
				if (region.getTime() > maxTime){
					maxTime = region.getTime();
				}
			}
			topupMonitor.setCollectionTime(maxTime);
		}
	}

	private void setupHarmonic() throws DeviceException, InterruptedException {// : #, gap_converter):
		moveMonoToInitialPosition();
	}

	private void moveMonoToInitialPosition() throws DeviceException, InterruptedException {
		Double initialPosition = null;
		if (scanBean instanceof XasScanParameters) {
			initialPosition = ((XasScanParameters) scanBean).getInitialEnergy();
		} else if (scanBean instanceof XanesScanParameters) {
			initialPosition = ((XanesScanParameters) scanBean).getRegions().get(0).getEnergy();
		} else if (scanBean instanceof XesScanParameters) {
			int xes_scanType = ((XesScanParameters) scanBean).getScanType();
			if (xes_scanType == XesScanParameters.SCAN_XES_FIXED_MONO) {
				initialPosition = ((XesScanParameters) scanBean).getMonoEnergy();
			} else {
				initialPosition = ((XesScanParameters) scanBean).getMonoInitialEnergy();
			}
		}

		if (energyInUse != null && initialPosition != null) {
			energyInUse.waitWhileBusy();
			log("Moving mono to initial position...");
			energyInUse.moveTo(initialPosition);

			if (energyInUse == energyWithGap) {
				log("mono move complete, disabling harmonic change");
				auto_mDeg_idGap_mm_converter.disableAutoConversion();
			} else {
				log("mono move complete.");
			}
		}
	}

	protected void log(String msg) {
		InterfaceProvider.getTerminalPrinter().print(msg);
		logger.info(msg);
	}

	@Override
	public void completeExperiment() throws Exception {

		if (scanBean instanceof MicroFocusScanParameters) {
			Date scanEnd = new Date();
			log("Map start time " + scanStart);
			log("Map end time " + scanEnd);
		}

		if (energyInUse == energyWithGap) {
			log("Re-enabling ID harmonic change");
			auto_mDeg_idGap_mm_converter.enableAutoConversion();
		}

		ScannableCommands.remove_default(detectorFillingMonitor);
	}

	public void setUseWithGapEnergy() {
		energyInUse = energyWithGap;
		logEnergyInUse();
	}

	public void setUseNoGapEnergy() {
		energyInUse = energyNoGap;
		logEnergyInUse();
	}

	public void logEnergyInUse() {
		log("Energy in use: " + energyInUse.getName());
		if (energyInUse == energyWithGap) {
			log("Energy changes will move the ID gap, but the ID gap should not change harmonic during energy scans");
		} else if (energyInUse == energyNoGap) {
			log("Energy changes will move the DCM only; the ID gap will not move");
		} else {
			log("Error: unexpected energy scannable");
		}
	}
}
