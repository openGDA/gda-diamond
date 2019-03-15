/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.epics.CAClient;
import gda.epics.connection.EpicsChannelManager;
import gda.epics.connection.EpicsController;
import gda.factory.FactoryException;
import gov.aps.jca.CAException;
import gov.aps.jca.Channel;
import gov.aps.jca.TimeoutException;

public class GeFanuc110BLADC extends DetectorBase {

	private static final long serialVersionUID = 1L;

	double samplingRate;
	int numberOfChannels;
	boolean useSoftwareGate;
	int noSamplesToAvg;
	int gateChannel;
	int adcThreshold;

	String samplingRate_pv;
	String numberOfChannels_pv;
	String useSoftwareGate_pv;
	String noSamplesToAvg_pv;
	String gateChannel_pv;
	String adcThreshold_pv;
	String enAcq_pv;
	String runtimeDataProblem_pv;
	String readStatus_pv;
	String fifoEmpty_pv;
	String data_pv;

	private EpicsChannelManager channelManager;
	private Channel dataChnl;
	private EpicsController controller;
	double[] data;

	private CAClient ca_client = new CAClient();
	private static final Logger logger = LoggerFactory.getLogger(GeFanuc110BLADC.class);

	@Override
	public void configure() throws FactoryException {


		try {
			controller = EpicsController.getInstance();
			channelManager = new EpicsChannelManager();
			dataChnl = channelManager.createChannel(data_pv, false);

		} catch (CAException e) {
			throw new FactoryException("CAException while creating channels for " + getName(), e);
		}
		super.configure();
	}


	@Override
	public void collectData() throws DeviceException {
		// 1. Set the sampling rate. (CLOCKRATE)
		// 2. Set the minimum number of channels to read out. (CHANNELS)
		// 3. If using a software gate, set the number of samples to average over (SAMPLESTOAVERAGE)
		// 4. If using a hardware gate:
		// - Enable the use of a hardware gate (GATEENABLE)
		// - Select the channel the gate signal is connected to (GATECHANNEL)
		// - Select the ADC count threshold that will define when the gate is high (GATETHRESHOLD)
		// 5. Enable data acquisition (ACQUIRE)
		// 6. Disable data acquisition.


		try {
			ca_client.caput(samplingRate_pv, samplingRate);
			ca_client.caput(numberOfChannels_pv, numberOfChannels);
			if (useSoftwareGate) {
				ca_client.caput(useSoftwareGate_pv, 0);
				ca_client.caput(noSamplesToAvg_pv, noSamplesToAvg);
			} else {
				ca_client.caput(useSoftwareGate_pv, 1);
				ca_client.caput(gateChannel_pv, gateChannel);
				ca_client.caput(adcThreshold_pv, adcThreshold);
			}
			ca_client.caput(enAcq_pv, 1);
			ca_client.caput(enAcq_pv, 0);

		}

		catch (CAException e) {
			throw new DeviceException("Error reading or setting pv ", e);
		} catch (InterruptedException e) {
			throw new DeviceException("Error reading or setting pv ", e);
		}
	}

	@Override
	public int getStatus() throws DeviceException {
		return 0;
	}

