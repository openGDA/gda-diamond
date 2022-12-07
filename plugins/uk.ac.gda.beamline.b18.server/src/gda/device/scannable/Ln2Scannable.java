/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.device.scannable.scannablegroup.IScannableGroup;
import gda.jython.JythonServerFacade;
public class Ln2Scannable extends ScannableBase {

	private IScannableGroup cryo;
	private String cylinderType;
	private double height;
	private double angle;
	private double heightCalibration=0;
	private double angleCalibration=0;
	private int heightIndex;
	private int angleIndex;

	@Override
	public boolean isBusy() throws DeviceException {
		return cryo.isBusy();
	}

	public void moveTo(int heightIndex, int angleIndex) throws DeviceException {

		height = heightCalibration + (heightIndex-1)*17.0;

		if(cylinderType.equals("trans")){
			angle = angleCalibration + ((angleIndex-1)*16.36);
		}
		else if(cylinderType.equals("fluo")){
			if(angleIndex<5)
				angle = angleCalibration + ((angleIndex-1)*22.5);
			else
				angle = angleCalibration + 180.0 + ((angleIndex-5)*22.5);
		}

		double[] newPosition = new double[2];
		newPosition[0]=height;
		newPosition[1]=angle;
		cryo.asynchronousMoveTo(newPosition);

		JythonServerFacade.getInstance().print("Moving cryo");

		while(cryo.isBusy()){
			Thread.yield();
		}

		JythonServerFacade.getInstance().print("Move complete : "+cryo.toFormattedString());
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		int[] indices = new int[2];
		indices[0]=heightIndex;
		indices[0]=angleIndex;
		return indices;
	}

	public String getCylinderType() {
		return cylinderType;
	}

	public void setCylinderType(String cylinderType) {
		this.cylinderType = cylinderType;
	}

	public double getHeightCalibration() {
		return heightCalibration;
	}

	public void setHeightCalibration(double heightCalibration) {
		this.heightCalibration = heightCalibration;
	}

	public double getAngleCalibration() {
		return angleCalibration;
	}

	public void setAngleCalibration(double angleCalibration) {
		this.angleCalibration = angleCalibration;
	}

	public IScannableGroup getCryo() {
		return cryo;
	}

	public void setCryo(IScannableGroup cryo) {
		this.cryo = cryo;
	}
}
