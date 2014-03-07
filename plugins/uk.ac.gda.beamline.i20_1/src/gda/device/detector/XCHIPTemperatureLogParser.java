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

package gda.device.detector;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

import org.apache.commons.lang.ArrayUtils;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IDataset;
import uk.ac.diamond.scisoft.analysis.dataset.LongDataset;

public class XCHIPTemperatureLogParser {

	private final String tempLogFilename;
	private long[][] times;
	private double[][] temps;

	public XCHIPTemperatureLogParser(String tempLogFilename) {
		this.tempLogFilename = tempLogFilename;
	}

	public IDataset[][] getTemperatures() {

		try {
			BufferedReader br = new BufferedReader(new FileReader(tempLogFilename));

			times = new long[4][];
			temps = new double[4][];

			String sCurrentLine;
			while ((sCurrentLine = br.readLine()) != null) {
				parseLine(sCurrentLine);
			}

			br.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			return null;
		} catch (IOException e) {
			// TODO Auto-generated catch block
			return null;
		}

		LongDataset[] timeDatasets = new LongDataset[4];
		DoubleDataset[] temperatureDatasets = new DoubleDataset[4];

		for (int i = 0; i < 4; i++) {
			timeDatasets[i] = new LongDataset(times[i]);
			temperatureDatasets[i] = new DoubleDataset(temps[i]);
		}

		return new IDataset[][] { timeDatasets, temperatureDatasets };
	}

	private void parseLine(String sCurrentLine) {
		// 1392715507 ch0=38.25

		String[] parts = sCurrentLine.split("\\s+");
		long time = Long.parseLong(parts[0]);
		parts = parts[1].split("=");
		int sensor = Integer.parseInt(parts[0].substring(2)); // chX
		double temp = Double.parseDouble(parts[1]);

		times[sensor] = ArrayUtils.add(times[sensor], time);
		temps[sensor] = ArrayUtils.add(temps[sensor], temp);

	}

}
