/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.junit.Test;

public class XspressFillMonitorTest {

	@Test
	public void testAtScanStart() {
		XspressFillMonitor monitor = new XspressFillMonitor();

		monitor.setWaitTime(600);
		monitor.setStartTimeHours(9);
		monitor.setStartTimeMinutes(15);

		DateFormat startPauseFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm");
		Date nineTwentyAM;
		Date sevenInTheEvening;
		try {
			nineTwentyAM = startPauseFormat.parse("2010-06-24 09:20");
			sevenInTheEvening = startPauseFormat.parse("2010-06-24 19:00");

			assertTrue(monitor.shouldPause(nineTwentyAM));
			assertFalse(monitor.shouldPause(sevenInTheEvening));


		} catch (ParseException e) {
			fail("test is wrong!");
			return;
		}


	}

}
