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

package gda.images.camera;

import java.awt.image.BufferedImage;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.io.Writer;
import java.net.Socket;
import java.util.ArrayList;
import java.util.StringTokenizer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Motor;
import gda.device.MotorException;
import gda.device.MotorStatus;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.util.Unix;

/**
 * Operate a Firewire camera using system calls via gda.utils.Unix.
 */
public class FirewireCamera extends CameraBase {

	private static final Logger logger = LoggerFactory.getLogger(FirewireCamera.class);

	private double focus = 1.0;

	private double zoom = 1.0;

	private int serverPort;

	private final String GET_IMAGE_COMMAND = "grab";

	private final int DELIMITER = '\n';

	private final int READ_TIMEOUT = 5000;

	private final int LINEFEED = 10;

	private final int ZOOM = 0;

	private final int FOCUS = 1;

	private Motor zoomMotor = null;

	private Motor focusMotor = null;

	private String focusMotorName;

	private String zoomMotorName;

	private ArrayList<String> zoomPositionList = new ArrayList<String>();

	private ArrayList<String> focusPositionList = new ArrayList<String>();

	private int zoomSteps;

	private int focusSteps;

	private double[] zoomPositions;

	private int[] zoomStepPositions;

	private double[] focusPositions;

	private int[] focusStepPositions;

	private StringTokenizer st = null;

	private String s1 = null;

	private String s2 = null;

	protected double micronsPerXPixel = 1.0;

	protected double micronsPerYPixel = 1.0;

	/**
	 * Constructor.
	 */
	public FirewireCamera() {
	}

	public void setMicronsPerXPixel(double micronsPerXPixel) {
		this.micronsPerXPixel = micronsPerXPixel;
	}

	public void setMicronsPerYPixel(double micronsPerYPixel) {
		this.micronsPerYPixel = micronsPerYPixel;
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		extractPositions(zoomPositionList, ZOOM);
		extractPositions(focusPositionList, FOCUS);

		zoomMotor = Finder.find(zoomMotorName);
		focusMotor = Finder.find(focusMotorName);
		if (zoomMotor == null || focusMotor == null) {
			throw new FactoryException("FirewireCamera : error finding zoom/focus motors");
		}

		try {
			Unix.stopFirewireCameraDaemon();
			Unix.startFirewireCameraDaemon();
		} catch (Exception e) {
			throw new FactoryException("Error configuring FirewireCamera" ,e);
		}
		setConfigured(true);
	}

	private void extractPositions(ArrayList<String> positionList, int type) {
		int steps = positionList.size();
		double[] positions = new double[steps];
		int[] stepPositions = new int[steps];
		switch (type) {
		case ZOOM:
			zoomSteps = steps;
			zoomPositions = positions;
			zoomStepPositions = stepPositions;
			break;
		case FOCUS:
			focusSteps = steps;
			focusPositions = positions;
			focusStepPositions = stepPositions;
			break;
		}
		steps = 0;

		for (int i = 0; i < positionList.size(); i++) {
			st = new StringTokenizer(positionList.get(i), " =,");
			s1 = null;
			s2 = null;
			if (st.hasMoreTokens())
				s1 = st.nextToken();
			if (st.hasMoreTokens())
				s2 = st.nextToken();
			if (s1 != null && s2 != null) {
				try {
					positions[steps] = Double.parseDouble(s1);
					stepPositions[steps] = Integer.parseInt(s2);
					steps++;
				} catch (NumberFormatException nfex) {
				}
			}
		}
	}

	@Override
	public String getImageFileName() throws DeviceException {
		return imageFile;
	}

	@Override
	public double getFocus() throws DeviceException {
		return focus;
	}

	@Override
	public double getZoom() throws DeviceException {
		return zoom;
	}

	@Override
	public void setZoom(double zoom) throws DeviceException {
		int i;

		for (i = 0; i < zoomSteps; i++) {
			if (zoom == zoomPositions[i]) {
				// TODO: allow tolerance in double comparison
				try {
					zoomMotor.setSpeedLevel(Motor.FAST);
					zoomMotor.moveTo(zoomStepPositions[i]);
					this.zoom = zoom;
					while (zoomMotor.getStatus() == MotorStatus.BUSY) {
						Thread.sleep(100);
					}
				} catch (MotorException e) {
					logger.error("Error moving camera zoom motor");
				} catch (InterruptedException e) {
					Thread.currentThread().interrupt();
					String msg = getName() + " - Thread interrupted waiting for camera to zoom";
					logger.error(msg, e);
					throw new DeviceException(msg, e);
				}
				break;
			}
		}
	}

