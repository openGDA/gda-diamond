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
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
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
import uk.ac.gda.ede.data.ClientConfig;

public class PowerCalulator {

	private static final Logger logger = LoggerFactory.getLogger(PowerCalulator.class);

	private double me2PitchAngle = 3.0;
	private double ringCurrent = 300.0;
	private String dataPath = DataPaths.getPowerCalculationDataPath();

	/** Lookup table of wiggler gap [mm] vs magnetic field strength [T]
	   { {gap0, field0}, {gap1, field1} ... }
	 */
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

	// Min and max values of wiggler horizontal slit size in power calculation files
	private static final double MIN_S1_HGAP = 0.8;
	private static final double MAX_S1_HGAP = 1.6;

	/** Name of the Be filter transmission file (filter thickness = 0.3mm) */
	public static final String BE_FILTER_FILE_NAME = "Be-0p3mm.dat";
	/** Thickness of Be filter (mm) */
	public static final double BE_FILTER_THICKNESS_MM = 0.3;

	/** Name of C-pyro filter transmission file (filter thickness = 1.0mm) */
	public static final String C_PYRO_FILTER_FILE_NAME = "C-pyro-1p0mm.dat";
	/** Thickness of C-pyro filter (mm) */
	public static final double C_PYRO_FILTER_THICKNESS_MM = 1.0;

	private static final double FLUX_TO_POWER = -1000*Utility.Q_ELECTRON; // = 1000*electron charge (1.60219e-16 C);

	private static final String RING_CURRENT = "300mA";
	private static final String SLIT_V_GAP = "0p12";
	private static final double CALCULATION_CURRENT = 300;

	/**
	 *
	 * @param gapValue wiggler gap [mm]
	 * @return magnetic field strength [T]
	 * @throws Exception
	 */
	public double getFieldValue(double gapValue) throws Exception {

		if (gapValue < GAP_FIELD[0][0]) {
			logger.warn("Wiggler gap {} mm is below limit of lookup table - using minimum value instead ({} mm)", gapValue, GAP_FIELD[0][0]);
			return GAP_FIELD[0][1];
		}

		// Find gap and field value in GAP_FIELD array where gap >= gapValue
		Optional<double[]> result = Arrays.stream(GAP_FIELD).filter(val -> val[0] >= gapValue).findFirst();
		if (!result.isPresent()) {
			throw new Exception("Unable to find field for gap value "+gapValue);
		}
		double[] gapAndField = result.get();
		int index = ArrayUtils.indexOf(GAP_FIELD, gapAndField);
		if (index == 0) {
			return GAP_FIELD[0][1];
		}
		if (index > 0) {
			double mid = 0.5*(GAP_FIELD[index-1][0] + GAP_FIELD[index][0]);
			if (gapValue >= mid) {
				return gapAndField[1];
			}
			return GAP_FIELD[index-1][1];
		}

		throw new Exception("Unable to find field for gap value "+gapValue);
	}

	public String getFieldName(double wigglerGap) throws Exception {
		return replaceDotWithP(Double.toString(getFieldValue(wigglerGap)), ClientConfig.UnitSetup.TESLA.getText());
	}

	public double getRoundedWigglerHGap(double gap) {
		double roundedGap = Math.max(gap, MIN_S1_HGAP);
		return Math.min(roundedGap, MAX_S1_HGAP);
	}

	public String getSlitHGapName(double s1HGap) {
		return replaceDotWithP(Double.toString(Math.round( s1HGap * 10.0 ) / 10.0), ClientConfig.UnitSetup.MILLI_RADIAN.getText());
	}

	public static String replaceDotWithP(String value, String suffix) {
		return value.replace('.', 'p') + suffix;
	}

	private class PowerFileNameFilter implements FilenameFilter {
		private final String pattern;

