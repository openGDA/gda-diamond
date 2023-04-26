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

package gda.device.detector;

import java.util.Arrays;
import java.util.List;

import fr.esrf.Tango.DevFailed;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Class for using Ede detectors (XH and Frelon) in Continuous scans. The idea is that the detector runs
 * continuously whilst the motor moves without synchronisation between them. The detector can be started
 * by hardware trigger (external Tfg), initiated e.g. by pulse produced by zebra gate.
 * @since 30/10/2017
 */
public class BufferedEdeDetector extends DetectorBase implements BufferedDetector, NexusDetector {

	private static final long serialVersionUID = 1L;

	private EdeDetector detector;

	private int numberScansPerFrame = 1;
	private double accumulationTime = 1e-5;
	private boolean applyAccumulations = false;

	private boolean externalTriggerStart = false; // wait for trigger, e.g. from Tfg before starting collection
	private ContinuousParameters continuousParameters;
	private List<Integer> frameCounts;
	private int maxReadFrames = 1000;

	@Override
	public void prepareForCollection() {
		// do preparation in setContinuousParameters, after continuous parameters have been set.
	}

	public void setExternalTriggerMode(boolean external) throws DevFailed {
		externalTriggerStart = external;
	}

	public boolean getExternalTriggerMode() {
		return externalTriggerStart;
	}

	@Override
	public void atScanEnd() throws DeviceException {
		frameCounts = null;
		detector.stop();
		// Set frelon external trigger mode back to false
		// (so that software trigger steps scans, live mode etc will work)
		if (externalTriggerStart) {
			setFrelonExternalTrigger(false);
		}
	}

	@Override
	public void stop() throws DeviceException {
		atScanEnd();
	}

	public void setFrelonExternalTrigger(boolean extTrigger) {
		if (!(detector instanceof EdeFrelon) ) {
			return;
		}

		EdeFrelon edeDetector = (EdeFrelon) detector;
		FrelonCcdDetectorData detectorSettings = (FrelonCcdDetectorData) edeDetector.getDetectorData();
		if (extTrigger) {
			detectorSettings.setTriggerMode(AcqTriggerMode.EXTERNAL_TRIGGER);
		} else {
			detectorSettings.setTriggerMode(AcqTriggerMode.INTERNAL_TRIGGER);
		}
	}

	public void prepareDetectorForCollection(ContinuousParameters params) throws DeviceException {
		int numSpectra = params.getNumberDataPoints();
		double timePerSpectrum = params.getTotalTime()/params.getNumberDataPoints();
		if (applyAccumulations) {
			timePerSpectrum = accumulationTime * numberScansPerFrame;
			prepareDetectorForCollection(numSpectra, timePerSpectrum, accumulationTime, numberScansPerFrame);
		} else {
			prepareDetectorForCollection(numSpectra, timePerSpectrum, timePerSpectrum, 1);
		}
	}

	// Set detector using same params as for normal ede scan
	public void prepareDetectorForCollection(int numSpectra, double timePerSpectrum, double accumulationTime, int numAccumulations) throws DeviceException {
		TimingGroup newGroup = new TimingGroup();
		newGroup.setLabel("group1");
		newGroup.setNumberOfFrames(numSpectra);
		newGroup.setTimePerScan(accumulationTime);
		newGroup.setNumberOfScansPerFrame(numAccumulations);
		newGroup.setTimePerFrame(timePerSpectrum);
		newGroup.setDelayBetweenFrames(0);

		detector.prepareDetectorwithScanParameters(EdeScanParameters.createEdeScanParameters(Arrays.asList(newGroup)));
		if (detector instanceof EdeFrelon) {
			setFrelonExternalTrigger(externalTriggerStart);
			// for Frelon need to call configureDetectorForTimingGroup to setup for timing groups
			detector.configureDetectorForTimingGroup(newGroup);
		}
	}

	@Override
	public void collectData() throws DeviceException {
		detector.collectData();
	}

	@Override
	public int getStatus() throws DeviceException {
		return detector.getStatus();
	}

	@Override
	public void waitWhileBusy() throws DeviceException, InterruptedException {
		while (detector.getStatus() == BUSY) {
			Thread.sleep(100);
		}
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	@Override
	public void clearMemory() throws DeviceException {
	}

	@Override
	public void setContinuousMode(boolean on) throws DeviceException {
		if (on) {
			frameCounts = null;
			prepareDetectorForCollection(continuousParameters);
			detector.collectData();
		}
	}

	@Override
	public boolean isContinuousMode() throws DeviceException {
		return false;
	}

	@Override
	public int getNumberFrames() throws DeviceException {
		int numImages = detector.getLastImageAvailable();
		if (numImages == 0 && frameCounts != null && !frameCounts.isEmpty()) {
			// XH : at end of scan, some frames of data still to be read out but detector reports zero frames available
			// --> Return total number of points in the scan.
			return continuousParameters.getNumberDataPoints();
		}
		if (frameCounts != null) {
			frameCounts.add(numImages);
		}
		return numImages;
	}

	@Override
	public void setContinuousParameters(ContinuousParameters parameters) throws DeviceException {
		this.continuousParameters = parameters;
	}

	@Override
	public ContinuousParameters getContinuousParameters() throws DeviceException {
		return continuousParameters;
	}

	@Override
	public NexusTreeProvider readout() throws DeviceException {
		int latestFrame = getNumberFrames()-1;
		return detector.readFrames(latestFrame,  latestFrame)[0];
	}

	@Override
	public Object[] readFrames(int startFrame, int finalFrame) throws DeviceException {
		return detector.readFrames(startFrame,  finalFrame);
	}

	@Override
	public Object[] readAllFrames() throws DeviceException {
		return detector.readFrames(0,  getNumberFrames()-1);

	}

	@Override
	public int maximumReadFrames() throws DeviceException {
		return maxReadFrames;
	}

	public void setMaximumReadFrames(int maxReadFrames) {
		this.maxReadFrames = maxReadFrames;
	}

	public EdeDetector getDetector() {
		return detector;
	}

	public void setDetector(EdeDetector detector) {
		this.detector = detector;
	}

	@Override
	public String[] getExtraNames() {
		return detector.getExtraNames();
	}

	@Override
	public String[] getInputNames() {
		return detector.getInputNames();
	}

	@Override
	public String[] getOutputFormat() {
		return detector.getOutputFormat();
	}

	// Number of accumulations
	public int getNumberScansPerFrame() {
		return numberScansPerFrame;
	}

	public void setNumberScansPerFrame(int numberScansPerFrame) {
		this.numberScansPerFrame = numberScansPerFrame;
	}

	public double getAccumulationTime() {
		return accumulationTime;
	}
	public void setAccumulationTime(double accumulationTime) {
		this.accumulationTime = accumulationTime;
	}
	public boolean isApplyAccumulations() {
		return applyAccumulations;
	}
	public void setApplyAccumulations(boolean applyAccumulations) {
		this.applyAccumulations = applyAccumulations;
	}
}
