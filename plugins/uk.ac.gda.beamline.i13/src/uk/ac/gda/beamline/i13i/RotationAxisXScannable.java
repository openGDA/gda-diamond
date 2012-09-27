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
import gda.device.scannable.ScannableBase;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.device.scannable.ScannableStatus;
import gda.device.scannable.ScannableUtils;
import gda.factory.FactoryException;
import gda.observable.IObserver;
import gda.util.persistence.LocalParameters;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.FileConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

public class RotationAxisXScannable extends ScannableBase implements InitializingBean{
//	private static final Logger logger = LoggerFactory.getLogger(RotationAxisXScannable.class);
	
	
	private FileConfiguration configuration;

	private String configurationName="configuration";
	private String propertyName="rotationXScannableOffset";

	
	double offset=0.;
	Scannable sampleStageXScannable;
	Scannable cameraStageXScannable;
	DisplayScaleProvider displayScaleProvider;
	DisplayScaleProvider cameraScaleProvider;
	private IObserver observer;

	
	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}


	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		try {
			Double[] array = ScannableUtils.objectToArray(position);
			offset = getOffsetForRotationAxisX(array[0]);
			configuration.setProperty(propertyName,offset);
			configuration.save();
			notifyIObservers(getName(), new ScannablePositionChangeEvent(offset));
		} catch (ConfigurationException e) {
			throw new DeviceException("Error saving new value",e);
		}
	}


	@Override
	public Object rawGetPosition() throws DeviceException {
		return getRotationAxisX();
	}





	@Override
	public void configure() throws FactoryException {
		super.configure();
		try {
			configuration = LocalParameters.getThreadSafeXmlConfiguration(getConfigurationName());
			offset = configuration.getDouble(propertyName, 0.0);
			if( observer == null){
				observer = new IObserver() {
					
					@Override
					public void update(Object source, Object arg) {
						if( arg instanceof ScannableStatus){
							notifyIObservers(RotationAxisXScannable.this, new ScannableStatus(getName(),((ScannableStatus)arg).status ));
						}
					}
				};
				sampleStageXScannable.addIObserver(observer);
				cameraStageXScannable.addIObserver(observer);
				displayScaleProvider.addIObserver(observer);
				cameraScaleProvider.addIObserver(observer);
				
			}
		} catch (Exception e) {
			throw new FactoryException("Error in configure for "+getName(), e);
		}
		
	}

	int getRotationAxisX() throws DeviceException {
		double x1 = ScannableUtils.getCurrentPositionArray(sampleStageXScannable)[0];
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageXScannable)[0];
		double dist = (offset-x1)*displayScaleProvider.getPixelsPerMMInX()-x2*cameraScaleProvider.getPixelsPerMMInX();
		return (int) Math.round(dist);
	}

	double getOffsetForRotationAxisX(double  array) throws DeviceException {
		double x1 = ScannableUtils.getCurrentPositionArray(sampleStageXScannable)[0];
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageXScannable)[0];
		return (array + x2*cameraScaleProvider.getPixelsPerMMInX())/displayScaleProvider.getPixelsPerMMInX() + x1;
	}
	
	
	@Override
	public void afterPropertiesSet() throws Exception {

		if(sampleStageXScannable == null){
			throw new Exception("sampleStageXScannable == null");
		}
		if(cameraStageXScannable == null){
			throw new Exception("cameraStageXScannable == null");
		}
		if(displayScaleProvider == null){
			throw new Exception("displayScaleProvider == null");
		}
	}


	public String getConfigurationName() {
		return configurationName;
	}


	public void setConfigurationName(String configurationName) {
		this.configurationName = configurationName;
	}


	public String getPropertyName() {
		return propertyName;
	}


	public void setPropertyName(String propertyName) {
		this.propertyName = propertyName;
	}


	public Scannable getSampleStageXScannable() {
		return sampleStageXScannable;
	}


	public void setSampleStageXScannable(Scannable sampleStageXScannable) {
		this.sampleStageXScannable = sampleStageXScannable;
	}


	public Scannable getCameraStageXScannable() {
		return cameraStageXScannable;
	}


	public void setCameraStageXScannable(Scannable cameraStageXScannable) {
		this.cameraStageXScannable = cameraStageXScannable;
	}


	public DisplayScaleProvider getDisplayScaleProvider() {
		return displayScaleProvider;
	}


	public void setDisplayScaleProvider(DisplayScaleProvider displayScaleProvider) {
		this.displayScaleProvider = displayScaleProvider;
	}


	public DisplayScaleProvider getCameraScaleProvider() {
		return cameraScaleProvider;
	}


	public void setCameraScaleProvider(DisplayScaleProvider cameraScaleProvider) {
		this.cameraScaleProvider = cameraScaleProvider;
	}

}
