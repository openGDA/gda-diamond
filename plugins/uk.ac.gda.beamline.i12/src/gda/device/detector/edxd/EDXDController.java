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

import gda.analysis.DataSet;
import gda.analysis.RCPPlotter;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.detector.DetectorBase;
import gda.device.detector.NXDetectorData;
import gda.device.detector.NexusDetector;
import gda.device.epicsdevice.FindableEpicsDevice;
import gda.device.epicsdevice.ReturnType;
import gda.epics.LazyPVFactory;
import gda.epics.PV;
import gda.factory.Configurable;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gda.util.persistence.LocalObjectShelf;
import gda.util.persistence.LocalObjectShelfManager;
import gda.util.persistence.ObjectShelfException;
import gda.util.persistence.LocalDatabase.LocalDatabaseException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class describes the EDXD detector on I12, it is made up of 24 subdetectors
 */
public class EDXDController extends DetectorBase implements Configurable, NexusDetector {

	// Setup the logging facilities
	transient protected static final Logger logger = LoggerFactory.getLogger(EDXDController.class);

	protected static final int NUMBER_OF_ATTEMPTS = 5;
	protected static final int NUMBER_OF_ELEMENTS = 24;
	protected static final int TOTAL_NUMBER_OF_TRACE_DATASETS = 10;
	protected static final String EDXD_PLOT = "EDXD Plot";
	private int numberOfElements = NUMBER_OF_ELEMENTS;
	/**
	 * This method is only public for testing, and should be removed from the interface
	 */
	public FindableEpicsDevice xmap = null;

	private boolean isBusy = false;

	private String deviceName;

	protected List<EDXDElement> subDetectors = new ArrayList<EDXDElement>();

	protected DeviceException collectData_Exception;
	
	private String prefix = "BL12I-EA-DET-03:";	
	private String meanDeadTimePVName = "DeadTime";
	private PV<Double> meanDeadTimePV;

	/**
	 * Basic constructor, nothing done in here, waiting for configure
	 */
	public EDXDController() {
	}

	/**
	 * @return String
	 */
	public String getDeviceName() {
		return deviceName;
	}

	/**
	 * @param deviceName
	 */
	public void setDeviceName(String deviceName) {
		this.deviceName = deviceName;
	}

	@Override
	public void configure() throws FactoryException {

		super.configure();

		xmap = new FindableEpicsDevice();
		xmap.setDeviceName(getDeviceName());
		xmap.setName(getDeviceName());
		
		//TODO do we really need to call configure here??
		xmap.configure();

		// Add all the EDXD Elements to the detector
		for (int i = 0; i < getNumberOfElements(); i++) {
			subDetectors.add(new EDXDElement(xmap, i+1));

		}

		setInputNames(new String[] {});
		setExtraNames(new String[] { "edxd_mean_live_time", "edxd_max_dead_time", "edxd_min_dead_time",
				"edxd_mean_dead_time", "edxd_total_counts" });

	}

	@Override
	public void collectData() throws DeviceException {

		for (int i = 0; i < subDetectors.size(); i++) {
			if (!subDetectors.get(i).isQMapped()) {
				throw new DeviceException(
						"Q mapping needs to be set before collecting data; you may need to calibrate to generate calibration file");
			}
		}
		
		collectData_Exception = null;
		// set the acquisition time
		xmap.setValue("SETPRESETVALUE", "", collectionTime);

		// set to take the acquisition for the amount of time specified
		// 0 = Disabled
		// 1 = real time
		// 2 = live time
		// 3 = events
		xmap.setValue("SETPRESETTYPE", "", 1);

		(new Thread() {

			@Override
			public void run() {

				isBusy = true;
				// now run the actual collection
				// this has been seen to fail, so a loop trying a couple of times would probably be good
				try {
//					xmap.setValue(null, "ACQUIRE", "", 1, (2 * collectionTime) + 5);
					xmap.setValue(null, "ACQUIRE", "", 1, (24*60*60));
				} catch (DeviceException e) {
					logger.error(e.getMessage(), e);
					collectData_Exception = e;
				}

				isBusy = false;
				return;
			}
		}).start();

		// now give the thread enough time to start before returning
		try {
			Thread.sleep(100);
		} catch (InterruptedException e) {
			// Just carry on, it shouldent be too much of a problem if this fails
		}
	}

	@Override
	public String getDescription() throws DeviceException {
		return "The EDXD Detector for I12";
	}