		PowerFileNameFilter(double wigglerGap, double s1HGap) throws Exception {
			String fieldfileNamePart = getFieldName(wigglerGap);
			String slitHSizeNamePart = getSlitHGapName(getRoundedWigglerHGap(s1HGap));
			pattern = fieldfileNamePart + "-"+ RING_CURRENT +"-" + SLIT_V_GAP + "x" + slitHSizeNamePart + ".dat";
			logger.debug("Finding files matching name pattern : {}", pattern);
		}

		@Override
		public boolean accept(File dir, String name) {
			try {
				return name.matches(pattern);
			} catch (Exception e) {
				return false;
			}
		}
	}

	/**
	 * Calculate the power for the given wiggler and slit gap
	 * using default set of filter (i.e. scannables returned {@link #getMirrorFilters()})
	 * @param wigglerGap (mm)
	 * @param s1HGap (mm)
	 * @return power (Watts)
	 * @throws Exception
	 */
	public double getPower(double wigglerGap, double s1HGap) throws Exception {
		return getPower(dataPath, wigglerGap, s1HGap, getMirrorFilterMap());
	}

	/**
	 *  Calculate the power for the given wiggler and slit gap and set of
	 *  filter values
	 * @param wigglerGap (mm)
	 * @param s1HGap (mm)
	 * @param filters key = scannable name, value = position
	 * @return power (Watts)
	 * @throws Exception
	 */
	public double getPower(double wigglerGap, double s1HGap,  Map<String, String> filters) throws Exception {
		return getPower(dataPath, wigglerGap, s1HGap, filters);
	}

	private double getPower(String parentFolder, double wigglerGap, double s1HGap, Map<String, String> filterMap) throws Exception {
		Dataset flux = calculateFluxVsEnergyForAllFilters(parentFolder, wigglerGap, s1HGap, filterMap);
		double result = doIntegration(flux);
		result = scalePower(result, ringCurrent);
		return result*FLUX_TO_POWER;
	}

	private void adjustTransmission(Dataset transmission, double oldThickness, double newThickness) {
		logger.info("Calculating transmission for filter thickness {} mm (original thickness = {} mm)", newThickness, oldThickness);
		int size = transmission.getShape()[0];
		for (int i = 0; i < size; i++) {
			double trans = Math.pow(transmission.getDouble(i, 1), newThickness / oldThickness);
			transmission.set(trans, i, 1);
		}
	}

	/**
	 * Calculate the energy resolved attenuated flux for the given combination of wiggler and slit gap
	 *
	 * @param parentFolder folder where the filter files are stored
	 * @param wigglerGap
	 * @param s1HGap
	 * @param filters map of filter values (key = filter/scannable name, value = position).
	 * @return Dataset of filtered flux (1 st column = energy, 2nd column = flux)
	 * @throws IllegalArgumentException
	 * @throws IOException
	 */
	public Dataset calculateFluxVsEnergyForAllFilters(String parentFolder, double wigglerGap, double s1HGap, Map<String, String> filters) throws IllegalArgumentException, IOException  {

		// Load wiggler power
		File wigglerFile = getEnergyFieldFile(parentFolder, wigglerGap, s1HGap);
		Dataset power = loadDatasetFromFile(wigglerFile);

		// Store the X-axis (energy) values
		int numVals = power.getShape()[0];
		Dataset xvals = power.getSlice(new int[] {0,0}, new int[] {numVals, 1}, null);

		// Apply Be filter to wiggler power
		File beFilterFile = new File(parentFolder, BE_FILTER_FILE_NAME);
		Dataset transmission = loadDatasetFromFile(beFilterFile);

		// Adjust the transmission if filter thickness is not 0.3mm
		if (Math.abs(BE_FILTER_THICKNESS_MM - 0.3) > 1e-4) {
			adjustTransmission(transmission, 0.3, BE_FILTER_THICKNESS_MM);
		}

		transmission = Maths.multiply(power, transmission);
		// Apply attenuators and mirrors to the transmission

		for (Entry<String, String> filter : filters.entrySet()) {
			logger.info("scannable = {}, position = {}", filter.getKey(), filter.getValue());
			if (Mirrors.INSTANCE.isPyroFilter(filter.getValue())) {
				Dataset cPyroTransmission = loadDatasetFromFile(new File(parentFolder, C_PYRO_FILTER_FILE_NAME));
				double filterThickness = Mirrors.INSTANCE.getThickness(filter.getValue());
				adjustTransmission(cPyroTransmission, C_PYRO_FILTER_THICKNESS_MM, filterThickness);
				transmission = Maths.multiply(transmission, cPyroTransmission);
			} else {
				String dataFileName = Mirrors.INSTANCE.getDataFileName(filter.getKey(), filter.getValue(), me2PitchAngle);
				if (!dataFileName.isEmpty()) {
					File file = new File(parentFolder, dataFileName);
					Dataset filterTransmission = loadDatasetFromFile(file);
					transmission = Maths.multiply(transmission, filterTransmission);

					if (ScannableSetup.ME2_STRIPE.getScannableName().equals(filter.getKey())) {
						transmission = Maths.multiply(transmission, filterTransmission);
					}
				}
			}
		}

		// Set the energy values (1st column) back to the original non-multiplied values
		transmission.setSlice(xvals, new int[] {0,0}, new int[] {numVals, 1}, null);
		return transmission;
	}

