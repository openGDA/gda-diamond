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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.Maths;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.analysis.numerical.integration.Simpson;
import gda.analysis.numerical.utilities.Utility;
import gda.device.DeviceException;
import gda.device.Scannable;

public class PowerCalulator {

	private static final Logger logger = LoggerFactory.getLogger(PowerCalulator.class);

	private PowerCalulator() {}

	// This needs be in sorted
	private static final double[][] GAP_FIELD = {
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

	private static final ScannableSetup[] MIRROR_FILTERS = new ScannableSetup[] { ScannableSetup.ATN1, ScannableSetup.ATN2, ScannableSetup.ATN3,
			ScannableSetup.ME1_STRIPE, ScannableSetup.ME2_STRIPE };

	/** Name of the Be filter transmission file (filter thickness = 0.3mm) */
	public static final String BE_FILTER_FILE_NAME = "Be-0p3mm.dat";

	private static final double FLUX_TO_POWER = -1000*Utility.Q_ELECTRON; // 1000*electron charge (1.60219e-16 C);

	/** Thickness of Be filter (mm) */
	private static final double beFilterThickness = 0.3;

	private static final String RING_CURRENT = "300mA";
	private static final String SLIT_V_GAP = "0p12";
	private static final double CALCULATION_CURRENT = 300;

	public static double getFieldValue(double gapValue) throws Exception {

		// Find gap and field value in GAP_FIELD array where gap >= gapValue
		Optional<double[]> result = Arrays.stream(GAP_FIELD).filter(val -> val[0] >= gapValue).findFirst();
		if (!result.isPresent()) {
			throw new Exception("Unable to find field string");
		}
		double[] gapAndField = result.get();
		if (Math.abs(gapAndField[0] - gapValue) < 1e-6) {
			return gapAndField[1];
		}

		int index = ArrayUtils.indexOf(GAP_FIELD, gapAndField);
		if (index > 0) {
			double mid = 0.5*(GAP_FIELD[index-1][0] + GAP_FIELD[index][0]);
			if (gapValue >= mid) {
				return gapAndField[1];
			}
			return GAP_FIELD[index-1][1];
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

	public static double getPower(double wigglerGap, double s1HGap, double ringCurrent) throws Exception {
		return getPower(DataPaths.getPowerCalculationDataPath(), wigglerGap, s1HGap, ringCurrent);
	}

	public static double getPower(String parentFolder, double wigglerGap, double s1HGap, double ringCurrent) throws Exception {
		Dataset flux = calculateFluxVsEnergyForAllFilters(parentFolder, wigglerGap, s1HGap);
		double result = doIntegration(flux);
		result = scalePower(result, ringCurrent);
		return result*FLUX_TO_POWER;
	}

	public static Dataset calculateFluxVsEnergyForAllFilters(String parentFolder, double wigglerGap, double s1HGap)
			throws FileNotFoundException, IOException, Exception {

		// Load wiggler power
		File wigglerFile = getEnergyFieldFile(wigglerGap, s1HGap, parentFolder);
		Dataset power = loadDatasetFromFile(wigglerFile);

		// Store the X-axis (energy) values
		int numVals = power.getShape()[0];
		Dataset xvals = power.getSlice(new int[] {0,0}, new int[] {numVals, 1}, null);

		// Apply Be filter to wiggler power
		File beFilterFile = new File(parentFolder, BE_FILTER_FILE_NAME);
		Dataset transmission = loadDatasetFromFile(beFilterFile);

		// Adjust the transmission if filter thickness is not 0.3mm
		if (Math.abs(beFilterThickness - 0.3) > 1e-4) {
			int size = transmission.getShape()[0];
			for (int i = 0; i < size; i++) {
				double trans = Math.pow(transmission.getDouble(i, 1), beFilterThickness / 0.3);
				transmission.set(trans, i, 1);
			}
		}

		transmission = Maths.multiply(power, transmission);

		// Apply attenuators and mirrors to the transmission
		for (ScannableSetup mirrorFilterScannable : MIRROR_FILTERS) {
			Scannable scannable = mirrorFilterScannable.getScannable();
			logger.info("scannable = {}, position = {}", scannable, scannable.getPosition());
			String dataFileName = Mirrors.INSTANCE.getDataFileName(scannable);
			if (dataFileName != null) {
				File file = new File(parentFolder, dataFileName);
				Dataset filterTransmission = loadDatasetFromFile(file);
				transmission = Maths.multiply(transmission, filterTransmission);

				if (ScannableSetup.ME2_STRIPE.getScannableName().equals(scannable.getName())) {
					transmission = Maths.multiply(transmission, filterTransmission);
				}
			}
		}

		// Set the energy values (1st column) back to the original non-multiplied values
		transmission.setSlice(xvals, new int[] {0,0}, new int[] {numVals, 1}, null);
		return transmission;
	}

	private static double doIntegration(Dataset values) {
		int size = values.getShape()[0];
		double[] xvals = (double[]) values.getSlice(new int[] {0, 0}, new int[] {size, 1}, null).getBuffer();
		double[] yvals = (double[]) values.getSlice(new int[] {0, 1}, new int[] {size, 2}, null).getBuffer();
		return Simpson.simpsonNE(xvals, yvals);
	}

	private static double scalePower(double result, double ringCurrent) {
		return (result * ringCurrent) / CALCULATION_CURRENT;
	}

	public static Dataset loadDatasetFromFile(File dataFile) throws FileNotFoundException, IOException {
		checkFile(dataFile);
		try (BufferedReader reader = new BufferedReader(new FileReader(dataFile))) {
			logger.info("Loading flux from {}", dataFile.getName());
			String line = reader.readLine();
			while (line.trim().startsWith("#")) {
				line = reader.readLine();
			}
			List<double[]> values = new ArrayList<>();
			while (line != null) {
				String[] sLine = line.trim().split("\\s");
				double[] lineVals = new double[sLine.length];
				for(int i=0; i<sLine.length; i++) {
					lineVals[i] = Double.parseDouble(sLine[i]);
				}
				values.add(lineVals);
				line = reader.readLine();
			}
			return DatasetFactory.createFromList(values);
		}
	}

	private static void checkFile(File datafile) throws FileNotFoundException {
		if (!datafile.exists() || !datafile.canRead()) {
			throw new FileNotFoundException("Cannot read data from "+datafile.getAbsolutePath());
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
			return Stream.of(FilterMirrorElementType.values())
					.filter(enumVal -> enumVal.name().equals(value))
					.findFirst()
					.orElse(null);
		}
	}

	public static enum Mirrors {
		INSTANCE;

		private static final String EMPTY = "empty";
		private static final String ME1_ANGLE = "3.0";

		private Mirrors() {
		}

		public String getDataFileName(Scannable scannable) {
			String value = null;
			try {
				value = (String) scannable.getPosition();
			} catch (DeviceException e) {
				return null;
			}
			if (scannable.getName().startsWith("atn")) {
				String[] nameParts = getNameParts(value);
				if (nameParts != null) {
					FilterMirrorElementType elementName = FilterMirrorElementType.valueOf(nameParts[0]);
					if (elementName != null) {
						return elementName.getSymbol() + "-" + replaceDotWithP(nameParts[1], nameParts[2]) + ".dat";
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
			if (name.toLowerCase().contains(EMPTY)) {
				return null;
			}

			Pattern pattern = Pattern.compile("(\\w+)\\s*(\\d+\\.\\d{1,2})\\s*(\\w+).*");
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
