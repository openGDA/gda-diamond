/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package gda.images.camera;

import gda.device.DeviceException;
import gda.factory.Findable;

/**
 * Interface to be implemented by services that allow a sample to be moved in microns.
 */
public interface SampleMovementService extends Findable {

	/**
	 * Moves the sample in 'real-world' microns. When standing behind the goniometer, with the beam travelling right,
	 * H +ve is away from you, V +ve is vertically up, and B +ve is along the beam:
	 * 
	 * <p><img src="doc-files/micron_coords.png" />
	 * 
	 * <p>In this coordinate system, the B and V axes are not affected by any rotation of the goniometer; they are
	 * always orthogonal with respect to the H axis.
	 * 
	 * <p>To calculate the required physical movement, this method will take into account the rotation of the
	 * goniometer. A movement along 'standard' goniometer axes will be calculated using the current value of ω (along
	 * with the direction in which the goniometer rotates for a +ve rotation of ω).
	 */
	public void moveSampleByMicrons(double h, double v, double b) throws DeviceException;
	
	/**
	 * Moves the sample along the three standard goniometer axes. When standing behind the goniometer, with the beam
	 * travelling right, H +ve is away from you. The V and B axes are the axes that rotate as the goniometer rotates.
	 * 
	 * <p>When ω = 0°, V +ve will be vertically up, and B +ve will be along the beam, as with 'real-world' coordinates:
	 * 
	 * <p><img src="doc-files/std_axis_0.png" />
	 * 
	 * <p>As the goniometer rotates, the V and B axes also rotate. If the goniometer rotates anticlockwise for a +ve
	 * rotation of ω, then when ω = 90°:
	 * 
	 * <p><img src="doc-files/std_axis_90.png" />
	 * 
	 * <p>A beamline-dependent movement will be calculated using the beamline's axis orientation matrix. This simply
	 * involves reorienting the three axes.
	 */
	public void moveSampleByMicronsAlongStandardAxes(double h, double v, double b) throws DeviceException;
	
	/**
	 * Moves the sample along the beamline's goniometer axes.
	 */
	public void moveSampleByMicronsAlongBeamlineAxes(double x, double y, double z) throws DeviceException;
	
}