	@Override
	public void setFocus(double focus) throws DeviceException {
		int i;

		for (i = 0; i < focusSteps; i++) {
			if (focus == focusPositions[i]) {
				// TODO: allow tolerance in double comparison
				try {
					focusMotor.setSpeedLevel(Motor.FAST);
					focusMotor.moveTo(focusStepPositions[i]);
					while (focusMotor.getStatus() == MotorStatus.BUSY) {
						Thread.sleep(100);
					}
					this.focus = focus;
				} catch (MotorException e) {
					logger.error("Error moving camera zoom motor");
					throw new DeviceException("Error moving camera zoom motor - {}", getName(), e);
				} catch (InterruptedException e) {
					Thread.currentThread().interrupt();
					String msg = getName() + " - Thread interrupted waiting for camera to focus";
					logger.error(msg, e);
					throw new DeviceException(msg, e);
				}
				break;
			}
		}
	}

	@Override
	public void captureImage(String imageName) throws DeviceException {
		Socket socket = null;
		Writer out = null;
		Reader in = null;

		try {
			socket = new Socket("localhost", serverPort);
			socket.setSoTimeout(READ_TIMEOUT);
			out = new OutputStreamWriter(socket.getOutputStream());
			in = new InputStreamReader(socket.getInputStream());

			if (imageName == null) {
				out.write(GET_IMAGE_COMMAND + " " + imageFile);
			} else {
				out.write(GET_IMAGE_COMMAND + " " + imageName);
			}
			out.write(DELIMITER);
			out.flush();

			int c;
			do {
				c = in.read();
			} while (c != LINEFEED);

			socket.close();
		} catch (Exception e) {
			logger.debug("ERROR SENDING DC1394 COMMAND");
		}

		notifyIObservers(this, IMAGE_UPDATED + cameraName);
	}

	@Override
	public BufferedImage getImage() {
		throw new UnsupportedOperationException();
	}

	// XML getters and setters

	/**
	 * @return image file
	 */
	public String getImageFile() {
		return imageFile;
	}

	/**
	 * @return server port
	 */
	public int getServerPort() {
		return serverPort;
	}

	/**
	 * @param serverPort
	 */
	public void setServerPort(int serverPort) {
		this.serverPort = serverPort;
	}

	/**
	 * @return focus motor name
	 */
	public String getFocusMotorName() {
		return focusMotorName;
	}

	/**
	 * @param focusMotorName
	 */
	public void setFocusMotorName(String focusMotorName) {
		this.focusMotorName = focusMotorName;
	}

	/**
	 * @return zoom motor name
	 */
	public String getZoomMotorName() {
		return zoomMotorName;
	}

	/**
	 * @param zoomMotorName
	 */
	public void setZoomMotorName(String zoomMotorName) {
		this.zoomMotorName = zoomMotorName;
	}

	/**
	 * @param zoomPosition
	 */
	public void addZoomPosition(String zoomPosition) {
		zoomPositionList.add(zoomPosition);
	}

	/**
	 * @return zoom position list
	 */
	public ArrayList<String> getZoomPositionList() {
		return zoomPositionList;
	}

	/**
	 * @param focusPosition
	 */
	public void addFocusPosition(String focusPosition) {
		focusPositionList.add(focusPosition);
	}

	/**
	 * @return focus poisition list
	 */
	public ArrayList<String> getFocusPositionList() {
		return focusPositionList;
	}

	@Override
	public double[] getZoomLevels() throws DeviceException {
		return zoomPositions;
	}

	@Override
	public double[] getFocusLevels() throws DeviceException {
		return focusPositions;
	}

	@Override
	public double getMicronsPerXPixel() {
		return micronsPerXPixel;
	}

	@Override
	public double getMicronsPerYPixel() {
		return micronsPerYPixel;
	}

}
