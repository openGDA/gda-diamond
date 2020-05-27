/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.data;

import gda.device.Scannable;
import gda.factory.Finder;
import uk.ac.gda.client.observablemodels.ScannableWrapper;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;

public enum ScannableSetup {

	WIGGLER_GAP("Wiggler gap", "wiggler_gap", UnitSetup.MILLI_METER),
	FRONTEND_APERTURE("FE aperture", "frontend_aperture", UnitSetup.MILLI_METER),
	POLY_BENDER_1("Bender 1", "poly_bend1", UnitSetup.MILLI_METER),
	POLY_BENDER_2("Bender 2", "poly_bend2",UnitSetup.MILLI_METER),

	SAMPLE_TABLEX_POSITION("Sample table x", "sample_tablex", UnitSetup.MILLI_METER),
	SAMPLE_TABLEY_POSITION("Sample table y", "sample_tabley", UnitSetup.MILLI_METER),
	SAMPLE_X_POSITION("Sample x", "sample_x", UnitSetup.MILLI_METER),
	SAMPLE_Y_POSITION("Sample y", "sample_y", UnitSetup.MILLI_METER),
	SAMPLE_Z_POSITION("Sample z", "sample_z", UnitSetup.MILLI_METER),
	SAMPLE_TOP_X_POSITION("Sample top x", "sample_topx", UnitSetup.MILLI_METER),
	SAMPLE_TOP_Y_POSITION("Sample top y", "sample_topy", UnitSetup.MILLI_METER),
	SAMPLE_TOP_Z_POSITION("Sample top z", "sample_topz", UnitSetup.MILLI_METER),
	SAMPLE_PITCH_POSITION("Sample pitch", "sample_pitch", UnitSetup.DEGREE),
	SAMPLE_ROLL_POSITION("Sample roll", "sample_roll", UnitSetup.DEGREE),
	USER_MOTOR1_POSITION("User motor 1", "um1", UnitSetup.MILLI_METER),
	USER_MOTOR2_POSITION("User motor 2", "um2", UnitSetup.MILLI_METER),

	SLIT_1_HORIZONAL_GAP("Primary slit hgap", "s1_hgap", UnitSetup.MILLI_RADIAN),

	ATN1 ("ATN 1", "atn1", UnitSetup.SELECTION),
	ATN2 ("ATN 2", "atn2", UnitSetup.SELECTION),
	ATN3 ("ATN 3", "atn3", UnitSetup.SELECTION),
	ATN4 ("ATN 4", "atn4", UnitSetup.SELECTION),
	ATN5 ("ATN 5", "atn6", UnitSetup.SELECTION),

	ME1_STRIPE("ME1 stripe", "me1_stripe", UnitSetup.SELECTION),
	ME2_STRIPE("ME2 stripe", "me2_stripe", UnitSetup.SELECTION),
	ME2_PITCH_ANGLE("ME2 pitch", "me2_pitch", UnitSetup.MILLI_RADIAN),

	POLY_BRAGG ("Bragg", "poly_theta", UnitSetup.DEGREE),
	ARM_2_THETA_ANGLE ("Arm 2theta", "twotheta", UnitSetup.DEGREE),

	DETECTOR_HEIGHT ("Detector height", "det_y", UnitSetup.MILLI_METER),
	DETECTOR_Z_POSITION ("Detector z", "det_z", UnitSetup.MILLI_METER),
	DETECTOR_DISTANCE ("Detector distance", "det_distance", UnitSetup.MILLI_METER),

	POLY_CURVATURE("Curvature", "poly_curve", UnitSetup.MILLI_METER),
	POLY_Y_ELLIPTICITY("Ellipticity","poly_ellip", UnitSetup.MILLI_METER),
	POLY_TWIST("Twist","poly_twist", UnitSetup.MILLI_METER),

	SLIT_3_HORIZONAL_GAP("Slit hgap", "as_hgap", UnitSetup.MILLI_METER),
	SLIT_3_HORIZONAL_OFFSET("Slit offset", "as_hoffset", UnitSetup.MILLI_METER),

	ALIGNMENT_STAGE_X_POSITION("Alignment stage x", "alignment_x", UnitSetup.MILLI_METER),
	ALIGNMENT_STAGE_Y_POSITION("Alignment stage y", "alignment_y", UnitSetup.MILLI_METER),
	FAST_SHUTTER_X_POSITION("Fast shutter x", "fast_shutter_x", UnitSetup.MILLI_METER), // imh
	FAST_SHUTTER_Y_POSITION("Fast shutter y", "fast_shutter_y", UnitSetup.MILLI_METER), // imh
	ALIGNMENT_STAGE("Alignment stage", "alignment_stage", UnitSetup.SELECTION);

	public static final int MAX_POWER_IN_WATT = 100;

	private final String scannableName;
	private final String label;
	private final UnitSetup unit;

	private Object uiViewer;

	private Scannable scannable;

	private ScannableWrapper scannableWrapper;

	private ScannableSetup(String label, String scannableName, UnitSetup unit) {
		this.label = label;
		this.scannableName = scannableName;
		this.unit = unit;
	}

	public String getScannableName() {
		return scannableName;
	}

	public Scannable getScannable() throws Exception {
		if (scannable == null) {
			synchronized (this) {
				if (scannable == null) {
					Scannable scannable = Finder.getInstance().find(scannableName);
					if (scannable == null) {
						throw new Exception(label + " object is not found on GDA server");
					}
					this.scannable = scannable;
				}
			}
		}
		return scannable;
	}

	public ScannableWrapper getScannableWrapper() throws Exception {
		if (scannableWrapper == null) {
			synchronized (this) {
				if (scannableWrapper == null) {
					scannableWrapper = new ScannableWrapper(getScannable());
				}
			}
		}
		return scannableWrapper;
	}

	public UnitSetup getUnit() {
		return unit;
	}

	public String getLabel() {
		return label;
	}

	public String getLabelForUI() {
		if (!unit.getText().isEmpty()) {
			return label + " (" + unit.getText() + "):";
		}
		return label + ":";
	}

	public Object getUiViewer() {
		return uiViewer;
	}

	public void setUiViewer(Object uiViewer) {
		this.uiViewer = uiViewer;
	}
}