	@Override
	public String getDetectorID() throws DeviceException {
		return "I12 EDXD Detector";
	}

	@Override
	public String getDetectorType() throws DeviceException {
		return "Multi channel MCA";
	}

	@Override
	public int getStatus() throws DeviceException {
		if (isBusy) {
			return 1;
		}
		return 0;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	protected void verifyData() throws DeviceException {
		// If there was a problem when acquiring the data
		if (collectData_Exception != null) {
			throw collectData_Exception;
		}
	}

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

		// populate the data item from the elements
		for (int i = 0; i < subDetectors.size(); i++) {

			EDXDElement det = subDetectors.get(i);

			// add the data
			plotds[i] = new DataSet(det.getName(), det.readoutDoubles());

			totalCounts += plotds[i].sum();

			data.addData(det.getName(), det.getDataDimensions(), det.getDataType(), plotds[i].doubleArray(), "counts",
					1);

			// add the energy Axis
			double[] energy = det.getEnergyBins();
			data.addAxis(det.getName(), "edxd_energy_approx", new int[] { energy.length }, NexusFile.NX_FLOAT64,
					energy, 2, 2, "keV", false);

			// add the q Axis
			double[] q = det.getQMapping();
			data.addAxis(det.getName(), "edxd_q", new int[] { energy.length }, NexusFile.NX_FLOAT64, q, 2, 1, "units",
					false);

			double[] elive_time = { det.getEnergyLiveTime() };
			data.addElement(det.getName(), "edxd_energy_live_time", new int[] { elive_time.length },
					NexusFile.NX_FLOAT64, elive_time, "seconds", true);

			double[] tlive_time = { det.getTriggerLiveTime() };
			data.addElement(det.getName(), "edxd_trigger_live_time", new int[] { tlive_time.length },
					NexusFile.NX_FLOAT64, tlive_time, "seconds", true);

			double[] real_time = { det.getRealTime() };
			data.addElement(det.getName(), "edxd_real_time", new int[] { real_time.length }, NexusFile.NX_FLOAT64,
					real_time, "seconds", true);

			int[] events = { det.getEvents() };
			data.addElement(det.getName(), "edxd_events", new int[] { events.length }, NexusFile.NX_INT32, events,
					"counts", true);

			double[] input_count_rate = { det.getInputCountRate() };
			data.addElement(det.getName(), "edxd_input_count_rate", new int[] { input_count_rate.length },
					NexusFile.NX_FLOAT64, input_count_rate, "counts/second", true);

			double[] output_count_rate = { det.getOutputCountRate() };
			data.addElement(det.getName(), "edxd_output_count_rate", new int[] { output_count_rate.length },
					NexusFile.NX_FLOAT64, output_count_rate, "counts/second", true);

			// simple deadtime calculation for now, which is simply based on the 2 rates
			double[] dead_time = { (1.0 - (output_count_rate[0] / input_count_rate[0])) * real_time[0] };
			data.addElement(det.getName(), "edxd_dead_time", new int[] { dead_time.length }, NexusFile.NX_FLOAT64,
					dead_time, "seconds", true);
			
			// simple deadtime calculation for now, which is simply based on the 2 rates
			double[] dead_time_percent = { (1.0 - (output_count_rate[0] / input_count_rate[0])) * 100.0 };
			data.addElement(det.getName(), "edxd_dead_time_percent", new int[] { dead_time_percent.length }, NexusFile.NX_FLOAT64,
					dead_time_percent, "percent", true);

			// now calculate the deadtime statistics
			if (dead_time[0] > dead_time_max)
				dead_time_max = dead_time[0];
			if (dead_time[0] < dead_time_min)
				dead_time_min = dead_time[0];
			dead_time_mean += dead_time[0];
			live_time_mean += tlive_time[0];
			dead_time_mean_elements++;

		}

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

	/**
	 * Sets the number of bins that are used by the xmap.
	 * 
	 * @param NumberOfBins
	 *            a number up to 16k
	 * @return the number of bins which are actualy set.
	 * @throws DeviceException
	 */
	public int setBins(int NumberOfBins) throws DeviceException {
		xmap.setValue("SETNBINS", "", NumberOfBins);
		return (Integer) xmap.getValue(ReturnType.DBR_NATIVE, "GETNBINS", "");
	}

	/**
	 * @return The number of bins the xmap is curently set to
	 * @throws DeviceException
	 */
	public int getBins() throws DeviceException {
		return (Integer) xmap.getValue(ReturnType.DBR_NATIVE, "GETNBINS", "");
	}

	/**
	 * Sets the dynamic range of the detector
	 * 
	 * @param dynamicRange
	 *            the dynamic range in KeV
	 * @return the actual value which has been set
	 * @throws DeviceException
	 */
	public double setDynamicRange(double dynamicRange) throws DeviceException {
		xmap.setValue("SETDYNRANGE", "", dynamicRange);
		return (Double) xmap.getValue(ReturnType.DBR_NATIVE, "GETDYNRANGE0", "");
	}

	/**
	 * Sets the energy per bin
	 * 
	 * @param binWidth
	 *            in eV
	 * @throws DeviceException
	 */
	public void setBinWidth(double binWidth) throws DeviceException {
		xmap.setValue("SETBINWIDTH", "", binWidth);
	}

	/**
	 * Simple method which sets up the EDXD with some basic assumptions
	 * 
	 * @param maxEnergy
	 *            The maxim energy expected in KeV
	 * @param numberOfBins
	 *            the number of bins that are wanted, i.e the resolution
	 * @throws DeviceException
	 */
	public void setup(double maxEnergy, int numberOfBins) throws DeviceException {
		// set the dynamic range to twice the max energy
		setDynamicRange(maxEnergy * 2.0);
		int bins = setBins(numberOfBins);
		setBinWidth((maxEnergy * 1000.0) / bins);
	}

	// All the saving and loading settings

	/**
	 * Save all the xmap settings, with no description
	 * 
	 * @param name
	 * @throws ObjectShelfException
	 * @throws LocalDatabaseException
	 * @throws DeviceException
	 */
	public void saveCurrentSettings(String name) throws ObjectShelfException, LocalDatabaseException, DeviceException {
		saveCurrentSettings(name, "No Description");
	}

	/**
	 * Save all the xmap settings along with the given description
	 * 
	 * @param name
	 * @param description
	 * @throws ObjectShelfException
	 * @throws LocalDatabaseException
	 * @throws DeviceException
	 */
	public void saveCurrentSettings(String name, String description) throws ObjectShelfException,
			LocalDatabaseException, DeviceException {
		LocalObjectShelf los = LocalObjectShelfManager.open("EDXD" + name);

		// Save the description
		los.addValue("desc", description);

		// save the number of bins
		los.addValue("nbins", getBins());

		// populate the shelf from the subdetectors
		for (int i = 0; i < subDetectors.size(); i++) {

			los.addValue(subDetectors.get(i).getName(), subDetectors.get(i).saveConfiguration());

		}

		InterfaceProvider.getTerminalPrinter().print("File Saved Sucsessfully");

	}

	/**
	 * Loads a setting from the persistance
	 * 
	 * @param name
	 * @return The description of the configuration loaded
	 * @throws DeviceException
	 * @throws ObjectShelfException
	 * @throws LocalDatabaseException
	 */
	public String loadSettings(String name) throws DeviceException, ObjectShelfException, LocalDatabaseException {

		LocalObjectShelf los = LocalObjectShelfManager.open("EDXD" + name);

		// load the number of bins
		setBins((Integer) los.get("nbins"));

		// populate the shelf from the subdetectors
		for (int i = 0; i < subDetectors.size(); i++) {

			logger.info("Setting subdetector {} with loaded values", i);
			subDetectors.get(i).loadConfiguration((EDXDElementBean) los.get(subDetectors.get(i).getName()));

		}
		String desc = "No Description";

		try {
			desc = (String) los.get("desc");
		} catch (ObjectShelfException e) {
			// Do nothing id the desc is absent
		}

		return desc;

	}

	/**
	 * This method shows all the savefiles for the EDXD detector
	 * 
	 * @return a string containing all the files
	 * @throws LocalDatabaseException
	 * @throws ObjectShelfException
	 * @throws LocalDatabaseException
	 * @throws ObjectShelfException
	 */
	public String listSettings() throws ObjectShelfException, LocalDatabaseException {

		String result = "";
		for (String shelf : LocalObjectShelfManager.shelves()) {
			if (shelf.startsWith("EDXD")) {
				LocalObjectShelf los = LocalObjectShelfManager.open(shelf);
				String desc = "No Description";

				try {
					desc = (String) los.get("desc");
				} catch (ObjectShelfException e) {
					// Do nothing id the desc is absent
				}

				result += shelf.replace("EDXD", "") + "\t:\t" + desc + "\n";
			}
		}

		return result;

	}

	/**
	 * Prints all the settings to the screen, this is an I12 request
	 * 
	 * @return the created string
	 */
	public String printCurrentSettings() {

		String result = "Element Name     Base_L   Base_T   Bin_Width  Dyn_Ran   E_Thresh  Gap_Time  Max_Wid  Peak_Time Pre_Gain  Re_Del T_Gap_T T_peak_T  Trig_Thres\n";

		// populate the string from the subdetectors
		for (int i = 0; i < subDetectors.size(); i++) {

			result = result + subDetectors.get(i).toString() + "\n";

		}

		return result;
	}

	// Setters for the various settings accross the board

	/**
	 * Set the preampGain for all elements
	 * 
	 * @param preampGain
	 * @throws DeviceException
	 */
	public void setPreampGain(double preampGain) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setPreampGain(preampGain);
		}
	}

	/**
	 * Set the peakTime for all elements
	 * 
	 * @param peakTime
	 * @throws DeviceException
	 */
	public void setPeakTime(double peakTime) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setPeakTime(peakTime);
		}
	}

	/**
	 * Set the triggerThreshold for all elements
	 * 
	 * @param triggerThreshold
	 * @throws DeviceException
	 */
	public void setTriggerThreshold(double triggerThreshold) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setTriggerThreshold(triggerThreshold);
		}
	}

	/**
	 * Set the baseThreshold for all elements
	 * 
	 * @param baseThreshold
	 * @throws DeviceException
	 */
	public void setBaseThreshold(double baseThreshold) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setBaseThreshold(baseThreshold);
		}
	}

	/**
	 * Set the baseLength for all elements
	 * 
	 * @param baseLength
	 * @throws DeviceException
	 */
	public void setBaseLength(int baseLength) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setBaseLength(baseLength);
		}
	}

	/**
	 * Set the energyThreshold for all elements
	 * 
	 * @param energyThreshold
	 * @throws DeviceException
	 */
	public void setEnergyThreshold(double energyThreshold) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setEnergyThreshold(energyThreshold);
		}
	}

	/**
	 * Set the resetDelay for all elements
	 * 
	 * @param resetDelay
	 * @throws DeviceException
	 */
	public void setResetDelay(double resetDelay) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setResetDelay(resetDelay);
		}
	}

	/**
	 * Set the gapTime for all elements
	 * 
	 * @param gapTime
	 * @throws DeviceException
	 */
	public void setGapTime(double gapTime) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setGapTime(gapTime);
		}
	}

	/**
	 * Set the triggerPeakTime for all elements
	 * 
	 * @param triggerPeakTime
	 * @throws DeviceException
	 */
	public void setTriggerPeakTime(double triggerPeakTime) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setTriggerPeakTime(triggerPeakTime);
		}
	}

	/**
	 * Set the triggerGapTime for all elements
	 * 
	 * @param triggerGapTime
	 * @throws DeviceException
	 */
	public void setTriggerGapTime(double triggerGapTime) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setTriggerGapTime(triggerGapTime);
		}
	}

	/**
	 * Set the maxWidth for all elements
	 * 
	 * @param maxWidth
	 * @throws DeviceException
	 */
	public void setMaxWidth(double maxWidth) throws DeviceException {
		for (int i = 0; i < subDetectors.size(); i++) {
			subDetectors.get(i).setMaxWidth(maxWidth);
		}
	}

	/**
	 * Get one of the elements specifialy by name
	 * 
	 * @param index
	 * @return An the EDXDElement requested
	 */
	public EDXDElement getSubDetector(int index) {
		return subDetectors.get(index);
	}

	// Spectra Monitoring and Plotting

	private boolean plotAllSpectra = false;

	private Integer traceOneSpectra = null;

	private boolean newTrace = true;

	private ArrayList<DataSet> traceDataSets = new ArrayList<DataSet>();

	/**
	 * 
	 */
	public void monitorAllSpectra() {
		plotAllSpectra = true;
	}

	/**
	 * Monitors a specific spectra
	 * 
	 * @param detectorNumber
	 */
	public void monitorSpectra(int detectorNumber) {
		if (detectorNumber < 1 || detectorNumber > getNumberOfElements())
		{
			throw new IllegalArgumentException("Detector number must be between 1 and 24 (both limits inclusive)");
		}
		detectorNumber-=1;
		
		plotAllSpectra = false;
		traceOneSpectra = detectorNumber;
		newTrace = true;
	}

	/**
	 * Stops monitoring the detector
	 */
	public void stopMonitoring() {
		plotAllSpectra = false;
		traceOneSpectra = null;
		newTrace = true;
	}

	/**
	 * Clears the trace if there is a specific detector being traced
	 */
	public void clearTrace() {
		newTrace = true;
	}

	/**
	 * Acquires a single image for viewing only
	 * 
	 * @param aquisitionTime
	 *            The time to collect for
	 * @return The dataset of the aquired data, for additional processing if required.
	 * @throws DeviceException
	 * @throws InterruptedException
	 */
	public DataSet[] acquire(double aquisitionTime) throws DeviceException, InterruptedException {
		return acquire(aquisitionTime, true);
	}

	/**
	 * Acquires a single image for viewing only
	 * 
	 * @param aquisitionTime
	 *            The time to collect for
	 * @return The dataset of the aquired data, for additional processing if required.
	 * @throws DeviceException
	 * @throws InterruptedException
	 */
	@SuppressWarnings("static-access")
	public DataSet[] acquire(double aquisitionTime, boolean verbose) throws DeviceException, InterruptedException {
		this.setCollectionTime(aquisitionTime);
		this.collectData();

		while (isBusy) {
			if (verbose)
				InterfaceProvider.getTerminalPrinter().print("Acquiring");
			Thread.sleep(1000);
		}

		if (verbose)
			InterfaceProvider.getTerminalPrinter().print("Done");

		this.verifyData();

		// now the data is acquired, plot it out to plot2 for the time being.
		DataSet[] data = new DataSet[subDetectors.size()];

		for (int i = 0; i < subDetectors.size(); i++) {

			EDXDElement det = subDetectors.get(i);

			// add the data
			data[i] = new DataSet(det.getName(), det.readoutDoubles());

		}
		DataSet yaxis = new DataSet("Energy", subDetectors.get(0).getEnergyBins());

		try {
			RCPPlotter.plot(EDXD_PLOT, yaxis, data);
		} catch (Exception e) {
			throw new DeviceException(e.getMessage(),e);
		}

		return data;

	}

	@SuppressWarnings("static-access")
	protected void updatePlots(DataSet[] plotds) throws DeviceException {
		try{
			
			if(plotAllSpectra) {
				DataSet yAxis = new DataSet("Energy",subDetectors.get(0).getEnergyBins());
				RCPPlotter.plot(EDXD_PLOT, yAxis, plotds);
			} else {
	
				if(traceOneSpectra!=null) {
					DataSet yAxis = new DataSet("Energy",subDetectors.get(traceOneSpectra).getEnergyBins());
					if (newTrace) {
						traceDataSets.clear();
						newTrace=false;
					}
					traceDataSets.add(plotds[traceOneSpectra]);
					while (traceDataSets.size() > TOTAL_NUMBER_OF_TRACE_DATASETS) {
						traceDataSets.remove(0);
					}
					DataSet[] plotValues = new DataSet[traceDataSets.size()];
					for(int i = 0; i < traceDataSets.size(); i++) {
						plotValues[i] = traceDataSets.get(i);				
					}
					RCPPlotter.stackPlot(EDXD_PLOT, yAxis, plotValues);


				}
			}

		} catch (Exception e) {
			throw new DeviceException(e.getMessage(),e);
		}

	}

	public void setNumberOfElements(int numberOfElements) {
		this.numberOfElements = numberOfElements;
	}

	public int getNumberOfElements() {
		return numberOfElements;
	}

	public boolean isQMapped() {
		for (int i = 0; i < subDetectors.size(); i++) {
			if (!subDetectors.get(i).isQMapped()) {
				return false;
			}
		}
		return true;
	}
	
	public String getPrefix() {
		return prefix;
	}

	public void setPrefix(String prefix) {
		this.prefix = prefix;
	}
	
	public PV<Double> getMeanDeadTimePV() {
		if (meanDeadTimePV == null) {
			meanDeadTimePV = LazyPVFactory.newDoublePV(getPrefix()+meanDeadTimePVName);
		}
		return meanDeadTimePV;
	}
}
