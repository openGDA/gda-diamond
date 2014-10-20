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

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.DetectorFillingMonitorScannable;
import gda.device.scannable.I18BeamMonitor;
import gda.device.scannable.LineRepeatingBeamMonitor;
import gda.device.scannable.TopupChecker;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServer;
import gda.util.converters.AutoRenameableConverter;

import java.util.Date;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.server.exafs.scan.BeamlinePreparer;

/**
 * Configures beamline energy and scan monitors for each experiment.
 * <p>
 * TODO check that this works for every scan type! It probably does not at the moment.
 */
public class I18BeamlinePreparer implements BeamlinePreparer {

	private static Logger logger = LoggerFactory.getLogger(I18BeamlinePreparer.class);

	private final TopupChecker topupMonitor;
	private final I18BeamMonitor beamMonitor;
	private final DetectorFillingMonitorScannable detectorFillingMonitor;
	private final LineRepeatingBeamMonitor trajBeamMonitor;
	private final AutoRenameableConverter auto_mDeg_idGap_mm_converter;
	private final Scannable energyScannable;

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;
	private ISampleParameters sampleParameters;
	private IOutputParameters outputBean;
	private String experimentFullPath;
	private Date scanStart;

	private boolean handleGapConverter;

	public I18BeamlinePreparer(TopupChecker topupMonitor, I18BeamMonitor beamMonitor,
			DetectorFillingMonitorScannable detectorFillingMonitor, LineRepeatingBeamMonitor trajBeamMonitor,
			Scannable energyScannable, AutoRenameableConverter auto_mDeg_idGap_mm_converter) {
		this.topupMonitor = topupMonitor;
		this.beamMonitor = beamMonitor;
		this.detectorFillingMonitor = detectorFillingMonitor;
		this.trajBeamMonitor = trajBeamMonitor;
		this.energyScannable = energyScannable;
		this.auto_mDeg_idGap_mm_converter = auto_mDeg_idGap_mm_converter;
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean,
			ISampleParameters sampleParameters, IOutputParameters outputBean, String experimentFullPath)
			throws Exception {
		this.scanBean = scanBean;
		this.detectorBean = detectorBean;
		this.sampleParameters = sampleParameters;
		this.outputBean = outputBean;
		this.experimentFullPath = experimentFullPath;
	}

	@Override
	public void prepareForExperiment() throws Exception {

		// only run fluorescence maps on I18, not transmission maps.
		if (scanBean instanceof MicroFocusScanParameters && detectorBean.getExperimentType().equals("Transmission")){
			throw new IllegalArgumentException("Need to set the detector parameters to be Fluorescence for maps. Cannot run this map.");
		}

		if (LocalProperties.get("gda.mode").equals("live")) {
			// topupMonitor and beamMonitor should be defaults in every I18 scan
			topupMonitor.setPauseBeforePoint(true);
			// if step map only
			// topupMonitor.setCollectionTime(((XasScanParameters) scanBean).getCollectionTime());
			topupMonitor.setPauseBeforeLine(false);

			beamMonitor.setPauseBeforePoint(true);
			beamMonitor.setPauseBeforeLine(true);

			if (detectorBean.getExperimentType().equals("Fluorescence")
					&& detectorBean.getFluorescenceParameters().getDetectorType().equals("Germanium")) {
				((JythonServer) Finder.getInstance().find("command_server")).addDefault(detectorFillingMonitor);
				detectorFillingMonitor.setPauseBeforePoint(true);
				detectorFillingMonitor.setPauseBeforeLine(false);
			}

			setupHarmonic();
		}
		
		scanStart = new Date();
	}

	private void setupHarmonic() throws DeviceException, InterruptedException {// : #, gap_converter):
		moveMonoToInitialPosition();
	}

	private void moveMonoToInitialPosition() throws DeviceException, InterruptedException {
		handleGapConverter = true;
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

		if (energyScannable != null && initialPosition != null) {
			energyScannable.waitWhileBusy();
			energyScannable.asynchronousMoveTo(initialPosition);
			log("Moving mono to initial position...");
			log("move complete, disabling harmonic change");
			log("disabling harmonic converter");

			auto_mDeg_idGap_mm_converter.disableAutoConversion();
			handleGapConverter = true;
		}
	}

	protected void log(String msg) {
		InterfaceProvider.getTerminalPrinter().print(msg);
		logger.info(msg);
	}

	@Override
	public void completeExperiment() throws Exception {

		Date scanEnd = new Date();
		log("Map start time " + scanStart);
		log("Map end time " + scanEnd);
		// if (moveMonoToStartBeforeScan) {
		energyScannable.stop();
		// }
		if (handleGapConverter) {
			// TODO move to I18's detectorPreparer.completeCollection() call one of the preparers here to do some
			// beamline specific reset
			// print "enabling gap converter"
			// Object auto_mDeg_idGap_mm_converter = Finder.getInstance().find("auto_mDeg_idGap_mm_converter");
			auto_mDeg_idGap_mm_converter.enableAutoConversion();
		}

		// for maps
		((JythonServer) Finder.getInstance().find("command_server")).removeDefault(detectorFillingMonitor);
	}

}
