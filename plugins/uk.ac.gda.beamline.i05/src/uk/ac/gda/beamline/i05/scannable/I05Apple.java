/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i05.scannable;

import gda.device.DeviceException;
import gda.device.ScannableMotion;
import gda.device.scannable.scannablegroup.ScannableMotionWithScannableFieldsBase;

public class I05Apple extends ScannableMotionWithScannableFieldsBase {
	
	public final static String VERTICAL = "vertical";
	public final static String HORIZONTAL = "horizontal";
	public final static String CIRCULAR_LEFT = "left";
	public final static String CIRCULAR_RIGHT = "right";
	
	ScannableMotion gapScannable;
	ScannableMotion upperPhaseScannable;
	ScannableMotion lowerPhaseScannable;
	
	public I05Apple() {
		setInputNames(new String[] { "energy", "polarisation"});
		setExtraNames(new String[] {});
		setOutputFormat(new String[] {"%8.5f", "%s"});
	}
	
	public static double sigmoid(double k0, double k1, double k2, double k3, double x) {
		return k0 + k1 / (1 + Math.exp(-(x-k2)/k3));
	}
	
	public void checkPhases() throws DeviceException {
		if (!upperPhaseScannable.isAt(lowerPhaseScannable.getPosition()))
			throw new DeviceException("upper and lower phase out of sync");
	}
	
	public double getPhaseForGap(String polarisation) throws DeviceException {
		if (HORIZONTAL.equalsIgnoreCase(polarisation))
			return 0;
		if (VERTICAL.equalsIgnoreCase(polarisation)) {
			if (((Double) lowerPhaseScannable.getPosition()) > 0.0) {
				return 70;
			} 
			return -70;
		}
		Double gap = (Double) gapScannable.getPosition();
		Double phase = sigmoid(-682.768,746.135,-144.152,47.4809, gap);
		// TODO define left and right correctly
		if (CIRCULAR_RIGHT.equalsIgnoreCase(polarisation))
			phase *= -1;
		return phase;
	}

	public String getPolarisation() throws DeviceException {
		checkPhases();
		for (String polarisation : new String[] {HORIZONTAL, VERTICAL, CIRCULAR_LEFT, CIRCULAR_RIGHT}) {
			if (lowerPhaseScannable.isAt(getPhaseForGap(polarisation)))
				return polarisation;
		}
		throw new DeviceException("found undefined id setting");
	}
	
	private double getEnergy(String polarisation) throws DeviceException {
		Double gap = (Double) gapScannable.getPosition();

		if (HORIZONTAL.equalsIgnoreCase(polarisation)) {
//			K0 =-1.9376 //± 0.571 //base
//					K1 =617.85 //± 0.765 //max
//					K2 =102.02 //± 0.0669 //Xhalf
//					K3 =19.047 //± 0.0606 //rate
			return sigmoid(-1.9376, 617.85, 102.02, 19.047, gap);
		}
		if (VERTICAL.equalsIgnoreCase(polarisation)) {
//			K0 =-12.465 //± 2.12 //base
//					K1 =627.54 //± 2.39 //max
//					K2 =64.039 //± 0.143 //Xhalf
//					K3 =13.121 //± 0.116 //rate
			return sigmoid(-12.465, 627.54, 64.039, 13.121, gap);

		}
//		K0 =-8.2934 //± 1.13 //base
//				K1 =622.41 //± 1.51 //max
//				K2 =71.656 //± 0.0806 //Xhalf
//				K3 =13.788 //± 0.0785 //rate
		return sigmoid(-8.2934, 622.41, 71.656, 13.788, gap);
	}
	
	public double getEnergy() throws DeviceException {
		return getEnergy(getPolarisation());
	}

	public void setPolaristation(String newpol) throws DeviceException {
		throw new DeviceException("setting polarisation not implemented yet");
	}
	
	public void setEnergy(double neweng) throws DeviceException {
		throw new DeviceException("setting energy not implemented yet");
	}

	public ScannableMotion getGapScannable() {
		return gapScannable;
	}

	public void setGapScannable(ScannableMotion gapScannable) {
		this.gapScannable = gapScannable;
	}

	public ScannableMotion getUpperPhaseScannable() {
		return upperPhaseScannable;
	}

	public void setUpperPhaseScannable(ScannableMotion upperPhaseScannable) {
		this.upperPhaseScannable = upperPhaseScannable;
	}

	public ScannableMotion getLowerPhaseScannable() {
		return lowerPhaseScannable;
	}

	public void setLowerPhaseScannable(ScannableMotion lowerPhaseScannable) {
		this.lowerPhaseScannable = lowerPhaseScannable;
	}
	
	@Override
	public Object getPosition() throws DeviceException {
		checkPhases();
		return new Object[] { getEnergy(), getPolarisation() };
	}
	
	@Override
	public boolean isBusy() throws DeviceException {
		return gapScannable.isBusy() || upperPhaseScannable.isBusy() || lowerPhaseScannable.isBusy();
	}
}