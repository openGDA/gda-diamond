/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

public class DisplayScaleProviderImpl implements DisplayScaleProvider {

	double pixelsPerMMInX=100;
	double pixelsPerMMInY=100;
	
	
	@Override
	public double getPixelsPerMMInX() {
		return pixelsPerMMInX;
	}

	@Override
	public double getPixelsPerMMInY() {
		return pixelsPerMMInY;
	}

	public void setPixelsPerMMInX(double pixelsPerMMInX) {
		this.pixelsPerMMInX = pixelsPerMMInX;
	}

	public void setPixelsPerMMInY(double pixelsPerMMInY) {
		this.pixelsPerMMInY = pixelsPerMMInY;
	}

}
