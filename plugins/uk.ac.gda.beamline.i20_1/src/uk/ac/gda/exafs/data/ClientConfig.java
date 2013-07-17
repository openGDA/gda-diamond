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

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.StripDetector;
import gda.factory.Finder;

import java.text.DecimalFormat;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClientConfig {

	private static Logger logger = LoggerFactory.getLogger(ClientConfig.class);

	public static final int KILO_UNIT = 1000;
	public static final int DEFAULT_DECIMAL_PLACE = 2;

	private ClientConfig() {
	}

	private static final DecimalFormat df = new DecimalFormat("#0.00");

	public static String roundDoubletoString(double value) {
		return df.format(value);
	}

	public enum UnitSetup {
		MILLI_METER("mm"), MILLI_RADIAN("mrad"), DEGREE("deg"), WATT("W"), EV("eV"), VOLTAGE("V"), MILLI_SEC("ms"),

		SELECTION("");

		private final String text;

		private UnitSetup(String text) {
			this.text = text;
		}

		public String getText() {
			return text;
		}

		public String addUnitSuffix(String value) {
			return String.format("%s %s", value, text);
		}

		public String removeUnitSuffix(String value) throws Exception {
			if (text.isEmpty()) {
				return value.trim();
			}
			Matcher matcher = Pattern.compile("(.*)\\s" + text + "$").matcher(value);
			if (matcher.find()) {
				return matcher.group(1);
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
		WIGGLER_GAP("Wiggler Gap", "wigglerGap", UnitSetup.MILLI_METER),

		POLY_BENDER_1("Bender 1", "polybend1", UnitSetup.MILLI_METER), POLY_BENDER_2("Bender 2", "polybend2",
				UnitSetup.MILLI_METER),

				SAMPLE_Z_POSITION("Sample z", "sample_z", UnitSetup.MILLI_METER),

				// FIXME Check if this is the right scannable
				SLIT_1_HORIZONAL_GAP("Slit 1 HGap", "s1_hgap", UnitSetup.MILLI_RADIAN),

				ATN1("Attenuator 1", "atn1", UnitSetup.MILLI_METER), ATN2("Attenuator 2", "atn2", UnitSetup.MILLI_METER), ATN3(
						"Attenuator 3", "atn3", UnitSetup.MILLI_METER),

						ME1_STRIPE("ME1 strip", "me1_stripe", UnitSetup.SELECTION), ME2_STRIPE("ME2 strip", "me2_stripe",
								UnitSetup.SELECTION), ME2_PITCH_ANGLE("ME2 pitch", "me2pitch", UnitSetup.MILLI_RADIAN),

								POLY_BRAGG("Bragg angle", "polytheta", UnitSetup.DEGREE), ARM_2_THETA_ANGLE("Arm 2theta", "twotheta",
										UnitSetup.DEGREE),

										DETECTOR_HEIGHT("Detector height", "detector_y", UnitSetup.MILLI_METER), DETECTOR_DISTANCE("Detector distance",
												"detector_z", UnitSetup.MILLI_METER),

												POLY_CURVATURE("Curvature", "polycurve", UnitSetup.MILLI_METER), POLY_Y_ELLIPTICITY("Ellipticity",
														"polyyellip", UnitSetup.MILLI_METER),

														SLIT_3_HORIZONAL_GAP("Slit HGap", "s3_hgap", UnitSetup.MILLI_METER), SLIT_3_HORIZONAL_OFFSET("Slit offset",
																"s3_hoffset", UnitSetup.MILLI_METER);

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

	public enum DetectorSetup {
		XH("xh"), XSTRIP("xstrip"), CCD("ccd");

		private static DetectorSetup[] availableDetectors;
		private static DetectorSetup connectedDetector;

		public static void setActiveDetectorSetup(DetectorSetup detectorSetup) {
			connectedDetector = detectorSetup;
			for (DetectorSetup detector : availableDetectors) {
				try {
					if (connectedDetector == detector) {
						detector.detectorScannable.connect();
					} else {
						detector.detectorScannable.disconnect();
					}
				} catch (DeviceException e) {
					logger.error("DeviceException when connecting / disconnecting detector "
							+ detector.detectorScannable.getName(), e);
				}
			}
		}

		public static DetectorSetup getActiveDetectorSetup() {
			if (connectedDetector == null) {
				return getAvailableDetectorSetups()[0];
			}
			return connectedDetector;
		}

		public static DetectorSetup[] getAvailableDetectorSetups() {
			if (availableDetectors == null) {
				getAvailableDetectors();
				if (availableDetectors.length == 0) {
					MessageDialog
					.openError(Display.getDefault().getActiveShell(), "Error",
							"Unable to find installed detector, please ensure the server configuration is setup correctly.");
				}
			}
			return availableDetectors;
		}

		/**
		 * Populate the availableDetectors and connectedDetector attributes
		 */
		private static void getAvailableDetectors() {
			availableDetectors = new DetectorSetup[0];
			for (DetectorSetup detector : DetectorSetup.values()) {
				Object detectorBean = Finder.getInstance().find(detector.getDetectorName());
				if (detectorBean != null && detectorBean instanceof StripDetector) {
					StripDetector stripdetector = (StripDetector) detectorBean;
					detector.setDetectorScannable(stripdetector);
					if (stripdetector.isConnected()) {
						connectedDetector = detector;
					}
					availableDetectors = (DetectorSetup[]) ArrayUtils.add(availableDetectors, detector);
				}
			}
		}

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

		public boolean isVoltageInRange(double value) {
			return (detectorScannable.getMinBias() <= value & value <= detectorScannable.getMaxBias());
		}

		/**
		 * Utility for other parts of the UI
		 * 
		 * @return Integer[]
		 */
		public Integer[] createArrayOfStrips() {
			int numberOfStrips = DetectorSetup.getActiveDetectorSetup().getDetectorScannable().getNumberChannels();
			Integer[] strips = new Integer[numberOfStrips];
			for (int i = 0; i < numberOfStrips; i++) {
				strips[i] = new Integer(i);
			}
			return strips;
		}

	}
}
