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

import gda.device.MotorException;
import gda.device.enumpositioner.DummyPositioner;
import gda.device.motor.DummyMotor;
import gda.device.scannable.ScannableMotor;
import gda.factory.FactoryException;
import uk.ac.gda.test.util.MockFinderHelper;

public class EdeTestBase extends MockFinderHelper {
	public static ScannableMotor createMotor(String name) throws MotorException, FactoryException {
		DummyMotor xMotor = new DummyMotor();
		xMotor.setSpeed(5000);
		xMotor.configure();
		ScannableMotor xScannable = new ScannableMotor();
		xScannable.setMotor(xMotor);
		xScannable.setName(name);
		xScannable.configure();
		return xScannable;
	}

	protected DummyPositioner createShutter2(){
		DummyPositioner shutter2 = new DummyPositioner();
		shutter2.setName("Shutter");
		shutter2.setPositions(new String[]{"In","Out"});
		return shutter2;
	}
}
