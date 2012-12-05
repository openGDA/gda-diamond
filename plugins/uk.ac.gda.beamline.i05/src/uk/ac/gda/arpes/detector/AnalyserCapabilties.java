/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.arpes.detector;

import gda.factory.Findable;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class AnalyserCapabilties implements Findable {

	private String name = "AnalyserCapabilties";
	
	public Map<String, double[]> lens2angles = new HashMap<String, double[]>();
	
	public AnalyserCapabilties() {
		for(Object[] o: new Object[][] {
											{"Transmission", 0., 0., 1000},
											{"Angular14", -7., 14/1000., 1000},
											{"Angular7_fix", -3.5, 7/1000., 1000},
											{"Angular30", -15., 30/1000., 1000},
											{"Angular7", -3.5, 7/1000., 1000},
											{"A14small", -7., 14/1000., 1000},
											{"A30small", -15., 30./1000., 1000}, }) {
			String lens = (String) o[0];
			double start = (Double) o[1];
			double step = (Double) o[2];
			int length = (Integer) o[3];
			double[] angles = new double[length]; 
			for (int i = 0; i < angles.length; i++) {
				angles[i] = start + step * i;
			}
			
			lens2angles.put(lens, angles);
		}
	}
	
	@Override
	public void setName(String name) {
		this.name = name;
	}

	@Override
	public String getName() {
		return name;
	}
	
	public Short[] getPassEnergies() {
		return new Short[] { 1, 2, 5, 10, 20, 50, 100, 200, 500 };
	}
	
	public double getEnergyWidthForPass(int pass) {
		return pass/10.0;
	}
	
	public double getEnergyStepForPass(int pass) {
		return pass/10000.0;
	}
	
	public double[] getAngleAxis(String lensTable, int startChannel, int length) {
		if (!lens2angles.containsKey(lensTable))
			throw new ArrayIndexOutOfBoundsException("unknown lens table "+lensTable);
		double[] doubles = lens2angles.get(lensTable);
		return Arrays.copyOfRange(doubles, startChannel, startChannel + length);
	}
}