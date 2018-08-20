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


import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FilenameFilter;
import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import gda.analysis.datastructure.DataVector;
import gda.analysis.numerical.integration.Integrate;
import gda.device.DeviceException;
import gda.device.Scannable;

public class PowerCalulator {

	private PowerCalulator() {}

	public static final String REF_DATA_PATH = DataPaths.getPowerCalculationDataPath();
	// This needs be in sorted
	public static final double[][] GAP_FIELD = {
		{18.5,1.3},
		{20.0,1.2},
		{21.9,1.1},
		{23.9,1.0},
		{26.0,0.9},
		{30.0,0.74},
		{40.0,0.48},
		{50.0,0.33},
		{250.0,0.33} // This is to avoid numbers over 50
	};

	public static final String BE_FILTER_FILE_NAME = "Be-0p3mm.dat";

	private static final String RING_CURRENT = "300mA";
	private static final String SLIT_V_GAP = "0p12";
	private static final double CALCULATION_CURRENT = 300;

	public static double getFieldValue(double gapValue) throws Exception {
		for (int i = 0; i < GAP_FIELD.length; i++) {
			if (GAP_FIELD[i][0] >= gapValue) {
				if (GAP_FIELD[i][0] == gapValue) {
					return GAP_FIELD[i][1];
				}
				if (i > 0) {
					double mid = (GAP_FIELD[i-1][0] + GAP_FIELD[i][0]) / 2;
					if (gapValue >= mid) {
						return GAP_FIELD[i][1];
					}
					return GAP_FIELD[i-1][1];
				}
			}
		}
		throw new Exception("Unable to find field string");
	}

	public static String getFieldName(double wigglerGap) throws Exception {
		return replaceDotWithP(Double.toString(getFieldValue(wigglerGap)), ClientConfig.UnitSetup.TESLA.getText());
	}

	public static String getSlitHGapName(double s1HGap) {
		return replaceDotWithP(Double.toString(Math.round( s1HGap * 10.0 ) / 10.0), ClientConfig.UnitSetup.MILLI_RADIAN.getText());
	}

	public static String replaceDotWithP(String value, String suffix) {
		return value.replace('.', 'p') + suffix;
	}

	private static class PowerFileNameFilter implements FilenameFilter {
		private final double wigglerGap;
		private final double s1HGap;
		PowerFileNameFilter(double wigglerGap, double s1HGap){
			this.wigglerGap = wigglerGap;
			this.s1HGap = s1HGap;
		}
		@Override
		public boolean accept(File dir, String name) {
			try {
				String fieldfileNamePart = getFieldName(wigglerGap);
				String slitHSizeNamePart = getSlitHGapName(s1HGap);
				return name.matches(fieldfileNamePart + "-"+ RING_CURRENT +"-" + SLIT_V_GAP + "x" + slitHSizeNamePart + ".dat");
			} catch (Exception e) {
				return false;
			}
		}
	}

	public static double getPower(String parentFolder, double wigglerGap, double s1HGap, double ringCurrent) throws Exception {
		double[] values = new double[100000 / 50];
		calculateFluxVsEnergyForAllFilters(parentFolder, wigglerGap, s1HGap, values);
		convertFluxToPower(values);
		double result = doIntegration(values);
		result = scalePower(result, ringCurrent);
		return result;
	}

	private static void calculateFluxVsEnergyForAllFilters(String parentFolder, double wigglerGap, double s1HGap, double[] values)
			throws FileNotFoundException, IOException, Exception {
		File wigglerFile = getEnergyFieldFile(wigglerGap, s1HGap, parentFolder);
		File beFilterFile = new File(parentFolder, BE_FILTER_FILE_NAME);
		if (!beFilterFile.exists()) {
			throw new FileNotFoundException();
		}
		loadAndCalculateFlux(wigglerFile, values);
		loadAndCalculateFlux(beFilterFile, values);
		for (ScannableSetup mirrorFilterScannable : Mirrors.INSTANCE.mirrorFilters) {
			Scannable scannable = mirrorFilterScannable.getScannable();
			String dataFileName = Mirrors.INSTANCE.getDataFileName(scannable);
			if (dataFileName != null) {
				File file = new File(parentFolder, dataFileName);
				if (!file.exists()) {
					throw new FileNotFoundException(file.getAbsolutePath());
				}
				loadAndCalculateFlux(file, values);
				if (ScannableSetup.ME2_STRIPE.getScannableName().equals(scannable.getName())) {
					loadAndCalculateFlux(file, values); // Since ME2 is double mirror it is added twice
				}
			}
		}
	}

	private static double doIntegration(double[] values) {
		int x = 50;
		double range = 100000;
		int size = values.length;
		double step = range / size;
		DataVector y1 = new DataVector(size);
		DataVector x1 = new DataVector(size);
		for (int i = 0; i < size; i++) {
			x1.set(i, (double) x);
			y1.set(i, values[i]);
			x += step;
		}
		return Integrate.simpson(x1, y1);
	}

	private static double scalePower(double result, double ringCurrent) {
		return (result * ringCurrent) / CALCULATION_CURRENT;
	}

	private static final double FLUX_TO_POWER = Double.parseDouble("1.60219e-16");
	private static void convertFluxToPower(double[] values) {
		for (int i = 0; i < values.length; i++) {
			values[i] = values[i] * FLUX_TO_POWER;
		}
	}

