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

package uk.ac.gda.beamline.i13i;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.observable.IObserver;
import gda.observable.ObservableComponent;

import java.util.Map;

import org.springframework.beans.factory.InitializingBean;

public class SelectableDisplayScaleProvider implements DisplayScaleProvider, InitializingBean {
//	private static final Logger logger = LoggerFactory.getLogger(SelectableDisplayScaleProvider.class);
	public static final String NEWVAL = "NEWVAL";
	ObservableComponent obsComp= new ObservableComponent();
	
	String currentKey="";
	
	Scannable keyScannable;
	Map<String , DisplayScaleProvider> providers;
	
	@Override
	public void addIObserver(IObserver anIObserver) {
		obsComp.addIObserver(anIObserver);
	}
	@Override
	public void deleteIObserver(IObserver anIObserver) {
		obsComp.deleteIObserver(anIObserver);
	}
	@Override
	public void deleteIObservers() {
		obsComp.deleteIObservers();
	}

	
	@Override
	public double getPixelsPerMMInX() throws DeviceException {
		return getProvider().getPixelsPerMMInX();
	}
	@Override
	public double getPixelsPerMMInY() throws DeviceException {
		return getProvider().getPixelsPerMMInY();
	}
	
	
	DisplayScaleProvider getProvider() throws DeviceException{
		currentKey = Double.valueOf(ScannableUtils.getCurrentPositionArray(keyScannable)[0]).toString();
		DisplayScaleProvider currentProvider = providers.get(currentKey);
		if( currentProvider == null)
			throw new DeviceException("Unable to get provider from map. key="+currentKey);
		return currentProvider;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if( keyScannable ==null)
			throw new Exception("keyScannable==null");
		if( providers ==null)
			throw new Exception("providers==null");
		
		if(keyScannable != null){
			keyScannable.addIObserver(new IObserver() {
				
				@Override
				public void update(Object source, Object arg) {
					obsComp.notifyIObservers(SelectableDisplayScaleProvider.this, NEWVAL);
				}
			});
		}
		
		
	}
	public Scannable getKeyScannable() {
		return keyScannable;
	}
	public void setKeyScannable(Scannable keyScannable) {
		this.keyScannable = keyScannable;
	}
	public Map<String, DisplayScaleProvider> getProviders() {
		return providers;
	}
	public void setProviders(Map<String, DisplayScaleProvider> providers) {
		this.providers = providers;
	}
	

}
