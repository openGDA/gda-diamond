/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.images.camera.corba.impl;

import java.awt.image.BufferedImage;

import org.omg.CORBA.Any;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.corba.CorbaDeviceException;
import gda.device.corba.impl.DeviceImpl;
import gda.factory.corba.CorbaFactoryException;
import gda.images.camera.Camera;
import gda.images.camera.CameraUtils;
import gda.images.camera.corba.CorbaCameraPOA;

/**
 * A server side implementation for a distributed Camera class
 */
public class CameraImpl extends CorbaCameraPOA {
	private static final Logger logger = LoggerFactory.getLogger(CameraImpl.class);
	//
	// Private reference to implementation object
	//
	private Camera camera;

	private DeviceImpl deviceImpl;

	//
	// Private reference to POA
	//
	private org.omg.PortableServer.POA poa;

	/**
	 * Create server side implementation to the CORBA package.
	 *
	 * @param camera
	 *            the Camera implementation object
	 * @param poa
	 *            the portable object adapter
	 */
	public CameraImpl(Camera camera, org.omg.PortableServer.POA poa) {
		this.camera = camera;
		this.poa = poa;
		deviceImpl = new DeviceImpl(camera, poa);
	}

	/**
	 * Get the implementation object
	 *
	 * @return the Camera implementation object
	 */
	public Camera _delegate() {
		return camera;
	}

	/**
	 * Set the implementation object.
	 *
	 * @param camera
	 *            set the Camera implementation object
	 */
	public void _delegate(Camera camera) {
		this.camera = camera;
	}

	@Override
	public org.omg.PortableServer.POA _default_POA() {
		return (poa != null) ? poa : super._default_POA();
	}

	//
	// gda.image.sampleChanger Camera Class Methods.
	//

	@Override
	public String getImageFileName() throws CorbaDeviceException {
		try {
			return camera.getImageFileName();
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public String getCameraName() throws CorbaDeviceException {
		try {
			return camera.getCameraName();
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public double getMicronsPerXPixel() throws CorbaDeviceException {
		try {
			return camera.getMicronsPerXPixel();
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public double getMicronsPerYPixel() throws CorbaDeviceException {
		try {
			return camera.getMicronsPerYPixel();
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public double getFocus() throws CorbaDeviceException {
		try {
			return camera.getFocus();
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public double getZoom() throws CorbaDeviceException {
		try {
			return camera.getZoom();
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public void setZoom(double zoom) throws CorbaDeviceException {
		try {
			camera.setZoom(zoom);
			return;
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public void setFocus(double focus) throws CorbaDeviceException {
		try {
			camera.setFocus(focus);
			return;
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public void captureImage(String fileName) throws CorbaDeviceException {
		try {
			camera.captureImage(fileName);
			return;
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public Any getImage() throws CorbaDeviceException {
		final Any any = org.omg.CORBA.ORB.init().create_any();
		try {
			final BufferedImage image = camera.getImage();
			final byte[] imageData = CameraUtils.convertBufferedImageToByteArray(image);
			any.insert_Value(imageData);
			return any;
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public void setAttribute(String attributeName, org.omg.CORBA.Any value) throws CorbaDeviceException {
		deviceImpl.setAttribute(attributeName, value);
	}

	@Override
	public org.omg.CORBA.Any getAttribute(String attributeName) throws CorbaDeviceException {
		return deviceImpl.getAttribute(attributeName);
	}

	@Override
	public double[] getZoomLevels() throws CorbaDeviceException {
		try {
			return camera.getZoomLevels();
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public double[] getFocusLevels() throws CorbaDeviceException {
		try {
			return camera.getFocusLevels();
		} catch (Exception ex) {
			logger.error(ex.getMessage(),ex);
			throw new CorbaDeviceException(ex.getMessage());
		}
	}

	@Override
	public void configure() throws CorbaFactoryException {
		deviceImpl.configure();
	}

	@Override
	public boolean isConfigured() throws CorbaDeviceException {
		return deviceImpl.isConfigured();
	}

	@Override
	public void reconfigure() throws CorbaFactoryException {
		deviceImpl.reconfigure();
	}

	@Override
	public void close() throws CorbaDeviceException {
		deviceImpl.close();
	}

	@Override
	public int getProtectionLevel() throws CorbaDeviceException {
		return deviceImpl.getProtectionLevel();
	}

	@Override
	public void setProtectionLevel(int newLevel) throws CorbaDeviceException {
		deviceImpl.setProtectionLevel(newLevel);
	}
}
