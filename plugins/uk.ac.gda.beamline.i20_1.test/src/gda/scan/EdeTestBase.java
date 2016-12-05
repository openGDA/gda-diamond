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

package gda.scan;

import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;

import gda.device.enumpositioner.DummyPositioner;
import gda.device.scannable.ScannableMotor;

public class EdeTestBase {
	public static ScannableMotor createMotor(String name) throws Exception {

		ScannableMotor energy_scannable = PowerMockito.mock(ScannableMotor.class);
		Mockito.when(energy_scannable.getName()).thenReturn(name);
		Mockito.when(energy_scannable.getInputNames()).thenReturn(new String[] { name });
		Mockito.when(energy_scannable.getExtraNames()).thenReturn(new String[] {});
		Mockito.when(energy_scannable.getOutputFormat()).thenReturn(new String[] { "%.2f" });
		Mockito.when(energy_scannable.getPosition()).thenReturn(7000.0);

		return energy_scannable;
	}

	protected DummyPositioner createShutter2(){
		DummyPositioner shutter2 = new DummyPositioner();
		shutter2.setName("Shutter");
		shutter2.setPositions(new String[]{"In","Out"});
		return shutter2;
	}
}
