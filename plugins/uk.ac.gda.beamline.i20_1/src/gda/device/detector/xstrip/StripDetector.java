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

package gda.device.detector.xstrip;

import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.detector.DetectorStatus;
import gda.device.detector.EdeDetector;
import gda.device.detector.Roi;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

/**
 * Interface for strip detectors on the EDE beamline.
 * <p>
 * They should return their data as a Nexus file chunk with extraNames columns which are summations of different regions
 * across the strip.
 * <p>
 * There can be ignored channels at each end of the strip.
 * <p>
 * The detector is in charge of its own timing for the experiment. The timing information is supplied by a
 * EdeScanParameters object.
 */
public interface StripDetector extends EdeDetector {

	public static final String CALIBRATION_PROP_KEY = "calibration";

	/**
	 * Set up the time frames as defined by the supplied object.
	 * <p>
	 * The time frames are started by the start method.
	 *
	 * @param newParameters
	 * @throws DeviceException
	 */
	public void loadParameters(EdeScanParameters newParameters) throws DeviceException;

	/**
	 * Reload the last scan as defined by the last call to loadParameters;
	 *
	 * @throws DeviceException
	 */
	public void loadTemplateParameters() throws DeviceException;

	/**
	 * Return the scan that would be run by the next call to collectData or start, or that is underway.
	 *
	 * @return EdeScanParameters
	 */
	public EdeScanParameters getLoadedParameters();

	/**
	 * Start the time frame sequence supplied by the last call of loadParameters().
	 *
	 * @throws DeviceException
	 */
	public void start() throws DeviceException;

	/**
	 * @param startFrame
	 * @param finalFrame
	 * @return read a range of frames
	 * @throws DeviceException
	 */
	@Override
	public NexusTreeProvider[] readFrames(int startFrame, int finalFrame) throws DeviceException;

	/**
	 * @return the size of the mca produced by the detector i.e. the number of strips
	 */
	public int getNumberChannels();

	/**
	 * Returns the regions in use, as defined by calls to setRois or setNumberRois
	 *
	 * @return the array of regions
	 */
	@Override
	public Roi[] getRois();

	/**
	 * Ignoring the lower and upper channel properties, explicitly set the regions in use.
	 *
	 * @param rois
	 */
	@Override
	public void setRois(Roi[] rois);

	/**
	 * Set evenly sized regions of interest, ignoring channels outside of the lower and upper channel limits.
	 *
	 * @param numberOfRois
	 */
	@Override
	public void setNumberRois(int numberOfRois);

	@Override
	public void setLowerChannel(int channel);

	@Override
	public int getLowerChannel();

	@Override
	public void setUpperChannel(int channel);

	@Override
	public int getUpperChannel();

	/**
	 * Sets the bias voltage. If the given value is 0.0 then the bias will be switched off. If non-zero then the bias will be switched on if necessary and then
	 * applied.
	 *
	 * @throws DeviceException
	 */
	public void setBias(Double biasVoltage) throws DeviceException;

	/**
	 * @return the current bias voltage or 0.0 if bias switched off
	 * @throws DeviceException
	 *             - thrown if there is a problem reading the current status
	 */
	public Double getBias() throws DeviceException;

	/**
	 * @return Double - the highest acceptable bias voltage
	 */
	public Double getMaxBias();

	/**
	 * @return Double - the lowest acceptable bias voltage
	 */
	public Double getMinBias();

	/**
	 * The numbers of the strips which should be excluded when returning the data and creating region totals.
	 * <p>
	 * NB: these strips are still to be accounted for by the set/getChannelBiases methods.
	 *
	 * @param excludedStrips
	 * @throws DeviceException
	 */
	public void setExcludedStrips(Integer[] excludedStrips) throws DeviceException;

	public Integer[] getExcludedStrips();

	/**
	 * @return details of the experiment progress using an enhanced progress bean object
	 * @throws DeviceException
	 */
	@Override
	public DetectorStatus fetchStatus() throws DeviceException;

	/**
	 * Send the software trigger continue command.
	 *
	 * @throws DeviceException
	 */
	public void fireSoftTrig() throws DeviceException;

	/**
	 * Connect to the underlying hardware. These detectors do not connect to the hardware during their configure().
	 *
	 * @throws DeviceException
	 */
	public void connect() throws DeviceException;

	/**
	 * Disconnect to the underlying hardware
	 *
	 * @throws DeviceException
	 */
	public void disconnect() throws DeviceException;

	/**
	 * @return true if a successful call to connect() has been made, and not subsequently disconnected.
	 */
	public boolean isConnected();

	/**
	 * Returns the function used to convert channel number to energy. If not calibrated it should return a simple y = x
	 * function.
	 *
	 * @return PolynomialFunction
	 * @throws DeviceException
	 */
	//public CalibrationDetails getEnergyCalibration() throws DeviceException;

	/**
	 * Set the energy calibration. The detector object should persist this between GDA server restarts.
	 *
	 * @param calibrationDetails
	 * @throws DeviceException
	 */
	//public void setEnergyCalibration(CalibrationDetails calibrationDetails) throws DeviceException;

	//boolean isEnergyCalibrationSet();
}
