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

package gda.device.detector;

import gda.device.DeviceException;
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
public interface StripDetector extends NexusDetector {

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
	 * Returns the regions in use, as defined by calls to setRois or setNumberRois
	 * 
	 * @return the array of regions
	 */
	public XHROI[] getRois();

	/**
	 * Ignoring the lower and upper channel properties, explicitly set the regions in use.
	 * 
	 * @param rois
	 */
	public void setRois(XHROI[] rois);

	/**
	 * Set evenly sized regions of interest, ignoring channels outside of the lower and upper channel limits.
	 * 
	 * @param numberOfRois
	 */
	public void setNumberRois(int numberOfRois);

	public void setLowerChannel(int channel);

	public int getLowerChannel();

	public void setUpperChannel(int channel);

	public int getUpperChannel();

	/**
	 * Sets the bias voltage. If the given value is 0.0 then the bias will be switched off. If non-zero then the bias
	 * will be swicthed on if necessary and then applied.
	 * 
	 * @throws DeviceException
	 */
	public void setBias(Double biasVoltage) throws DeviceException;

	/**
	 * @return the current bias voltage or 0.0 if biad switched off
	 * @throws DeviceException - thrown if there is a problem reading the current status
	 */
	public Double getBias() throws DeviceException;

	/**
	 * The numbers of the strips which should be excluded when returning the data and creating region totals.
	 * <p>
	 * NB: these strips are still to be accounted for by the set/getChannelBiases methods.
	 * 
	 * @param excludedStrips
	 * @throws DeviceException
	 */
	public void setExcludedStrips(int[] excludedStrips) throws DeviceException;

	public int[] getExcludedStrips();

	/**
	 * @return details of the experiment progress using an enhanced progress bean object
	 * @throws DeviceException
	 */
	public ExperimentStatus fetchStatus() throws DeviceException;

	/**
	 * Send the software trigger continue command.
	 * 
	 * @throws DeviceException
	 */
	public void fireSoftTrig() throws DeviceException;

}
