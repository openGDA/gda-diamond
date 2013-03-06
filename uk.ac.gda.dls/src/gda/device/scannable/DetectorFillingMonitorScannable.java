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
import gda.jython.commands.ScannableCommands;
import gda.scan.ScanBase;

import java.util.Calendar;
import java.util.GregorianCalendar;

public class DetectorFillingMonitorScannable extends TopupScannable {

	
	private double duration = 30.0;
	private int  startTime = 9;
	private boolean fillingOverride = false;
	public void setDuration(double duration) {
		this.duration = duration;
	}
	public double getDuration() {
		return duration;
	}
	public void setStartTime(int startTime) {
		this.startTime = startTime;
	}
	public int getStartTime() {
		return startTime;
	}
	public void setFillingOverride(boolean fillingOverride) {
		this.fillingOverride = fillingOverride;
	}
	public boolean isFillingOverride() {
		return fillingOverride;
	}
	
	@Override
	public void configure(){
		//nothing to configure
	}
	
	@Override
	protected void testShouldPause() throws DeviceException{
		while(isFilling())
		{
			try {
				
					ScanBase.checkForInterrupts();
					sendAndPrintMessage("Detector Filling : Pausing until completed");
				
				//sleep for a minute
				Thread.sleep(60000);
				
			} catch (InterruptedException e) {
				// someone trying to kill the thread so re-throw to kill any scan
				throw new DeviceException(e.getMessage(), e);
			}
			
		}

	}
	private boolean isFilling() {
		if(!fillingOverride)
		{
			double currentHour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
			if((currentHour == startTime))
			{
				if(Calendar.getInstance().get(Calendar.MINUTE) <= duration)
					return true;
			}
			else
			{
				GregorianCalendar startTimeCal = new GregorianCalendar();
				startTimeCal.set(Calendar.HOUR_OF_DAY,startTime);
				startTimeCal.set(Calendar.MINUTE, 0);
				startTimeCal.set(Calendar.SECOND, 0);
				double difference = (System.currentTimeMillis() -startTimeCal.getTime().getTime() )/1000.0;
				if(difference < 0)
				{
					if(Math.abs(difference) <= getCollectionTime())
						return true;
				}
			}
		}
		return false;
	}
	@Override
	public void atScanEnd() throws DeviceException{
		ScannableCommands.remove_default(this);
		
	}
	
	@Override
	public void atCommandFailure() 
	{
		ScannableCommands.remove_default(this);
	}
	
	public static void main(String[] args)
	{
		DetectorFillingMonitorScannable ds = new DetectorFillingMonitorScannable();
		ds.setStartTime(11);
		ds.setDuration(30.0);
		ds.setCollectionTime(1800.0);
		try {
			ds.testShouldPause();
		} catch (DeviceException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