	/**
	 * Generate a list of ScannableSetup objects corresponding to the filters and mirrors
	 * that attenuate the beam
	 * @return list of filter and mirrors
	 */
	public List<ScannableSetup> getMirrorFilters() {
		List<ScannableSetup> mirrorFilters = new ArrayList<>();
		if (AlignmentParametersModel.INSTANCE.isUseAtn45()) {
			mirrorFilters.add(ScannableSetup.ATN4);
			mirrorFilters.add(ScannableSetup.ATN5);
		} else {
			mirrorFilters.add(ScannableSetup.ATN1);
			mirrorFilters.add(ScannableSetup.ATN2);
			mirrorFilters.add(ScannableSetup.ATN3);
		}
		mirrorFilters.add(ScannableSetup.ME1_STRIPE);
		mirrorFilters.add(ScannableSetup.ME2_STRIPE);
		return mirrorFilters;
	}

	/**
	 * Generate a map of filter values from current positions of 'mirror filter' scannables
	 * (i.e. scannables returned by {@link #getMirrorFilters()});
	 * @return map of filter values : key = scannable name, value = position (as a string)
	 * @throws Exception
	 */
	public Map<String, String> getMirrorFilterMap() throws Exception {
		Map<String, String> filterMap = new LinkedHashMap<>();
		for(ScannableSetup mirrorFilters : getMirrorFilters()) {
			filterMap.put(mirrorFilters.getScannable().getName(), mirrorFilters.getScannable().getPosition().toString());
		}
		return filterMap;
	}

	private double doIntegration(Dataset values) {
		int size = values.getShape()[0];
		double[] xvals = (double[]) values.getSlice(new int[] {0, 0}, new int[] {size, 1}, null).getBuffer();
		double[] yvals = (double[]) values.getSlice(new int[] {0, 1}, new int[] {size, 2}, null).getBuffer();
		return Simpson.simpsonNE(xvals, yvals);
	}

	private double scalePower(double result, double ringCurrent) {
		return (result * ringCurrent) / CALCULATION_CURRENT;
	}

