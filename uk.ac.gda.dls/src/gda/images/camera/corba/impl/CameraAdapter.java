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

import gda.device.DeviceException;
import gda.device.corba.CorbaDeviceException;
import gda.device.corba.impl.DeviceAdapter;
import gda.factory.corba.util.NetService;
import gda.images.camera.Camera;
import gda.images.camera.CameraUtils;
import gda.images.camera.corba.CorbaCamera;
import gda.images.camera.corba.CorbaCameraHelper;

import java.awt.image.BufferedImage;

import org.omg.CORBA.Any;
import org.omg.CORBA.COMM_FAILURE;
import org.omg.CORBA.TRANSIENT;

/**
 * A client side implementation of the adapter pattern for the Camera class
 */
public class CameraAdapter extends DeviceAdapter implements Camera {
	private CorbaCamera corbaCamera;

	/**
	 * Create client side interface to the CORBA package.
	 * 
	 * @param obj
	 *            the CORBA object
	 * @param name
	 *            the name of the object
	 * @param netService
	 *            the CORBA naming service
	 */
	public CameraAdapter(org.omg.CORBA.Object obj, String name, NetService netService) {
		super(obj, name, netService);
		corbaCamera = CorbaCameraHelper.narrow(obj);
		this.netService = netService;
		this.name = name;
	}

	@Override
	public String getImageFileName() throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				return corbaCamera.getImageFileName();
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public String getCameraName() throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				return corbaCamera.getCameraName();
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public double getMicronsPerXPixel() throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				return corbaCamera.getMicronsPerXPixel();
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public double getMicronsPerYPixel() throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				return corbaCamera.getMicronsPerYPixel();
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public double getFocus() throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				return corbaCamera.getFocus();
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public double getZoom() throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				return corbaCamera.getZoom();
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public void setZoom(double zoom) throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				corbaCamera.setZoom(zoom);
				return;
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public void setFocus(double focus) throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				corbaCamera.setFocus(focus);
				return;
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public void captureImage(String fileName) throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				corbaCamera.captureImage(fileName);
				return;
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}
	
	@Override
	public BufferedImage getImage() throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				final Any any = corbaCamera.getImage();
				final byte[] imageData = (byte[]) any.extract_Value();
				final BufferedImage image = CameraUtils.convertByteArrayToBufferedImage(imageData);
				return image;
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public double[] getZoomLevels() throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				return corbaCamera.getZoomLevels();
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}

	@Override
	public double[] getFocusLevels() throws DeviceException {
		for (int i = 0; i < NetService.RETRY; i++) {
			try {
				return corbaCamera.getFocusLevels();
			} catch (COMM_FAILURE cf) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (TRANSIENT ct) {
				corbaCamera = CorbaCameraHelper.narrow(netService.reconnect(name));
			} catch (CorbaDeviceException e) {
				throw new DeviceException(e.message);
			}
		}
		throw new DeviceException("Communication failure: retry failed");
	}
}
