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

import java.io.IOException;

import gda.device.DeviceException;
import gda.epics.LazyPVFactory;
import gda.epics.PV;
import gda.epics.ReadOnlyPV;
import gda.factory.FactoryException;

public class SampleWheel extends ScannableBase {

	private String demandPVString; // BL18B-EA-SAMPL-03:ROT.VAL
	private String readbackPVString; // BL18B-EA-SAMPL-03:ROT.RBV
	private String inPosPVString; // BL18B-EA-SAMPL-03:ROT.DMOV
	private String filterBasePVString; // BL18B-EA-SAMPL-03:ROT:POS

	private int numberOfFilters;
	private Filter[] filters;

	private PV<Double> demandPV;

	private ReadOnlyPV<Double> readbackPV;

	private ReadOnlyPV<Integer> inPosPV;

	// private CAClient ca_client = new CAClient();

	public SampleWheel() {
		updateFilters();
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		demandPV = LazyPVFactory.newDoublePV(demandPVString);
		readbackPV = LazyPVFactory.newReadOnlyDoublePV(readbackPVString);
		inPosPV = LazyPVFactory.newReadOnlyIntegerPV(inPosPVString);
		updateFilters();
		setConfigured(true);
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		try {
			demandPV.putNoWait(Double.parseDouble(position.toString()));
		} catch (Exception e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		try {
			return readbackPV.get();
		} catch (Exception e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public boolean isBusy() throws DeviceException {
		try {
			int status = inPosPV.get();
			return status != 1;
		} catch (Exception e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	public void moveToFilter(String filterName) throws DeviceException {
		updateFilters();
		int filterNumber = findFilterNumber(filterName);
		if (filterNumber != -1) {
			filters[filterNumber].go();
		}
	}

	private int findFilterNumber(String filterName) throws DeviceException {
		for (int i = 0; i < filters.length; i++) {
			if (filters[i].getName().equals(filterName))
				return i;
		}
		return -1;
	}

	public String[] getFilterNames() throws DeviceException {
		updateFilters();
		String[] names = new String[numberOfFilters];
		for (int i = 0; i < numberOfFilters; i++) {
			String filter = filters[i].getName();
			names[i] = filter;
		}
		return names;
	}

	public void updateFilters() {
		filters = new Filter[numberOfFilters];
		for (int i = 1; i <= numberOfFilters; i++) {
			String name = filterBasePVString + i + ":DESC";
			String go = filterBasePVString + i + ":GO.PROC";
			filters[i - 1] = new Filter(name, go);
		}
	}

	public String getDemandPV() {
		return demandPVString;
	}

	public void setDemandPV(String demandPV) {
		this.demandPVString = demandPV;
	}

	public String getReadbackPV() {
		return readbackPVString;
	}

	public void setReadbackPV(String readbackPV) {
		this.readbackPVString = readbackPV;
	}

	public int getNumberOfFilters() {
		return numberOfFilters;
	}

	public void setNumberOfFilters(int numberOfFilters) {
		this.numberOfFilters = numberOfFilters;
	}

	public String getInPosPV() {
		return inPosPVString;
	}

	public void setInPosPV(String inPosPV) {
		this.inPosPVString = inPosPV;
	}

	public String getFilterBasePV() {
		return filterBasePVString;
	}

	public void setFilterBasePV(String filterBasePV) {
		this.filterBasePVString = filterBasePV;
	}

	class Filter {

		private ReadOnlyPV<String> namePV;
		private PV<Integer> goPV;

		public Filter(String newNamePV, String newGoPV) {
			namePV = LazyPVFactory.newReadOnlyStringPV(newNamePV);
			goPV = LazyPVFactory.newIntegerPV(newGoPV);
		}

		public void go() throws DeviceException {
			try {
				goPV.putNoWait(1);
			} catch (IOException e) {
				throw new DeviceException(e.getMessage(), e);
			}
		}

		public String getName() throws DeviceException {
			try {
				return namePV.get();
			} catch (IOException e) {
				throw new DeviceException(e.getMessage(), e);
			}
		}
	}
}