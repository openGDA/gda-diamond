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

import java.util.HashMap;

import org.dawnsci.ede.CalibrationDetails;
import org.eclipse.january.dataset.DoubleDataset;

import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import uk.ac.gda.ede.data.DetectorSetupType;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public interface EdeDetector extends NexusDetector {

	public static final String CALIBRATION_PROP_KEY = "calibration";
	public static final int INITIAL_NO_OF_ROIS = 4;
	public static final String ROIS_PROP_NAME = "rois";
	public static final String EXCLUDED_PIXELS_PROP_NAME = "excludedStrips";

	/**
	 * @param startFrame
	 * @param finalFrame
	 * @return read a range of frames
	 * @throws DeviceException
	 */
	NexusTreeProvider[] readFrames(int startFrame, int finalFrame) throws DeviceException;

	DoubleDataset createDatasetForPixel();

	void writeLiveDataFile() throws DeviceException;

	double[] getEnergyForChannels();

	Integer[] getPixels();

	DetectorData getDetectorData();

	int getNumberOfSpectra() throws DeviceException;

	HashMap<String, Double> getTemperatures() throws DeviceException;

	DetectorStatus fetchStatus() throws DeviceException;

	int getNumberScansInFrame(double frameTime, double scanTime, int numberOfFrames) throws DeviceException;

	int getMaxPixel();

	void prepareDetectorwithScanParameters(EdeScanParameters newParameters) throws DeviceException;

	/**
	 * to pull detector setting from detector server to synchronise the {@link DetectorData} object
	 */
	void fetchDetectorSettings();

	boolean isDropFirstFrame();
	/**
	 * Returns the function used to convert channel number to energy. If not calibrated it should return a simple y = x
	 * function.
	 *
	 * @return PolynomialFunction
	 */
	CalibrationDetails getEnergyCalibration();

	/**
	 * Set the energy calibration. The detector object should persist this between GDA server restarts.
	 *
	 * @param calibrationDetails
	 */
	void setEnergyCalibration(CalibrationDetails calibrationDetails);

	boolean isEnergyCalibrationSet();

	/**
	 * Returns the regions in use, as defined by calls to setRois or setNumberRois
	 *
	 * @return the array of regions
	 */
	Roi[] getRois();

	/**
	 * Ignoring the lower and upper channel properties, explicitly set the regions in use.
	 *
	 * @param rois
	 */
	void setRois(Roi[] rois);

	/**
	 * Set evenly sized regions of interest, ignoring channels outside of the lower and upper channel limits.
	 *
	 * @param numberOfRois
	 */
	void setNumberRois(int numberOfRois);

	int getNumberOfRois();

	void setLowerChannel(int channel);

	int getLowerChannel();

	void setUpperChannel(int channel);

	int getUpperChannel();

	/**
	 * The numbers of the strips which should be excluded when returning the data and creating region totals.
	 * <p>
	 * NB: these strips are still to be accounted for by the set/getChannelBiases methods.
	 *
	 * @param excludedStrips
	 */
	void setExcludedPixels(Integer[] excludedStrips);

	Integer[] getExcludedPixels();

	int getRoiFor(int elementIndex);

	int getNumberScansInFrame();

	void setNumberScansInFrame( int numScansInFrame );

	void configureDetectorForTimingGroup(TimingGroup group) throws DeviceException;

	void configureDetectorForROI(int verticalBinning, int ccdLineBegin) throws DeviceException;

	void setSynchroniseToBeamOrbit( boolean synchroniseToBeamOrbit ) ;

	boolean getSynchroniseToBeamOrbit();

	void setSynchroniseBeamOrbitDelay( int synchroniseBeamOrbitDelay ) throws DeviceException;

	int getSynchroniseBeamOrbitDelay();

	void setOrbitWaitMethod( String methodString );

	String getOrbitWaitMethod();

	/**
	 * Set the accumulation readout time
	 * @param accumulationReadoutTime (in seconds)
	 */
	void setAccumulationReadoutTime(double timeSecs);

	/**
	 * @return Accumulation readout time (in seconds)
	 */
	double getAccumulationReadoutTime();

	DetectorSetupType getDetectorSetupType();

	void setDetectorSetupType(DetectorSetupType detectorSetupType);

	/**
	 * implements the read out of frames from the actual detector used.
	 *
	 * @param startFrame
	 * @param finalFrame
	 * @return an 1D integer array containing all frames concatenated from start frame to the final frame inclusively.
	 * @throws DeviceException
	 */
	int[] readoutFrames(int startFrame, int finalFrame) throws DeviceException;

	/**
	 *
	 * @return Index of last image on the detector available for reading out using.
	 * (i.e. -1 = no image is ready, 0 = 1 image is ready)
	 *
	 * @throws DeviceException
	 */
	int getLastImageAvailable() throws DeviceException;

	int getMaxNumFramesToRead();
}
