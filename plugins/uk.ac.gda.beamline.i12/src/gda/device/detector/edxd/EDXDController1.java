/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.device.detector.edxd;

import java.io.IOException;

import gda.analysis.DataSet;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.detector.NXDetectorData;
import gda.device.epicsdevice.ReturnType;

import org.nexusformat.NexusFile;

/**
 * This class describes the EDXD detector on I12, it is made up of 24 subdetectors
 */
public class EDXDController1 extends EDXDController {

	@Override
	public NexusTreeProvider readout() throws DeviceException {

		// If there was a problem when acquiring the data
		verifyData();

		NXDetectorData data = new NXDetectorData(this);

		// Quick integrator to calculate the total counts and values for the dead_time stats
		int totalCounts = 0;
		double dead_time_max = -Double.MAX_VALUE;
		double dead_time_min = Double.MAX_VALUE;
		double dead_time_mean = 0.0;
		int dead_time_mean_elements = 0;
		double live_time_mean = 0.0;

		// one final thing for the use of plotting
		DataSet[] plotds = new DataSet[subDetectors.size()];
		
		int nsubdets = subDetectors.size();
		Integer nbins = (Integer) xmap.getValue(ReturnType.DBR_NATIVE, "GETNBINS", "");
		double[][] all_data = new double [nsubdets][nbins];
		double[][] all_energy = new double [nsubdets][];
		double[][] all_q = new double [nsubdets][];
		double[][] all_elive_time = new double [nsubdets][];
		double[][] all_tlive_time = new double [nsubdets][];
		double[][] all_real_time = new double [nsubdets][];
		int[][] all_events = new int [nsubdets][];
		double[][] all_input_count_rate = new double [nsubdets][];
		double[][] all_output_count_rate = new double [nsubdets][];
		double[][] all_dead_time = new double [nsubdets][];
		double[][] all_dead_time_percent = new double [nsubdets][];

		// populate the data item from the elements
		for (int i = 0; i < subDetectors.size(); i++) {

			EDXDElement det = subDetectors.get(i);

			// add the data
			plotds[i] = new DataSet(det.getName(), det.readoutDoubles());

			totalCounts += plotds[i].sum();
			
			all_data[i] = det.readoutDoubles();
//			data.addData(det.getName(), det.getDataDimensions(), det.getDataType(), plotds[i].doubleArray(), "counts",
//					1);

			// add the energy Axis
//			double[] energy = det.getEnergyBins();
//			data.addAxis(det.getName(), "edxd_energy_approx", new int[] { energy.length }, NexusFile.NX_FLOAT64,
//					energy, 2, 2, "keV", false);

			all_energy[i] = new double[] {};
			all_energy[i] = det.getEnergyBins();
			
			// add the q Axis
//			double[] q = det.getQMapping();
//			data.addAxis(det.getName(), "edxd_q", new int[] { energy.length }, NexusFile.NX_FLOAT64, q, 2, 1, "units",
//					false);
			
			all_q[i] = new double[] {};
			all_q[i] = det.getQMapping();

//			double[] elive_time = { det.getEnergyLiveTime() };
//			data.addElement(det.getName(), "edxd_energy_live_time", new int[] { elive_time.length },
//					NexusFile.NX_FLOAT64, elive_time, "seconds", true);
			
			all_elive_time[i] = new double[] { det.getEnergyLiveTime() };

			double[] tlive_time = { det.getTriggerLiveTime() };
//			data.addElement(det.getName(), "edxd_trigger_live_time", new int[] { tlive_time.length },
//					NexusFile.NX_FLOAT64, tlive_time, "seconds", true);

			all_tlive_time[i] = new double[] { det.getTriggerLiveTime() };
			
			double[] real_time = { det.getRealTime() };
//			data.addElement(det.getName(), "edxd_real_time", new int[] { real_time.length }, NexusFile.NX_FLOAT64,
//					real_time, "seconds", true);
			
			all_real_time[i] = new double[] { det.getRealTime() };

//			int[] events = { det.getEvents() };
//			data.addElement(det.getName(), "edxd_events", new int[] { events.length }, NexusFile.NX_INT32, events,
//					"counts", true);

			all_events[i] = new int[] { det.getEvents() };
			
			double[] input_count_rate = { det.getInputCountRate() };
//			data.addElement(det.getName(), "edxd_input_count_rate", new int[] { input_count_rate.length },
//					NexusFile.NX_FLOAT64, input_count_rate, "counts/second", true);
			
			all_input_count_rate[i] = new double[] { det.getInputCountRate() };

			double[] output_count_rate = { det.getOutputCountRate() };
//			data.addElement(det.getName(), "edxd_output_count_rate", new int[] { output_count_rate.length },
//					NexusFile.NX_FLOAT64, output_count_rate, "counts/second", true);
			
			all_output_count_rate[i] = new double[] { det.getOutputCountRate() };

			// simple deadtime calculation for now, which is simply based on the 2 rates
			double[] dead_time = { (1.0 - (output_count_rate[0] / input_count_rate[0])) * real_time[0] };
//			data.addElement(det.getName(), "edxd_dead_time", new int[] { dead_time.length }, NexusFile.NX_FLOAT64,
//					dead_time, "seconds", true);
			
			all_dead_time[i] = new double[] {};
			all_dead_time[i] = dead_time;
			
			// simple deadtime calculation for now, which is simply based on the 2 rates
			double[] dead_time_percent = { (1.0 - (output_count_rate[0] / input_count_rate[0])) * 100.0 };
//			data.addElement(det.getName(), "edxd_dead_time_percent", new int[] { dead_time_percent.length }, NexusFile.NX_FLOAT64,
//					dead_time_percent, "percent", true);
			
			all_dead_time_percent[i] = new double[] {};
			all_dead_time_percent[i] = dead_time_percent;

			// now calculate the deadtime statistics
			if (dead_time[0] > dead_time_max)
				dead_time_max = dead_time[0];
			if (dead_time[0] < dead_time_min)
				dead_time_min = dead_time[0];
			dead_time_mean += dead_time[0];
			live_time_mean += tlive_time[0];
			dead_time_mean_elements++;

		}
		String name = "EDXD_elements";
		data.addData(name, new int [] { nsubdets, nbins}, NexusFile.NX_FLOAT64, all_data, "counts", 1);
		data.addAxis(name, "edxd_energy_approx", new int[] { nsubdets, all_energy[0].length }, NexusFile.NX_FLOAT64, all_energy, 2, 2, "keV", false);
		data.addAxis(name, "edxd_q", new int[] { nsubdets, all_q[0].length }, NexusFile.NX_FLOAT64, all_q, 2, 1, "units", false);
		data.addElement(name, "edxd_energy_live_time", new int[] { nsubdets, all_elive_time[0].length }, NexusFile.NX_FLOAT64, all_elive_time, "seconds", true);
		data.addElement(name, "edxd_trigger_live_time", new int[] { nsubdets, all_tlive_time[0].length }, NexusFile.NX_FLOAT64, all_tlive_time, "seconds", true);
		data.addElement(name, "edxd_real_time", new int[] { nsubdets, all_real_time[0].length }, NexusFile.NX_FLOAT64, all_real_time, "seconds", true);
		data.addElement(name, "edxd_events", new int[] { nsubdets, all_events[0].length }, NexusFile.NX_INT32, all_events, "counts", true);
		data.addElement(name, "edxd_input_count_rate", new int[] { nsubdets, all_input_count_rate[0].length }, NexusFile.NX_FLOAT64, all_input_count_rate, "counts/second", true);
		data.addElement(name, "edxd_output_count_rate", new int[] { nsubdets, all_output_count_rate[0].length }, NexusFile.NX_FLOAT64, all_output_count_rate, "counts/second", true);
		data.addElement(name, "edxd_dead_time", new int[] { nsubdets, all_dead_time[0].length }, NexusFile.NX_FLOAT64, all_dead_time, "seconds", true);
		data.addElement(name, "edxd_dead_time_percent", new int[] { nsubdets, all_dead_time_percent[0].length }, NexusFile.NX_FLOAT64, all_dead_time_percent, "percent", true);
		
		data.setPlottableValue("edxd_mean_live_time", live_time_mean / dead_time_mean_elements);
		data.setPlottableValue("edxd_max_dead_time", dead_time_max);
		data.setPlottableValue("edxd_min_dead_time", dead_time_min);
		//data.setPlottableValue("edxd_mean_dead_time", dead_time_mean / dead_time_mean_elements);
		double edxd_mean_dead_time = dead_time_mean / dead_time_mean_elements;
		try {
			edxd_mean_dead_time = getMeanDeadTimePV().get();
		} catch (IOException e) {
			logger.error("Failed to get edxd_mean_dead_time", e);
		}
		data.setPlottableValue("edxd_mean_dead_time", edxd_mean_dead_time);
		data.setPlottableValue("edxd_total_counts", (double) totalCounts);

		// now perform the plotting
		updatePlots(plotds);

		return data;

	}
}
