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

import gda.factory.Findable;
import gda.observable.IObservable;
import uk.ac.gda.exafs.calibration.data.CalibrationDetails;

public interface IDetectorData extends IObservable, Findable {

	public static final String ROIS_PROP_NAME = "rois";

	public abstract int getLowerChannel();

	public abstract void setLowerChannel(int lowerChannel);

	public abstract int getUpperChannel();

	public abstract void setUpperChannel(int upperChannel);

	public abstract Roi[] getRois();

	public abstract void setRois(Roi[] rois);

	public abstract CalibrationDetails getEnergyCalibration();

	public abstract void setEnergyCalibration(CalibrationDetails energyCalibration);

	public abstract boolean isEnergyCalibrationSet();

	public abstract Integer[] getExcludedPixels();

	public abstract void setExcludedPixels(Integer[] excludedPixels);

	public abstract void setNumberRois(int numberOfRois);

	public abstract int getRoiFor(int elementIndex);

}