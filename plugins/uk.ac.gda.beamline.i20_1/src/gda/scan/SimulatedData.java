/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package gda.scan;

import gda.configuration.properties.LocalProperties;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.detector.NXDetectorData;
import gda.device.detector.StripDetector;
import gda.device.detector.XHDetector;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.datawriters.EdeDataConstants;
import gda.scan.ede.position.EdePositionType;

import java.io.File;

import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.Dataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.SRSLoader;

public class SimulatedData {

	private static final Logger logger = LoggerFactory.getLogger(SimulatedData.class);

	//	private static final String SIMULATED_DATA_FILE_PATH = "simulated_data.dat";

	private static final String SIMULATED_DATA_I0_DARK_FILE_PATH = "I0dark1.dat";
	private static final String SIMULATED_DATA_IT_DARK_FILE_PATH = "Itdark1.dat";
	private static final String SIMULATED_DATA_I0_RAW_FILE_PATH = "I01.dat";
	private static final String SIMULATED_DATA_IT_RAW_FILE_PATH = "It181.dat";

	private static final int MAX = 181;

	private static double[] simulatedEnergies;
	private static double[] simulatedI0_dark;
	private static double[] simulatedIt_dark;
	private static double[] simulatedI0_raw;
	private static double[][] simulatedIt_raw = new double[MAX][];

	static {
		try {
			String separator = File.separator;
			String filePath = LocalProperties.getConfigDir() + "servers" + separator + "main" + separator + "dummy" + separator;

			DataHolder simulatedSpectrumData = new SRSLoader(filePath + SIMULATED_DATA_I0_DARK_FILE_PATH).loadFile();
			simulatedI0_dark = ((DoubleDataset) simulatedSpectrumData.getDataset(1).cast(Dataset.FLOAT64)).getData();
			simulatedSpectrumData = new SRSLoader(filePath + SIMULATED_DATA_IT_DARK_FILE_PATH).loadFile();
			simulatedIt_dark = ((DoubleDataset) simulatedSpectrumData.getDataset(1).cast(Dataset.FLOAT64)).getData();
			simulatedSpectrumData = new SRSLoader(filePath + SIMULATED_DATA_I0_RAW_FILE_PATH).loadFile();
			simulatedI0_raw = ((DoubleDataset) simulatedSpectrumData.getDataset(1).cast(Dataset.FLOAT64)).getData();

			simulatedSpectrumData = new SRSLoader(filePath + SIMULATED_DATA_IT_RAW_FILE_PATH).loadFile();
			for (int i = 0; i < MAX; i++) {
				simulatedIt_raw[i] = ((DoubleDataset) simulatedSpectrumData.getDataset(i + 1).cast(Dataset.FLOAT64)).getData();
			}
		} catch (Exception e) {
			logger.error("Unable to load simulated Data", e);
		}
	}

	public static NexusTreeProvider[] readSimulatedDataFromFile(int lowFrame, int highFrame, StripDetector theDetector, EdePositionType positionType, EdeScanType scanType)  throws Exception {
		if (simulatedIt_raw == null) {
			throw new Exception("Simulated data not loaded");
		}
		simulatedEnergies = ((XHDetector) theDetector).getEnergyForChannels();
		int numberOfFrames = (highFrame + 1) - lowFrame;
		NexusTreeProvider[] nexusTreeProvider = new NexusTreeProvider[numberOfFrames];
		int startFrame = lowFrame % MAX;

		for(int i = 0; i < numberOfFrames; i++) {
			NXDetectorData thisFrame = new NXDetectorData(theDetector);
			thisFrame.addAxis(theDetector.getName(), EdeDataConstants.ENERGY_COLUMN_NAME, new int[] { XHDetector.NUMBER_ELEMENTS }, NexusFile.NX_FLOAT64, simulatedEnergies, 1, 1, "eV", false);
			double[] simulatedData = null;
			if (positionType == EdePositionType.OUTBEAM) {
				if (scanType == EdeScanType.LIGHT) {
					simulatedData = createCorrectedSimulatedData(simulatedI0_raw, theDetector);
				} else {
					simulatedData = createCorrectedSimulatedData(simulatedI0_dark, theDetector);
				}
			} else if(positionType == EdePositionType.INBEAM) {
				if (scanType == EdeScanType.LIGHT) {
					simulatedData = createCorrectedSimulatedData(simulatedIt_raw[startFrame + i], theDetector);
				} else {
					simulatedData = createCorrectedSimulatedData(simulatedIt_dark, theDetector);
				}
			} else {
				if (scanType == EdeScanType.LIGHT) {
					simulatedData = createCorrectedSimulatedData(simulatedIt_raw[startFrame + i], theDetector);
				} else {
					simulatedData = createCorrectedSimulatedData(simulatedIt_dark, theDetector);
				}
			}

			thisFrame.addData(theDetector.getName(), EdeDataConstants.DATA_COLUMN_NAME, new int[] { XHDetector.NUMBER_ELEMENTS }, NexusFile.NX_FLOAT64, simulatedData, "eV", 1);
			for (String name : thisFrame.getExtraNames()) {
				thisFrame.setPlottableValue(name, 0.0);
			}
			nexusTreeProvider[i] = thisFrame;
		}
		return nexusTreeProvider;
	}

	private static double[] createCorrectedSimulatedData(double[] simulatedData, StripDetector theDetector) {
		double[] correctedSimulatedData = new double[simulatedData.length];
		for (int i = 0; i < simulatedData.length; i++) {
			if (i >= theDetector.getLowerChannel() && i <= theDetector.getUpperChannel()) {
				correctedSimulatedData[i] = simulatedData[i];
			} else {
				correctedSimulatedData[i] = 0.0;
			}
		}
		return correctedSimulatedData;
	}

	public static int generatRandomPositiveNegitiveValue(int range) {
		int ii = (int) (Math.random() * (range * 2)) - range;
		return ii;
	}

	public static boolean isLoaded() {
		return simulatedIt_raw != null;
	}



	private SimulatedData() {}

}
