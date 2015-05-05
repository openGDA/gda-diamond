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

package gda.device.detector;

import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;

import java.util.HashMap;

import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;

import uk.ac.gda.exafs.calibration.data.CalibrationDetails;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

public interface EdeDetector extends NexusDetector {
	public static final String CALIBRATION_PROP_KEY = "calibration";
	public static final int INITIAL_NO_OF_ROIS = 4;

	public abstract NexusTreeProvider[] readFrames(int startFrame, int finalFrame) throws DeviceException;

	public abstract DoubleDataset createDatasetForPixel();

	public abstract void writeLiveDataFile() throws DeviceException;

	public abstract double[] getEnergyForChannels();

	public abstract Integer[] getPixels();
	public abstract DetectorData getDetectorData();
	public abstract int getNumberOfSpectra() throws DeviceException;
	public abstract HashMap<String, Double> getTemperatures() throws DeviceException;

	public abstract DetectorStatus fetchStatus() throws DeviceException;

	public abstract int getNumberScansInFrame(double frameTime, double scanTime, int numberOfFrames) throws DeviceException;

	public abstract int getMaxPixel();

	public abstract void prepareDetectorwithScanParameters(EdeScanParameters newParameters) throws DeviceException;
	/**
	 * to pull detector setting from detector server to synchronise the {@link DetectorData} object
	 */
	void synchronizWithDetectorData();

	boolean isDropFirstFrame();
	/**
	 * Returns the function used to convert channel number to energy. If not calibrated it should return a simple y = x
	 * function.
	 *
	 * @return PolynomialFunction
	 */
	public CalibrationDetails getEnergyCalibration();

	/**
	 * Set the energy calibration. The detector object should persist this between GDA server restarts.
	 *
	 * @param calibrationDetails
	 */
	public void setEnergyCalibration(CalibrationDetails calibrationDetails);

	boolean isEnergyCalibrationSet();

}