	@Override
	public Object readout() throws DeviceException {
		// 7. Read the RUNTIMEPROBLEM_RBV_PV and make sure it is not on.
		// 8. Read the ADC card status (READSTATUS). Make sure STATUSFIFOEMPTY_RBV is on.
		// 9. Readout the data arrays.

		try {
			int runtimeDataProblem = Integer.parseInt(ca_client.caget(runtimeDataProblem_pv).toString());
			ca_client.caput(readStatus_pv, 1);
			String fifoEmpty = ca_client.caget(fifoEmpty_pv);

			if (runtimeDataProblem==0 && fifoEmpty.equals("1.0")) {
				data = controller.cagetDoubleArray(dataChnl);
				return data;
			}
			logger.error("Runtime Data Problem or fifo not empty, will not read data.");
		}
		catch (TimeoutException e) {
			throw new DeviceException("Error reading or setting pv ", e);
		} catch (CAException e) {
			throw new DeviceException("Error reading or setting pv ", e);
		} catch (InterruptedException e) {
			throw new DeviceException("Error reading or setting pv ", e);
		}
		return null;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {

		return false;
	}

	@Override
	public String getDescription() throws DeviceException {

		return null;
	}

	@Override
	public String getDetectorID() throws DeviceException {

		return null;
	}

	@Override
	public String getDetectorType() throws DeviceException {

		return null;
	}

	public double getSamplingRate() {
		return samplingRate;
	}

	public void setSamplingRate(double samplingRate) {
		this.samplingRate = samplingRate;
	}

	public int getNumberOfChannels() {
		return numberOfChannels;
	}

	public void setNumberOfChannels(int numberOfChannels) {
		this.numberOfChannels = numberOfChannels;
	}

	public boolean isUseSoftwareGate() {
		return useSoftwareGate;
	}

	public void setUseSoftwareGate(boolean useSoftwareGate) {
		this.useSoftwareGate = useSoftwareGate;
	}

	public String getSamplingRate_pv() {
		return samplingRate_pv;
	}

	public void setSamplingRate_pv(String samplingRate_pv) {
		this.samplingRate_pv = samplingRate_pv;
	}

	public String getNumberOfChannels_pv() {
		return numberOfChannels_pv;
	}

	public void setNumberOfChannels_pv(String numberOfChannels_pv) {
		this.numberOfChannels_pv = numberOfChannels_pv;
	}

	public String getUseSoftwareGate_pv() {
		return useSoftwareGate_pv;
	}

	public void setUseSoftwareGate_pv(String useSoftwareGate_pv) {
		this.useSoftwareGate_pv = useSoftwareGate_pv;
	}

	public int getNoSamplesToAvg() {
		return noSamplesToAvg;
	}

	public void setNoSamplesToAvg(int noSamplesToAvg) {
		this.noSamplesToAvg = noSamplesToAvg;
	}

	public String getNoSamplesToAvg_pv() {
		return noSamplesToAvg_pv;
	}

	public void setNoSamplesToAvg_pv(String noSamplesToAvg_pv) {
		this.noSamplesToAvg_pv = noSamplesToAvg_pv;
	}

	public String getEnAcq_pv() {
		return enAcq_pv;
	}

	public void setEnAcq_pv(String enAcq_pv) {
		this.enAcq_pv = enAcq_pv;
	}

	public String getRuntimeDataProblem_pv() {
		return runtimeDataProblem_pv;
	}

	public void setRuntimeDataProblem_pv(String runtimeDataProblem_pv) {
		this.runtimeDataProblem_pv = runtimeDataProblem_pv;
	}

	public String getReadStatus_pv() {
		return readStatus_pv;
	}

	public void setReadStatus_pv(String readStatus_pv) {
		this.readStatus_pv = readStatus_pv;
	}

	public int getGateChannel() {
		return gateChannel;
	}

	public void setGateChannel(int gateChannel) {
		this.gateChannel = gateChannel;
	}

	public int getAdcThreshold() {
		return adcThreshold;
	}

	public void setAdcThreshold(int adcThreshold) {
		this.adcThreshold = adcThreshold;
	}

	public String getGateChannel_pv() {
		return gateChannel_pv;
	}

	public void setGateChannel_pv(String gateChannel_pv) {
		this.gateChannel_pv = gateChannel_pv;
	}

	public String getAdcThreshold_pv() {
		return adcThreshold_pv;
	}

	public void setAdcThreshold_pv(String adcThreshold_pv) {
		this.adcThreshold_pv = adcThreshold_pv;
	}

	public String getFifoEmpty_pv() {
		return fifoEmpty_pv;
	}

	public void setFifoEmpty_pv(String fifoEmpty_pv) {
		this.fifoEmpty_pv = fifoEmpty_pv;
	}

	public String getData_pv() {
		return data_pv;
	}

	public void setData_pv(String data_pv) {
		this.data_pv = data_pv;
	}


}
