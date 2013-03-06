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

import gda.device.DeviceException;
import gda.jython.InterfaceProvider;
import gda.scan.RedoScanLineThrowable;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DummyBeamMonitorScannable extends TopupScannable implements  Runnable {

	private static final Logger logger = LoggerFactory.getLogger(DummyBeamMonitorScannable.class);
	private boolean beamDown = false;
	private BeamChecker beamChecker;
	public DummyBeamMonitorScannable() {
		super();
	}
	@Override
	public void atPointStart() throws DeviceException {
		
	}
	
	@Override
	public void atScanLineStart() throws DeviceException {
	
		beamChecker = new BeamChecker();
		beamChecker.setDaemon(true);
		beamChecker.setCheck(true);
		beamChecker.start();
	}

	
	@Override
	public void atScanLineEnd()throws DeviceException
	{				
		beamChecker.setCheck(false);
		testShouldPause();
	}
	
	@Override
	public void atCommandFailure() throws DeviceException
	{
		beamChecker.setCheck(false);
	}
	/**
	 * protected so this method may be overridden
	 * 
	 * @throws DeviceException
	 */
	@Override
	protected void testShouldPause() throws DeviceException {
		double randomNumber = 	Math.random();
		if(randomNumber >= 0.5 && randomNumber <= 0.6 || beamDown){
			setBeamDown(false);
			InterfaceProvider.getTerminalPrinter().print("beam down redoing scan " + beamDown);
			throw new RedoScanLineThrowable("Beam drop detected ");
		}
	}
	@Override
	public void run() {
		// TODO Auto-generated method stub
		
	}
	public void setBeamDown(boolean beamDown) {
		this.beamDown = beamDown;
	}
	public boolean isBeamDown() {
		return beamDown;
	}
	
	
	class BeamChecker extends Thread{
		 private boolean check;

		public boolean isCheck() {
			return check;
		}

		public void setCheck(boolean check) {
			this.check = check;
		}

		@Override
		public void run(){
			 while(check){
			 
			 double randomNumber = 	Math.random();
			 
				if(randomNumber >= 0.5 && randomNumber <= 0.51){
					beamDown = true;
					InterfaceProvider.getTerminalPrinter().print("setting the beamDown " + beamDown  + " " + this.getName());
				}
				try {
					synchronized(this){
						wait(100);
					}
				} catch (InterruptedException e) {
					InterfaceProvider.getTerminalPrinter().print("Beam monitor interrupted during scan line: Stopping");
					logger.error("Beam monitor interrupted during scan line: Stopping");
					check =false;
					break;
				}
			 }
		 }
	}
}
