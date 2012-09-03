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

	double sampleStagePixelsPerMMInX=100;
	double sampleStagePixelsPerMMInY=100;
	double cameraStagePixelsPerMMInX=50;
	double cameraStagePixelsPerMMInY=12.5;
	
	
	@Override
	public double getSampleStagePixelsPerMMInX() {
		return sampleStagePixelsPerMMInX;
	}
	public void setSampleStagePixelsPerMMInX(double sampleStagePixelsPerMMInX) {
		this.sampleStagePixelsPerMMInX = sampleStagePixelsPerMMInX;
	}
	@Override
	public double getSampleStagePixelsPerMMInY() {
		return sampleStagePixelsPerMMInY;
	}
	public void setSampleStagePixelsPerMMInY(double sampleStagePixelsPerMMInY) {
		this.sampleStagePixelsPerMMInY = sampleStagePixelsPerMMInY;
	}
	@Override
	public double getCameraStagePixelsPerMMInX() {
		return cameraStagePixelsPerMMInX;
	}
	public void setCameraStagePixelsPerMMInX(double cameraStagePixelsPerMMInX) {
		this.cameraStagePixelsPerMMInX = cameraStagePixelsPerMMInX;
	}
	@Override
	public double getCameraStagePixelsPerMMInY() {
		return cameraStagePixelsPerMMInY;
	}
	public void setCameraStagePixelsPerMMInY(double cameraStagePixelsPerMMInY) {
		this.cameraStagePixelsPerMMInY = cameraStagePixelsPerMMInY;
	}
	

}
