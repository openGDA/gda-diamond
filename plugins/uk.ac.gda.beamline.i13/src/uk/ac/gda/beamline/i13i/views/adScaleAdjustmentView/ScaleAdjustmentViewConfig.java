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

package uk.ac.gda.beamline.i13i.views.adScaleAdjustmentView;

import gda.device.detector.areadetector.v17.NDProcess;
import gda.device.detector.areadetector.v17.NDStats;

public class ScaleAdjustmentViewConfig implements ADController {
	public NDStats ndStats;
	public NDProcess ndProc;
	private int imageHistSize;
	private int imageHistMin;
	private int imageHistMax;
	@Override
	public NDStats getImageStats() {
		return ndStats;
	}
	@Override
	public NDProcess getLiveViewProc() {
		return ndProc;
	}
	public void setNdStats(NDStats ndStats) {
		this.ndStats = ndStats;
	}
	public void setNdProcess(NDProcess ndProc) {
		this.ndProc = ndProc;
	}
	
	
	@Override
	public int getImageHistSize() {
		return imageHistSize;
	}
	@Override
	public int getImageMin() {
		return imageHistMin;
	}
	@Override
	public int getImageMax() {
		return imageHistMax;
	}
	public void setImageHistSize(int imageHistSize) {
		this.imageHistSize = imageHistSize;
	}
	public void setImageHistMin(int imageHistMin) {
		this.imageHistMin = imageHistMin;
	}
	public void setImageHistMax(int imageHistMax) {
		this.imageHistMax = imageHistMax;
	}
	
	
}
