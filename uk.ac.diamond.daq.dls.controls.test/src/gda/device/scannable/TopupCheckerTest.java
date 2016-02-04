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

package gda.device.scannable;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import gda.device.DeviceException;
import gda.device.monitor.DummyMonitor;

import org.junit.Test;

public class TopupCheckerTest {

	
	@Test
	public void testDelayCorrect() throws DeviceException {
		
		final DummyMonitor monitor = new DummyMonitor();
		monitor.setName("machine topup");
		
		final TopupChecker topup = new TopupChecker();
		topup.setName("topupMonitor");
		topup.setScannableToBeMonitored(monitor);
		topup.setTolerance(0);   		// the margin for safety on top of the data collection time
		topup.setCollectionTime(2.0);	// the data collection time 
		topup.setWaittime(1.0);			// the timeout after the topup has completed before continuing
		topup.setPauseBeforeScan(false);
		topup.setPauseBeforeLine(false);
		topup.setPauseBeforePoint(true);
		
		monitor.setConstantValue(120.0);
		assertFalse(topup.topupImminent());
		
		monitor.setConstantValue(1.0);
		assertTrue(topup.topupImminent());
		
		topup.setCollectionTime(0.5);
		assertFalse(topup.topupImminent());
		
		topup.setTolerance(5);
		assertTrue(topup.topupImminent());
	}
}
