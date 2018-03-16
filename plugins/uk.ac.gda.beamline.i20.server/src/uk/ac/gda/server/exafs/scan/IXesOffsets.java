/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

/**
 * Interface used for Jython XESOffsets class (xes_offsets.py).
 * This allows the XESOffsets object created in localStation.py to be injected into XesScanFactory, XesScan
 * and the methods called when required during scans.
 */
public interface IXesOffsets {

	/** Apply offset parameters stored in file to XES spectrometer motors. */
	public void apply(String filename);

	/** Re-apply offset parameters previously set using {@link #apply(String)} */
	public void reApply();

	/** Save the offset values for each motor into an xml file */
	public void saveAs(String filename);

	/** @return Name of current offset file */
	public String getCurrentFile();

	/** Save current motor offsets to temporary file */
	public void saveToTemp();

	/** Apply motor offsets using values in temporary file */
	public void applyFromTemp();

	/** Set name of temporary file */
	public void setTempSaveName(String filename);

	/** Get name of temporary file */
	public String getTempSaveName();
}
