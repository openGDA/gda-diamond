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

import gda.device.detector.StripDetector;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ScannableSetup {

	public static Integer[] STRIPS;
	static {
		STRIPS = new Integer[DetectorSetup.MAX_STRIPS];
		for (int i = 0; i < DetectorSetup.MAX_STRIPS; i++) {
			STRIPS[i] = new Integer(i + 1);
		}
	}

	public static final int KILO_UNIT = 1000;

	private ScannableSetup() {}

	public enum Units {
		MILLI_METER ("mm"),
		MILLI_RADIAN ("mrad"),
		DEGREE ("deg"),
		WATT ("W"),
		EV ("eV"),
		VOLTAGE ("V"),
		MILLI_SEC ("ms");

		private final String text;

		private Units(String text) {
			this.text = text;
		}

		public String getText() {
			return text;
		}

		public String addUnitSuffix(String value) {
			return String.format("%s %s", value, text);
		}

		public String removeUnitSuffix(String value) throws Exception {
			Matcher matcher = Pattern.compile("(.*)\\s" + text + "$").matcher(value);
			if (matcher.find()) {
				return matcher.group(1);
			}
			throw new Exception("Unable to find Unit suffix to remove");
		}
	}

	public enum CrystalCut {
		// See requirement spec for assigned values
		Si111 (6 * KILO_UNIT, 14 * KILO_UNIT),
		Si311 (7 * KILO_UNIT, 26 * KILO_UNIT);

		private final double min;
		private final double max;

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

	public enum Scannables {
		POLY_BENDER_1 ("Bender 1", "polybend1", Units.MILLI_METER),
		POLY_BENDER_2 ("Bender 2", "polybend2", Units.MILLI_METER),
		POLY_CURVATURE ("Curvature", "polycurve", Units.MILLI_METER),
		POLY_Y_ELLIPTICITY ("Ellipticity", "polyyellip", Units.MILLI_METER),

		SAMPLE_Z_POSITION ("Sample_z", "sample_z", Units.MILLI_METER),

		SLIT_1_HORIZONAL_GAP ("Slit 1 HGap", "s1_hgap", Units.MILLI_METER),
		SLIT_1_VERTICAL_GAP ("Slit 1 VGap", "s1_vgap", Units.MILLI_METER),

		// TODO Fill label and scannable names
		SLIT_1_HORIZONAL_OFFSET ("", "s1_hoffset", Units.MILLI_METER),
		SLIT_1_VERTICAL_OFFSET ("", "s1_voffset", Units.MILLI_METER),
		SLIT_2_HORIZONAL_GAP ("", "s2_vgap", Units.MILLI_METER),
		SLIT_2_VERTICAL_GAP ("", "s2_vgap", Units.MILLI_METER),
		SLIT_2_HORIZONAL_OFFSET ("", "s2_hoffset", Units.MILLI_METER),
		SLIT_2_VERTICAL_OFFSET ("", "s2_voffset", Units.MILLI_METER),
		SLIT_INTEGRATION_TIME ("", "", Units.MILLI_SEC);

		private final String scannableName;
		private final String label;
		private final Units unit;

		private Scannables(String label, String scannableName, Units unit) {
			this.scannableName = scannableName;
			this.label = label;
			this.unit = unit;
		}

		public String getScannableName() {
			return scannableName;
		}

		public Units getUnit() {
			return unit;
		}

		public String getLabel() {
			return label;
		}

		public String getLabelForUI() {
			return label + " (" + unit.getText() + "):";
		}
	}

	public enum DetectorSetup {
		XH ("xh"),
		XSTRIP ("xstrip"),
		CCD ("ccd");

		public static final int MIN_STRIPS = 1;
		public static final int MAX_STRIPS = 1024;

		private final String detectorName;
		private StripDetector detectorScannable;

		private DetectorSetup(String detectorName) {
			this.detectorName = detectorName;
		}

		public String getDetectorName() {
			return detectorName;
		}

		public void setDetectorScannable(StripDetector detectorScannable) {
			this.detectorScannable = detectorScannable;
		}

		public StripDetector getDetectorScannable() {
			return detectorScannable;
		}

		private static DetectorSetup activeDetectorSetup;
		public static void setActiveDetectorSetup(DetectorSetup detectorSetup) {
			activeDetectorSetup = detectorSetup;
		}

		public static DetectorSetup getActiveDetectorSetup() {
			return activeDetectorSetup;
		}
	}
}
