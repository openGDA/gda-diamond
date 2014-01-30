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
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.position.EdePositionType;

import java.util.Arrays;

import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;

public class SimulatedData {

	private static final Logger logger = LoggerFactory.getLogger(SimulatedData.class);

	private static final String SIMULATED_DATA_FILE_PATH = "/simulated_data.dat";

	private static double[] simulatedEnergies;
	private static double[] simulatedI0_dark;
	private static double[] simulatedIt_dark;
	private static double[] simulatedI0_raw;
	private static double[] simulatedIt_raw;

	static {
		try {
			final DataHolder simulatedSpectrumData = LoaderFactory.getData(LocalProperties.getVarDir() + SIMULATED_DATA_FILE_PATH);
			simulatedEnergies = ((DoubleDataset) simulatedSpectrumData.getLazyDataset(EdeExperiment.STRIP_COLUMN_NAME)).getData();
			simulatedI0_dark = ((DoubleDataset) simulatedSpectrumData.getLazyDataset(EdeExperiment.I0_DARK_COLUMN_NAME)).getData();
			simulatedIt_dark = ((DoubleDataset) simulatedSpectrumData.getLazyDataset(EdeExperiment.IT_DARK_COLUMN_NAME)).getData();
			simulatedI0_raw = ((DoubleDataset) simulatedSpectrumData.getLazyDataset(EdeExperiment.I0_RAW_COLUMN_NAME)).getData();
			simulatedIt_raw = ((DoubleDataset) simulatedSpectrumData.getLazyDataset(EdeExperiment.IT_RAW_COLUMN_NAME)).getData();
		} catch (Exception e) {
			logger.error("Unable to load simulated Data", e);
		}
	}

	public static NexusTreeProvider[] readSimulatedDataFromFile(int lowFrame, int highFrame, StripDetector theDetector, EdePositionType positionType, EdeScanType scanType)  throws Exception {
		if (simulatedEnergies == null) {
			throw new Exception("Simulated data not loaded");
		}
		int numberOfFrames = (highFrame + 1) - lowFrame;
		NexusTreeProvider[] nexusTreeProvider = new NexusTreeProvider[numberOfFrames];

		for(int i = 0; i < numberOfFrames; i++) {
			NXDetectorData thisFrame = new NXDetectorData(theDetector);
			thisFrame.addAxis(theDetector.getName(), EdeExperiment.ENERGY_COLUMN_NAME, new int[] { XHDetector.NUMBER_ELEMENTS }, NexusFile.NX_FLOAT64, simulatedEnergies, 1, 1, "eV", false);
			double[] simulatedData = null;
			if (positionType == EdePositionType.OUTBEAM) {
				if (scanType == EdeScanType.LIGHT) {
					simulatedData = Arrays.copyOf(simulatedI0_raw, simulatedI0_raw.length);
				} else {
					simulatedData = Arrays.copyOf(simulatedI0_dark, simulatedI0_dark.length);
				}
			} else if(positionType == EdePositionType.INBEAM) {
				if (scanType == EdeScanType.LIGHT) {
					simulatedData = Arrays.copyOf(simulatedIt_raw, simulatedIt_raw.length);
				} else {
					simulatedData = Arrays.copyOf(simulatedIt_dark, simulatedIt_dark.length);
				}

			} else {
				// TODO Add Iref
			}
			addNoise(simulatedData);
			thisFrame.addData(theDetector.getName(), EdeExperiment.DATA_COLUMN_NAME, new int[] { XHDetector.NUMBER_ELEMENTS }, NexusFile.NX_FLOAT64, simulatedData, "eV", 1);
			for (String name : thisFrame.getExtraNames()) {
				thisFrame.setPlottableValue(name, 0.0);
			}
			nexusTreeProvider[i] = thisFrame;
		}
		return nexusTreeProvider;
	}

	private static void addNoise(double[] simulatedData) {
		for (int i=0; i < simulatedData.length; i++) {
			simulatedData[i] = simulatedData[i] + generatRandomPositiveNegitiveValue(100000);
		}
	}

	public static int generatRandomPositiveNegitiveValue(int range) {
		int ii = (int) (Math.random() * (range * 2)) - range;
		return ii;
	}

	private SimulatedData() {}

}
