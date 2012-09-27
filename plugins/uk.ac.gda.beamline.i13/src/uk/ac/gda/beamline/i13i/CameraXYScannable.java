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
import org.springframework.beans.factory.InitializingBean;

public class CameraXYScannable extends ScannableBase implements InitializingBean{
//	private static final Logger logger = LoggerFactory.getLogger(CameraXYScannable.class);
	
	
	private FileConfiguration configuration;

	private String configurationName="configuration";
	private String propertyNameX="cameraXYScannableOffsetX";
	private String propertyNameY="cameraXYScannableOffsetY";

	
	double offsetX=0.;
	double offsetY=0.;
	Scannable cameraStageXScannable;
	Scannable cameraStageYScannable;
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
			offsetX = getOffsetXForRotationAxisX(array[0]);
			configuration.setProperty(propertyNameX,offsetX);
			offsetY = getOffsetYForRotationAxisX(array[1]);
			configuration.setProperty(propertyNameY,offsetY);
			configuration.save();
			notifyIObservers(getName(), new ScannablePositionChangeEvent(new double[]{offsetX, offsetY}));
		} catch (ConfigurationException e) {
			throw new DeviceException("Error saving new value",e);
		}
	}


	@Override
	public Object rawGetPosition() throws DeviceException {
		return new double[]{getRotationAxisX(), getRotationAxisY()};
	}





	@Override
	public void configure() throws FactoryException {
		super.configure();
		setInputNames(new String[]{"X","Y"});
		try {
			configuration = LocalParameters.getThreadSafeXmlConfiguration(getConfigurationName());
			offsetX = configuration.getDouble(propertyNameX, 0.0);
			offsetY = configuration.getDouble(propertyNameY, 0.0);
			if( observer == null){
				observer = new IObserver() {
					
					@Override
					public void update(Object source, Object arg) {
						if( arg instanceof ScannableStatus){
							notifyIObservers(CameraXYScannable.this, new ScannableStatus(getName(),((ScannableStatus)arg).status ));
						}
					}
				};
				cameraStageXScannable.addIObserver(observer);
				cameraStageYScannable.addIObserver(observer);
				cameraScaleProvider.addIObserver(observer);
			}
		} catch (Exception e) {
			throw new FactoryException("Error in configure for "+getName(), e);
		}
		
	}

	int getRotationAxisX() throws DeviceException {
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageXScannable)[0];
		double dist = offsetX+x2;
		double a = dist * cameraScaleProvider.getPixelsPerMMInX();
		return (int) Math.round(a);
	}
	int getRotationAxisY() throws DeviceException {
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageYScannable)[0];
		double dist = offsetY+x2;
		double a = dist * cameraScaleProvider.getPixelsPerMMInY();
		return (int) Math.round(a);
	}

	double getOffsetXForRotationAxisX(double  array) throws DeviceException {
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageXScannable)[0];
		return (array/cameraScaleProvider.getPixelsPerMMInX() - x2);
	}
	double getOffsetYForRotationAxisX(double  array) throws DeviceException {
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageYScannable)[0];
		return (array/cameraScaleProvider.getPixelsPerMMInY() - x2);
	}
	
	
	@Override
	public void afterPropertiesSet() throws Exception {

		if(cameraStageXScannable == null){
			throw new Exception("cameraStageXScannable == null");
		}
		if(cameraStageYScannable == null){
			throw new Exception("cameraStageYScannable == null");
		}
		if(cameraScaleProvider == null){
			throw new Exception("displayScaleProvider == null");
		}
	}


	public String getConfigurationName() {
		return configurationName;
	}


	public void setConfigurationName(String configurationName) {
		this.configurationName = configurationName;
	}





	public String getPropertyNameX() {
		return propertyNameX;
	}


	public void setPropertyNameX(String propertyNameX) {
		this.propertyNameX = propertyNameX;
	}


	public String getPropertyNameY() {
		return propertyNameY;
	}


	public void setPropertyNameY(String propertyNameY) {
		this.propertyNameY = propertyNameY;
	}


	public Scannable getCameraStageYScannable() {
		return cameraStageYScannable;
	}


	public void setCameraStageYScannable(Scannable cameraStageYScannable) {
		this.cameraStageYScannable = cameraStageYScannable;
	}



	public Scannable getCameraStageXScannable() {
		return cameraStageXScannable;
	}


	public void setCameraStageXScannable(Scannable cameraStageXScannable) {
		this.cameraStageXScannable = cameraStageXScannable;
	}


	public DisplayScaleProvider getCameraScaleProvider() {
		return cameraScaleProvider;
	}


	public void setCameraScaleProvider(DisplayScaleProvider cameraScaleProvider) {
		this.cameraScaleProvider = cameraScaleProvider;
	}


}
