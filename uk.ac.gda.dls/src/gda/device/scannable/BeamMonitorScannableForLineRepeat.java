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
import gda.jython.InterfaceProvider;
import gda.scan.RedoScanLineThrowable;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BeamMonitorScannableForLineRepeat extends TopupScannable {

	private static final Logger logger = LoggerFactory.getLogger(BeamMonitorScannableForLineRepeat.class);
	private boolean beamDown = false;
	private BeamChecker beamChecker;
	private BeamMonitorWithFeedbackSwitchScannable beamMonitor;
	private boolean active = false;
	private boolean override;
	public BeamMonitorScannableForLineRepeat(BeamMonitorWithFeedbackSwitchScannable beam) {
		super();
		this.beamMonitor = beam;
	}
	@Override
	public void atPointStart() throws DeviceException {
		
	}
	
	@Override
	public void atScanLineStart() throws DeviceException {
		if(active && !isOverride()){
			beamChecker = new BeamChecker();
			beamChecker.setDaemon(true);
			beamChecker.setCheck(true);
			beamChecker.start();
		}
	}

	
	@Override
	public void atScanLineEnd()throws DeviceException
	{	if(active && !isOverride()){			
		beamChecker.setCheck(false);
		testShouldPause();
	}
	}
	
	@Override
	public void atCommandFailure() throws DeviceException
	{
		if(active && !isOverride())
			beamChecker.setCheck(false);
	}
	
	public boolean isOverride() {
		return override;
	}

	public void setOverride(boolean override) {
		this.override = override;
	}
	/**
	 * protected so this method may be overridden
	 * 
	 * @throws DeviceException
	 */
	@Override
	protected void testShouldPause() throws DeviceException {
		if (active && beamDown && !isOverride()) {
			setBeamDown(false);
			InterfaceProvider.getTerminalPrinter().print("***Beam down! Redoing scan/line***");
			throw new RedoScanLineThrowable("Beam drop detected ");
		}
	}

	public void setBeamDown(boolean beamDown) {
		this.beamDown = beamDown;
	}
	public boolean isBeamDown() {
		return beamDown;
	}
	
	
	public void setActive(boolean active) {
		this.active = active;
	}
	public boolean isActive() {
		return active;
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
			 
			 		 
				try {
					if(!beamMonitor.beamWithFeedbackOn()){
						beamDown = true;
						InterfaceProvider.getTerminalPrinter().print("setting the beamDown " + beamDown  + " " + this.getName());
						check = false;
						//break;
					}
				} catch (DeviceException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
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

