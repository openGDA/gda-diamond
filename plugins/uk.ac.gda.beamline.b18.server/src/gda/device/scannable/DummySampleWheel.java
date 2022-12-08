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

public class DummySampleWheel extends ScannableBase {

	double demand = 0;

	private int numberOfFilters;
	private Filter[] filters;

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		demand = Double.parseDouble(position.toString());
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return demand;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
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

	public String[] getFilterNames() {
		updateFilters();
		String[] names = new String[numberOfFilters];
		for (int i = 0; i < numberOfFilters; i++)
			names[i] = filters[i].name;
		return names;
	}

	public void updateFilters() {
		filters = new Filter[numberOfFilters];
		for (int i = 1; i <= numberOfFilters; i++)
			filters[i - 1] = new Filter("Filter"+i, i);
	}

	public int getNumberOfFilters() {
		return numberOfFilters;
	}

	public void setNumberOfFilters(int numberOfFilters) {
		this.numberOfFilters = numberOfFilters;
	}

	class Filter {

		private String name;
		private double pos;

		public Filter(String name, double pos) {
			//name = "Filter " + (int) Math.ceil(Math.random()*100);
			this.name=name;
			this.pos=pos;
			updateName();
			updatePos();
		}

		public void updateName() {
		}

		public void updatePos() {
			//pos = Math.random()*10;
		}

		public void go() {
		}

		public void setName(String name){
			this.name = name;
		}

		public String getName() {
			return name;
		}

		public double getPos() {
			return pos;
		}

		public void setPos(double pos){
			this.pos = pos;
		}
	}
}
