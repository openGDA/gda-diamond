/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

import java.io.Serializable;

/**
 * Event indicating that the camera zoom level has changed.
 */
public class CameraZoomLevelChangedEvent implements Serializable {
	
	private static final long serialVersionUID = 1L;
	
	public double newLevel;
	
	public CameraZoomLevelChangedEvent(double newLevel) {
		this.newLevel = newLevel;
	}
	
	@Override
	public String toString() {
		return String.format("CameraZoomLevelChangedEvent(newLevel=%.2f)", newLevel);
	}

}
