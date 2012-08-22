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

package uk.ac.gda.beamline.i13i;


/**
 * Interface for listening to image mode changes
 * <p>
 * This interface may be implemented by clients.
 * <p>
 */
public interface IImageModeListener {
	
	/**
	 * Notifies this listener that the image mode has changed.
	 * <p>
	 * This method is called when the image mode changes. 
	 * <p>
	 * 
	 * @param mode the current mode {@link IImageMode}
	 */
	public void imageModeChanged(IImageMode mode);

}
