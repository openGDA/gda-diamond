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

package gda.device.detector;

import gda.device.DeviceException;
import gda.epics.CAClient;
import gov.aps.jca.CAException;
import gov.aps.jca.TimeoutException;

public class MerlinDetector extends DetectorBase{

	private static final long serialVersionUID = 1L;

	private CAClient caClient;
	private NXDetector merlinController;
	private String totalCountsPV;

	public MerlinDetector(){
		caClient = new CAClient();
	}

	public void setMerlinController(NXDetector merlinController){
		this.merlinController = merlinController;
	}

	@Override
	public void collectData() throws DeviceException {
		merlinController.collectData();
	}

	@Override
	public int getStatus() throws DeviceException {
		return merlinController.getStatus();
	}

	@Override
	public Object readout() throws DeviceException {
		try {
			String totalCounts = caClient.caget(totalCountsPV);
			Double total = Double.valueOf(totalCounts);
			return total;
		} catch (CAException | TimeoutException e) {
		} catch (InterruptedException e) {
			// Reset interrupt status
			Thread.currentThread().interrupt();
		}
		return 0;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public void setCollectionTime(double collectionTime) throws DeviceException {
		merlinController.setCollectionTime(collectionTime);
		try {
			caClient.caput("BL20I-EA-DET-05:CAM:AcquireTime", collectionTime);
			caClient.caput("BL20I-EA-DET-05:CAM:AcquirePeriod", 0);
		} catch (CAException e) {
		} catch (InterruptedException e) {
		}
		this.collectionTime = collectionTime;
	}

	public String getTotalCountsPV() {
		return totalCountsPV;
	}

	public void setTotalCountsPV(String totalCountsPV) {
		this.totalCountsPV = totalCountsPV;
	}
}
