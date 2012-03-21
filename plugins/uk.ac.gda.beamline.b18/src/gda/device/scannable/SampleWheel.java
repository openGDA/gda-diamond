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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.epics.CAClient;
import gov.aps.jca.CAException;
import gov.aps.jca.TimeoutException;

public class SampleWheel extends ScannableBase implements Scannable {

	private String demandPV; 		// BL18B-EA-SAMPL-03:ROT.VAL
	private String readbackPV; 		// BL18B-EA-SAMPL-03:ROT.RBV
	private String inPosPV; 		// BL18B-EA-SAMPL-03:ROT.DMOV

	private String filterBasePV; 	// BL18B-EA-SAMPL-03:ROT:POS

	private int numberOfFilters;
	private Filter[] filters;

	private CAClient ca_client = new CAClient();

	public SampleWheel(){
		updateFilters();
	}
	
	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		try {
			ca_client.caput(demandPV, Double.parseDouble(position.toString()));
		} catch (CAException e) {
		} catch (InterruptedException e) {
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		try {
			return Double.parseDouble(ca_client.caget(readbackPV).toString());
		} catch (NumberFormatException e) {
		} catch (CAException e) {
		} catch (TimeoutException e) {
		} catch (InterruptedException e) {
		}
		return 0;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		int status = -1;
		try {
			status = Integer.parseInt(ca_client.caget(inPosPV).toString());
		} catch (CAException e) {
		} catch (TimeoutException e) {
		} catch (InterruptedException e) {
		}
		if(status==1)
			return false;
		return true;
	}

	public void moveToFilter(String filterName) {
		updateFilters();
		int filterNumber = findFilterNumber(filterName);
		if (filterNumber != -1) {
			filters[filterNumber].go();
		}
	}

	public int findFilterNumber(String filterName) {
		for (int i = 0; i < filters.length; i++) {
			if (filters[i].name.equals(filterName))
				return i;
		}
		return -1;
	}

	public Filter[] getFilters() {
		return filters;
	}

	public String[] getFilterNames(){
		updateFilters();
		String[] names = new String[numberOfFilters];
		for(int i=0;i<numberOfFilters;i++){
			String filter = filters[i].name.toString();
			names[i]=filter;
		}
		return names;
	}
	
	public void updateFilters() {
		filters = new Filter[numberOfFilters];
		for (int i = 1; i <= numberOfFilters; i++) {
			String name = filterBasePV + i + ":DESC";
			String go = filterBasePV + i + ":GO.PROC";
			String val = filterBasePV + i + ":VAL";
			filters[i-1] = new Filter(name, go, val);
		}
	}

	public String getDemandPV() {
		return demandPV;
	}

	public void setDemandPV(String demandPV) {
		this.demandPV = demandPV;
	}

	public String getReadbackPV() {
		return readbackPV;
	}

	public void setReadbackPV(String readbackPV) {
		this.readbackPV = readbackPV;
	}

	public int getNumberOfFilters() {
		return numberOfFilters;
	}

	public void setNumberOfFilters(int numberOfFilters) {
		this.numberOfFilters = numberOfFilters;
	}

	class Filter {
		private String namePV;
		private String goPV;
		private String posPV;

		private String name;
		private double pos;

		private CAClient ca_client = new CAClient();

		public Filter(String newNamePV, String newGoPV, String newPosPV) {
			namePV = newNamePV;
			goPV = newGoPV;
			posPV = newPosPV;
			updateName();
			updatePos();
		}

		public void updateName() {
			try {
				name = ca_client.caget(namePV);
			} catch (CAException e) {
			} catch (TimeoutException e) {
			} catch (InterruptedException e) {
			}
		}

		public void updatePos() {
			try {
				pos = Double.parseDouble(ca_client.caget(posPV).toString());
			} catch (NumberFormatException e) {
			} catch (CAException e) {
			} catch (TimeoutException e) {
			} catch (InterruptedException e) {
			}
		}

		public void go() {
			try {
				ca_client.caput(goPV, 1);
			} catch (CAException e) {
			} catch (InterruptedException e) {
			}
		}

		public String getName() {
			return name;
		}

		public double getPos() {
			return pos;
		}
	}

	public String getInPosPV() {
		return inPosPV;
	}

	public void setInPosPV(String inPosPV) {
		this.inPosPV = inPosPV;
	}

	public String getFilterBasePV() {
		return filterBasePV;
	}

	public void setFilterBasePV(String filterBasePV) {
		this.filterBasePV = filterBasePV;
	}
	
	
}