	private static void loadAndCalculateFlux(File dataFile, double[] values) throws FileNotFoundException, IOException {
		BufferedReader reader = new BufferedReader(new FileReader(dataFile));
		try {
			String line = reader.readLine();
			while (line.trim().startsWith("#")) {
				line = reader.readLine();
			}
			int i = 0;
			while (line != null) {
				String[] sLine = line.trim().split("\\s");
				if (values[i] != 0) {
					values[i] = values[i] * Double.parseDouble(sLine[1]);
				} else {
					values[i] = Double.parseDouble(sLine[1]);
				}
				i++;
				line = reader.readLine();
			}
		} finally {
			reader.close();
		}
	}

	public static File getEnergyFieldFile(double wigglerGap, double s1HGap, String parentFolder) throws FileNotFoundException {
		File folder = new File(parentFolder);
		if (!folder.exists() || !folder.canRead()) {
			throw new FileNotFoundException();
		}
		String[] matchedFileNames = folder.list(new PowerFileNameFilter(wigglerGap, s1HGap));
		if (matchedFileNames.length > 0) {
			return new File(parentFolder, matchedFileNames[0]);
		}
		throw new FileNotFoundException();
	}

	public enum FilterMirrorElementType {
		pC("C-pyro"),
		Silicon("Si"),
		Rhodium("Rh"),
		SiC("SiC"),
		Platinum("Pt");

		private final String symbol;

		private FilterMirrorElementType(String symbol) {
			this.symbol = symbol;
		}

		public String getSymbol() {
			return symbol;
		}

		public static FilterMirrorElementType findByName(String value) {
			for (FilterMirrorElementType elementType : FilterMirrorElementType.values()) {
				if (elementType.name().equals(value)) {
					return elementType;
				}
			}
			return null;
		}
	}


	public static enum Mirrors {
		INSTANCE;

		public static final String EMPTY = "Empty";
		public static final String ME1_ANGLE = "3.0";
		private final ScannableSetup[] mirrorFilters = new ScannableSetup[5];

		private Mirrors() {
			mirrorFilters[0] = ScannableSetup.ATN1;
			mirrorFilters[1] = ScannableSetup.ATN2;
			mirrorFilters[2] = ScannableSetup.ATN3;
			mirrorFilters[3] = ScannableSetup.ME1_STRIPE;
			mirrorFilters[4] = ScannableSetup.ME2_STRIPE;
		}

		public String getDataFileName(Scannable scannable) {
			String value = null;
			try {
				value = (String) scannable.getPosition();
			} catch (DeviceException e) {
				return null;
			}
			if (scannable.getName().startsWith("atn")) {
				if (!value.equals("Empty")) {
					String[] nameParts = getNameParts(value);
					if (nameParts != null) {
						FilterMirrorElementType elementName = FilterMirrorElementType.findByName(nameParts[0]);
						if (elementName != null) {
							return elementName.getSymbol() + "-" + replaceDotWithP(nameParts[1], nameParts[2]) + ".dat";
						}
					}
				}
			} else {
				FilterMirrorElementType elementName = FilterMirrorElementType.findByName(value);
				if (elementName != null) {
					if (scannable.getName().equals(ScannableSetup.ME1_STRIPE.getScannableName())) {
						return elementName.getSymbol() + "-" + replaceDotWithP(ME1_ANGLE, ClientConfig.UnitSetup.MILLI_RADIAN.getText()) + ".dat";
					} else if (scannable.getName().equals(ScannableSetup.ME2_STRIPE.getScannableName())) {
						try {
							double me2PatchAngle = findNearest((double) ScannableSetup.ME2_PITCH_ANGLE.getScannable().getPosition());
							return elementName.getSymbol() + "-" + replaceDotWithP(Double.toString(me2PatchAngle), ClientConfig.UnitSetup.MILLI_RADIAN.getText()) + ".dat";
						} catch (Exception e) {
							return null;
						}
					}
				}
			}
			return null;
		}

		public double findNearest(double value) {
			double me2PatchAngle;
			me2PatchAngle = Math.round(value * 1000.0 ) / 1000.0;
			double modValue = (me2PatchAngle * 100.0) % 25.0;
			int wholeValue = (int) ((me2PatchAngle * 1000.0) / 1000.0);
			if (modValue == 0.0) {
				return me2PatchAngle;
			}
			for (double i = 0; i < 100; i = i + 25) {
				if (modValue > i & modValue < i + 25) {
					if (modValue >= (i + 25) / 2) {
						return wholeValue + (i + 25) / 100;
					}
					return wholeValue + (i) / 100;
				}
			}
			return me2PatchAngle;
		}

		public String[] getNameParts(String name) {
			Pattern pattern = Pattern.compile("(\\w+)\\s*(\\d+\\.\\d{1,2})(\\w+)");
			Matcher matcher = pattern.matcher(name);
			String[] nameParts = new String[3];
			if (matcher.find()) {
				if (matcher.groupCount() < 3) {
					return null;
				}
				nameParts[0] = matcher.group(1); // Element name
				nameParts[1] = matcher.group(2); // Value
				nameParts[2] = matcher.group(3); // Unit
				return nameParts;
			}
			return null;
		}
	}
}
