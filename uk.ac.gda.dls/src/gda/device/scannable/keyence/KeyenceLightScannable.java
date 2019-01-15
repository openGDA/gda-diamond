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

package gda.device.scannable.keyence;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.ScannableMotionUnits;
import gda.device.scannable.DummyPersistentScannable;
import gda.device.scannable.ScannableMotionUnitsBase;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.device.scannable.ScannableUtils;
import gda.factory.FactoryException;
import gda.factory.corba.util.CorbaAdapterClass;
import gda.factory.corba.util.CorbaImplClass;
import uk.ac.gda.api.remoting.ServiceInterface;

/*
 * The class needs to implement ScannableMotionUnits for it to be used by a ConverterScannable used to link zoom to 
 * light level
 */
@CorbaImplClass(value = gda.device.scannable.corba.impl.ScannableImpl.class)
@CorbaAdapterClass(value = gda.device.scannable.corba.impl.ScannableAdapter.class)
@ServiceInterface(ScannableMotionUnits.class)
public class KeyenceLightScannable extends ScannableMotionUnitsBase {
	private static final Logger logger = LoggerFactory.getLogger(KeyenceLightScannable.class);

	Keyence keyence;
	Integer lightNumber = 0;
	private Double percentDbl = Double.NaN;
	DummyPersistentScannable dummyPersistentScannable;

	public void setLightNumber(Integer lightNumber) {
		this.lightNumber = lightNumber;
	}

	KeyenceLightScannable() {
		setInputNames(new String[] { "Brightness(%)" });
	}

	@Override
	public String checkPositionValid(Object position) {
		Double[] objectToArray = ScannableUtils.objectToArray(position);
		if (objectToArray.length != 1)
			return "position must be convertible to a single Double";
		if (objectToArray[0] < 0. || objectToArray[0] > 100.)
			return "position must be between 0 and 100";
		return null;
	}

	@Override
	public void configure() throws FactoryException {
		if(isConfigured())
			return;
		super.configure();
		if (keyence == null)
			throw new FactoryException("Keyence is null");
		if (lightNumber != 1 && lightNumber != 2) {
			throw new FactoryException("lightNumber must be either 1 or 2");
		}
		dummyPersistentScannable = new DummyPersistentScannable();
		dummyPersistentScannable.setName(getName());
		dummyPersistentScannable.configure();
		try {
			Object storedVal = dummyPersistentScannable.rawGetPosition();
			if ( storedVal != null && storedVal instanceof String){
				asynchronousMoveTo(Double.valueOf((String)storedVal));
			}
		} catch (Exception e) {
			logger.error("Error in reading old value for {}", getName());
		}
		setConfigured(true);
	}

	public void setKeyence(Keyence keyence) {
		this.keyence = keyence;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		
		// See page 9-29 of the Keyence User's Manual for information about the CW,LV command.
		
		// Check position is valid
		final String reason = checkPositionValid(position);
		if (reason != null) {
			throw new DeviceException(reason);
		}
		
		// Get new brightness (%age)
		Double[] objectToArray = ScannableUtils.objectToArray(position);
		Double val = objectToArray[0];
		
		// Don't change if we're already at the requested brightness
		if( percentDbl.equals(val))
			return;
		
		// Convert %age brightness to value in range 0-127 inclusive
		int valToSend = (int) Math.round(val * 127 / 100);
		
		// Send command
		String command = String.format("CW,LV,%d,%d", lightNumber, valToSend);
		String reply = keyence.processCommand(command);
		if( !reply.startsWith("CW"))
			throw new DeviceException("Error adjusting keyence light. reply = " + reply);
		
		// Remember new position
		percentDbl = val;
		dummyPersistentScannable.rawAsynchronousMoveTo(percentDbl);
		
		notifyIObservers(this, new ScannablePositionChangeEvent(percentDbl));
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return percentDbl;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

}
