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
import gda.device.scannable.corba.impl.ScannableAdapter;
import gda.device.scannable.corba.impl.ScannableImpl;
import gda.factory.FactoryException;
import gda.factory.corba.util.CorbaAdapterClass;
import gda.factory.corba.util.CorbaImplClass;
import gda.observable.IObserver;
import gda.util.persistence.LocalParameters;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.FileConfiguration;
import org.springframework.beans.factory.InitializingBean;

@CorbaImplClass(ScannableImpl.class)
@CorbaAdapterClass(ScannableAdapter.class)
public class CameraXYScannable extends ScannableBase implements InitializingBean {
	// private static final Logger logger = LoggerFactory.getLogger(CameraXYScannable.class);

	private FileConfiguration configuration;
	Scannable lensScannable;
	private String configurationName = "configuration";
	private String propertyNameX = "cameraXYScannableOffsetX";
	private String propertyNameY = "cameraXYScannableOffsetY";

	Scannable cameraStageXScannable;
	Scannable cameraStageYScannable;
	DisplayScaleProvider cameraScaleProvider;
	private IObserver observer;

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	private String getLensValue() throws DeviceException {
		return (String) lensScannable.getPosition();
	}

	private void setOffset(double offsetX, double offsetY) throws DeviceException, ConfigurationException {
		String lensPos = getLensValue();
		configuration.setProperty(getAllowedKey(propertyNameX + lensPos), offsetX);
		configuration.setProperty(getAllowedKey(propertyNameY + lensPos), offsetY);
		configuration.save();
	}

	String getAllowedKey(String key) {
		return key.replace(" ", "_");
	}

	private double getOffsetX() throws DeviceException {
		String lensPos = getLensValue();
		double offset = configuration.getDouble(getAllowedKey(propertyNameX + lensPos), 0.0);
		return offset;
	}

	private double getOffsetY() throws DeviceException {
		String lensPos = getLensValue();
		double offset = configuration.getDouble(getAllowedKey(propertyNameY + lensPos), 0.0);
		return offset;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		try {
			Double[] array = ScannableUtils.objectToArray(position);
			double offsetX = getOffsetXForRotationAxisX(array[0]);
			double offsetY = getOffsetYForRotationAxisX(array[1]);
			setOffset(offsetX, offsetY);
			notifyIObservers(getName(), new ScannablePositionChangeEvent(new double[] { offsetX, offsetY }));
		} catch (ConfigurationException e) {
			throw new DeviceException("Error saving new value", e);
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return new double[] { getRotationAxisX(), getRotationAxisY() };
	}

	@Override
	public void configure() throws FactoryException {
		super.configure();
		setInputNames(new String[] { "X", "Y" });
		try {
			configuration = LocalParameters.getThreadSafeXmlConfiguration(getConfigurationName());
			if (observer == null) {
				observer = new IObserver() {

					@Override
					public void update(Object source, Object arg) {
						if (arg instanceof ScannableStatus) {
							notifyIObservers(CameraXYScannable.this, new ScannableStatus(getName(), ((ScannableStatus) arg).status));
						} else if (arg instanceof ScannablePositionChangeEvent) {
							notifyIObservers(CameraXYScannable.this, arg);
						}
					}
				};
				lensScannable.addIObserver(observer);
				cameraStageXScannable.addIObserver(observer);
				cameraStageYScannable.addIObserver(observer);
				cameraScaleProvider.addIObserver(observer);
			}
		} catch (Exception e) {
			throw new FactoryException("Error in configure for " + getName(), e);
		}

	}

	int getRotationAxisX() throws DeviceException {
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageXScannable)[0];
		double dist = getOffsetX() - x2;
		double a = dist * cameraScaleProvider.getPixelsPerMMInX();
		return (int) Math.round(a);
	}

	int getRotationAxisY() throws DeviceException {
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageYScannable)[0];
		double dist = getOffsetY() - x2;
		double a = dist * cameraScaleProvider.getPixelsPerMMInY();
		return (int) Math.round(a);
	}

	double getOffsetXForRotationAxisX(double array) throws DeviceException {
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageXScannable)[0];
		return (array / cameraScaleProvider.getPixelsPerMMInX() + x2);
	}

	double getOffsetYForRotationAxisX(double array) throws DeviceException {
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageYScannable)[0];
		return (array / cameraScaleProvider.getPixelsPerMMInY() + x2);
	}

	public void autoCentre(double pixelsX, double pixelsY) throws DeviceException, InterruptedException {
		cameraStageXScannable.asynchronousMoveTo(pixelsX / cameraScaleProvider.getPixelsPerMMInX() - getOffsetX());
		cameraStageYScannable.asynchronousMoveTo(pixelsY / cameraScaleProvider.getPixelsPerMMInY() - getOffsetY());
		cameraStageXScannable.waitWhileBusy();
		cameraStageYScannable.waitWhileBusy();

	}

	@Override
	public void afterPropertiesSet() throws Exception {

		if (cameraStageXScannable == null) {
			throw new Exception("cameraStageXScannable == null");
		}
		if (cameraStageYScannable == null) {
			throw new Exception("cameraStageYScannable == null");
		}
		if (cameraScaleProvider == null) {
			throw new Exception("cameraScaleProvider == null");
		}
		if (lensScannable == null) {
			throw new Exception("lensScannable == null");
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

	public Scannable getLensScannable() {
		return lensScannable;
	}

	public void setLensScannable(Scannable lensScannable) {
		this.lensScannable = lensScannable;
	}
}