	public Dataset loadDatasetFromFile(File dataFile) throws FileNotFoundException, IOException {
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

	private void checkFile(File datafile) throws FileNotFoundException {
		if (!datafile.exists() || !datafile.canRead()) {
			throw new FileNotFoundException("Cannot read data from "+datafile.getAbsolutePath());
		}
	}

	public File getEnergyFieldFile(String parentFolder, double wigglerGap, double s1HGap) throws FileNotFoundException, IllegalArgumentException {
		File folder = new File(parentFolder);
		if (!folder.exists() || !folder.canRead()) {
			throw new FileNotFoundException("Cannot read filter file from directory "+parentFolder);
		}
		try {
			String[] matchedFileNames = folder.list(new PowerFileNameFilter(wigglerGap, s1HGap));
			if (matchedFileNames.length > 0) {
				return new File(parentFolder, matchedFileNames[0]);
			}
		} catch(Exception e) {
			throw new FileNotFoundException("Problem getting energy field file - "+e.getMessage());
		}
		throw new FileNotFoundException("No filter files found in "+parentFolder);
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

	public enum Mirrors {
		INSTANCE;

		private static final String EMPTY = "empty";
		private static final String ME1_ANGLE = "3.0";

		private Mirrors() {
		}


		public String getDataFileName(String scnName, String scnPos, double me2Pitch) {
			if (isAttenuator(scnName)) {
				return getAttenuatorFileName(scnPos);
			} else {
				FilterMirrorElementType elementName = FilterMirrorElementType.findByName(scnPos);
				if (elementName != null) {
					if (scnName.equals(ScannableSetup.ME1_STRIPE.getScannableName())) {
						return elementName.getSymbol() + "-" + replaceDotWithP(ME1_ANGLE, ClientConfig.UnitSetup.MILLI_RADIAN.getText()) + ".dat";
					} else if (scnName.equals(ScannableSetup.ME2_STRIPE.getScannableName())) {
						try {
							double roundedAngle = findNearest(me2Pitch);
							return elementName.getSymbol() + "-" + replaceDotWithP(Double.toString(roundedAngle), ClientConfig.UnitSetup.MILLI_RADIAN.getText()) + ".dat";
						} catch (Exception e) {
							return "";
						}
					}
				}
			}
			return "";
		}

		private String getAttenuatorFileName(String scannablePosition) {
			String[] nameParts = getNameParts(scannablePosition);
			if (nameParts.length > 0) {
				FilterMirrorElementType elementName = FilterMirrorElementType.valueOf(nameParts[0]);
				if (elementName != null && nameParts.length == 3) {
					return elementName.getSymbol() + "-" + replaceDotWithP(nameParts[1], nameParts[2]) + ".dat";
				}
			}
			return "";
		}

		public boolean isAttenuator(String scannableName) {
			return scannableName.startsWith("atn");
		}

		public boolean isPyroFilter(String scannablePosition) {
			String[] nameParts = getNameParts(scannablePosition);
			return nameParts.length > 0 && nameParts[0].contentEquals(FilterMirrorElementType.pC.name());
		}

		public double getThickness(String scannablePosition) {
			String[] nameParts = getNameParts(scannablePosition);
			if (nameParts.length > 1) {
				return Double.parseDouble(nameParts[1]);
			}
			return 0;
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
			final String[] emptyString = new String[] {};

			if (name.toLowerCase().contains(EMPTY)) {
				return emptyString;
			}

			Pattern pattern = Pattern.compile("(\\w+)\\s*(\\d+\\.\\d{1,2})\\s*(\\w+).*");
			Matcher matcher = pattern.matcher(name);
			String[] nameParts = new String[3];
			if (matcher.find()) {
				if (matcher.groupCount() < 3) {
					return emptyString;
				}
				nameParts[0] = matcher.group(1); // Element name
				nameParts[1] = matcher.group(2); // Value
				nameParts[2] = matcher.group(3); // Unit
				return nameParts;
			}
			return emptyString;
		}
	}

	public double getMe2PitchAngle() {
		return me2PitchAngle;
	}

	public void setMe2PitchAngle(double me2PitchAngle) {
		this.me2PitchAngle = me2PitchAngle;
	}

	public double getRingCurrent() {
		return ringCurrent;
	}

	public void setRingCurrent(double ringCurrent) {
		this.ringCurrent = ringCurrent;
	}

	public String getDataPath() {
		return dataPath;
	}

	public void setDataPath(String dataPath) {
		this.dataPath = dataPath;
	}
}
