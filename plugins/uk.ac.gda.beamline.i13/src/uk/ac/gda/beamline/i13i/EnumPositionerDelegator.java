/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i;

import gda.device.DeviceBase;
import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.EnumPositionerStatus;
import gda.device.detector.areadetector.v17.ADBase;
import gda.device.enumpositioner.corba.impl.EnumpositionerAdapter;
import gda.device.enumpositioner.corba.impl.EnumpositionerImpl;
import gda.factory.FactoryException;
import gda.factory.Localizable;
import gda.factory.corba.util.CorbaAdapterClass;
import gda.factory.corba.util.CorbaImplClass;
import gda.observable.IObserver;

import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@CorbaImplClass(EnumpositionerImpl.class)
@CorbaAdapterClass(EnumpositionerAdapter.class)
public class EnumPositionerDelegator extends DeviceBase implements EnumPositioner, Localizable{
	private static final Logger logger = LoggerFactory.getLogger(EnumPositionerDelegator.class);
	Map<String, EnumPositioner> scannableMap;
	EnumPositioner delegate;
	ADBase adBase;
	private String name;
	
	
	
	public void setScannableMap(Map<String, EnumPositioner> scannableMap) {
		this.scannableMap = scannableMap;
	}

	public void setAdBase(ADBase adBase) {
		this.adBase = adBase;
	}

	public EnumPositioner getDelegate()  {
		if( delegate == null){
			delegate =scannableMap.values().toArray(new EnumPositioner[0])[0];
			try {
				delegate = scannableMap.get(adBase.getModel_RBV());
			} catch (Exception e) {
				logger.error("Error setting delegate for '" + getName() + ".", e);
			}
		}
		return delegate;
	}
	
	@Override
	public void setName(String name) {
		this.name = name;
	}
	@Override
	public void reconfigure() throws FactoryException {
		getDelegate().reconfigure();
	}
	@Override
	public Object getPosition() throws DeviceException {
		return getDelegate().getPosition();
	}
	@Override
	public String getName() {
		return name;
	}
	@Override
	public void addIObserver(IObserver observer) {
		getDelegate().addIObserver(observer);
	}
	@Override
	public void setAttribute(String attributeName, Object value) throws DeviceException {
		getDelegate().setAttribute(attributeName, value);
	}
	@Override
	public String[] getPositions() throws DeviceException {
		return getDelegate().getPositions();
	}
	@Override
	public void deleteIObserver(IObserver observer) {
		getDelegate().deleteIObserver(observer);
	}
	@Override
	public String toString() {
		return getDelegate().toString();
	}
	@Override
	public EnumPositionerStatus getStatus() throws DeviceException {
		return getDelegate().getStatus();
	}
	@Override
	public void deleteIObservers() {
		getDelegate().deleteIObservers();
	}
	@Override
	public Object getAttribute(String attributeName) throws DeviceException {
		return getDelegate().getAttribute(attributeName);
	}
	@Override
	public void moveTo(Object position) throws DeviceException {
		getDelegate().moveTo(position);
	}
	@Override
	public void stop() throws DeviceException {
		getDelegate().stop();
	}
	@Override
	public void asynchronousMoveTo(Object position) throws DeviceException {
		getDelegate().asynchronousMoveTo(position);
	}
	@Override
	public void close() throws DeviceException {
		getDelegate().close();
	}
	@Override
	public void setProtectionLevel(int newLevel) throws DeviceException {
		getDelegate().setProtectionLevel(newLevel);
	}
	@Override
	public String checkPositionValid(Object position) throws DeviceException {
		return getDelegate().checkPositionValid(position);
	}
	@Override
	public int getProtectionLevel() throws DeviceException {
		return getDelegate().getProtectionLevel();
	}
	@Override
	public boolean isBusy() throws DeviceException {
		return getDelegate().isBusy();
	}
	@Override
	public void waitWhileBusy() throws DeviceException, InterruptedException {
		getDelegate().waitWhileBusy();
	}
	@Override
	public boolean isAt(Object positionToTest) throws DeviceException {
		return getDelegate().isAt(positionToTest);
	}
	@Override
	public void setLevel(int level) {
		getDelegate().setLevel(level);
	}
	@Override
	public int getLevel() {
		return getDelegate().getLevel();
	}
	@Override
	public String[] getInputNames() {
		return getDelegate().getInputNames();
	}
	@Override
	public void setInputNames(String[] names) {
		getDelegate().setInputNames(names);
	}
	@Override
	public String[] getExtraNames() {
		return getDelegate().getExtraNames();
	}
	@Override
	public void setExtraNames(String[] names) {
		getDelegate().setExtraNames(names);
	}
	@Override
	public void setOutputFormat(String[] names) {
		getDelegate().setOutputFormat(names);
	}
	@Override
	public String[] getOutputFormat() {
		return getDelegate().getOutputFormat();
	}
	@SuppressWarnings("deprecation")
	@Override
	public void atStart() throws DeviceException {
		getDelegate().atStart();
	}
	@SuppressWarnings("deprecation")
	@Override
	public void atEnd() throws DeviceException {
		getDelegate().atEnd();
	}
	@Override
	public void atScanStart() throws DeviceException {
		getDelegate().atScanStart();
	}
	@Override
	public void atScanEnd() throws DeviceException {
		getDelegate().atScanEnd();
	}
	@Override
	public void atScanLineStart() throws DeviceException {
		getDelegate().atScanLineStart();
	}
	@Override
	public void atScanLineEnd() throws DeviceException {
		getDelegate().atScanLineEnd();
	}
	@Override
	public void atPointStart() throws DeviceException {
		getDelegate().atPointStart();
	}
	@Override
	public void atPointEnd() throws DeviceException {
		getDelegate().atPointEnd();
	}
	@Override
	public void atLevelMoveStart() throws DeviceException {
		getDelegate().atLevelMoveStart();
	}
	@Override
	public void atLevelStart() throws DeviceException {
		getDelegate().atLevelStart();
	}
	@Override
	public void atLevelEnd() throws DeviceException {
		getDelegate().atLevelEnd();
	}
	@Override
	public void atCommandFailure() throws DeviceException {
		getDelegate().atCommandFailure();
	}
	@Override
	public String toFormattedString() {
		return getDelegate().toFormattedString();
	}

	@Override
	public void setLocal(boolean local) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public boolean isLocal() {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public void configure() throws FactoryException {
		// TODO Auto-generated method stub
		
	}
	

}
