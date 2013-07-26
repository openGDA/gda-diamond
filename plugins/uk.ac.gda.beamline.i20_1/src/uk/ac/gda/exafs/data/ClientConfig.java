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

package uk.ac.gda.exafs.data;

import gda.device.Scannable;
import gda.factory.Finder;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ClientConfig {

	public static final int KILO_UNIT = 1000;
	public static final int DEFAULT_DECIMAL_PLACE = 2;

	private ClientConfig() {}

	public static String roundDoubletoString(double value) {
		return String.format("%." + DEFAULT_DECIMAL_PLACE + "f", value);
	}

	public enum UnitSetup {
		MILLI_METER("mm"),
		MILLI_RADIAN("mrad"),
		DEGREE("deg"),
		WATT("W"),
		EV("eV"),
		VOLTAGE("V"),
		MILLI_SEC("ms"),

		SELECTION("");

		private final String text;

		private UnitSetup(String text) {
			this.text = text;
		}

		public String getText() {
			return text;
		}

		public String addUnitSuffix(String value) {
			if (!value.isEmpty()) {
				return String.format("%s %s", value, text);
			}
			return value;
		}

		public String addUnitSuffixForLabel(String value) {
			if (!value.isEmpty()) {
				return String.format("%s (%s): ", value, text);
			}
			return String.format("(%s): ", text);
		}

		public String removeUnitSuffix(String value) throws Exception {
			if (text.isEmpty() | value.isEmpty()) {
				return value.trim();
			}
			Matcher matcher = Pattern.compile("(.*)\\s" + text + "$").matcher(value);
			if (matcher.find()) {
				return matcher.group(1).trim();
			}
			throw new Exception("Unable to find Unit suffix to remove");
		}
	}

	public enum CrystalType {
		Bragg, Laue;
		public static final String UI_LABEL = "Crystal type:";
	}

	public enum CrystalCut {
		// See requirement spec for assigned values
		Si111(6 * KILO_UNIT, 14 * KILO_UNIT), Si311(7 * KILO_UNIT, 26 * KILO_UNIT);

		private final double min;
		private final double max;
		public static final String UI_LABEL = "Crystal cut:";

		private CrystalCut(double min, double max) {
			this.min = min;
			this.max = max;
		}

		public double getMax() {
			return max;
		}

		public double getMin() {
			return min;
		}
	}

	public enum ScannableSetup {

		WIGGLER_GAP ("Wiggler gap", "wigglerGap", UnitSetup.MILLI_METER),
		POLY_BENDER_1("Bender 1", "polybend1", UnitSetup.MILLI_METER),
		POLY_BENDER_2("Bender 2", "polybend2",UnitSetup.MILLI_METER),

		SAMPLE_Z_POSITION("Sample z", "sample_z", UnitSetup.MILLI_METER),

		SLIT_1_HORIZONAL_GAP("Primary slit hgap", "s1_hgap", UnitSetup.MILLI_RADIAN),

		ATN1 ("ATN 1", "atn1", UnitSetup.SELECTION),
		ATN2 ("ATN 2", "atn2", UnitSetup.SELECTION),
		ATN3 ("ATN 3", "atn3", UnitSetup.SELECTION),

		ME1_STRIPE("ME1 stripe", "me1_stripe", UnitSetup.SELECTION),
		ME2_STRIPE("ME2 stripe", "me2_stripe", UnitSetup.SELECTION),
		ME2_PITCH_ANGLE("ME2 pitch", "me2pitch", UnitSetup.MILLI_RADIAN),

		POLY_BRAGG ("Bragg", "polytheta", UnitSetup.DEGREE),
		ARM_2_THETA_ANGLE ("Arm 2theta", "twotheta", UnitSetup.DEGREE),

		DETECTOR_HEIGHT ("Detector height", "detector_y", UnitSetup.MILLI_METER),
		DETECTOR_DISTANCE ("Detector distance", "detector_z", UnitSetup.MILLI_METER),

		POLY_CURVATURE("Curvature", "polycurve", UnitSetup.MILLI_METER),
		POLY_Y_ELLIPTICITY("Ellipticity","polyyellip", UnitSetup.MILLI_METER),

		SLIT_3_HORIZONAL_GAP("Slit hgap", "s3_hgap", UnitSetup.MILLI_METER),
		SLIT_3_HORIZONAL_OFFSET("Slit offset", "s3_hoffset", UnitSetup.MILLI_METER);

		public static final double MAX_POWER_IN_WATT = 150.0;

		private final String scannableName;
		private final String label;
		private final UnitSetup unit;

		private Object uiViewer;

		private ScannableSetup(String label, String scannableName, UnitSetup unit) {
			this.label = label;
			this.scannableName = scannableName;
			this.unit = unit;
		}

		public String getScannableName() {
			return scannableName;
		}

		public Scannable getScannable() throws Exception {
			Scannable scannable = Finder.getInstance().find(scannableName);
			if (scannable == null) {
				throw new Exception(label + " is not connected");
			}
			return scannable;
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
}
