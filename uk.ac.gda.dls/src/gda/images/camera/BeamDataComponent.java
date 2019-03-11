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

import static gda.configuration.properties.LocalProperties.isDummyModeEnabled;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.List;
import java.util.Vector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.factory.FindableConfigurableBase;
import gda.factory.Finder;
import gda.observable.IObservable;
import gda.observable.IObserver;
import gda.observable.ObservableComponent;

/**
 * Reads and saves the data which describes the various zoom levels of a gda.images.camera object.
 */
public class BeamDataComponent extends FindableConfigurableBase implements IObservable {

	private static final Logger logger = LoggerFactory.getLogger(BeamDataComponent.class);

	private static String INSTANCE_NAME = "BeamDataComponent";
	private static BeamDataComponent theInstance;

	// read in from the beamData file
	private List<BeamData> beamDataArray = new Vector<BeamData>();

	private Camera opticalCamera;

	private boolean singleBeamCenter = LocalProperties.check(LocalProperties.GDA_IMAGES_SINGLE_BEAM_CENTRE, false);

	ObservableComponent obsComp = new ObservableComponent();

	private static final String convert(int x, int y) {
		return "(" + x + ", " + y + ")";
	}

	public static class BeamData {

		public Double zoomLevel = null;

		public int xCentre;

		public int yCentre;

		public int xTopLeft;

		public int yTopLeft;

		public int xBottomRight;

		public int yBottomRight;

		@Override
		public String toString() {
			return "BeamData[zoomLevel=" + zoomLevel + ", centre=" + convert(xCentre, yCentre) + ", topleft=" + convert(xTopLeft, yTopLeft) + ", bottomright=" + convert(xBottomRight, yBottomRight) + "]";
		}
	}

	/**
	 * @return the singleton object for this class.
	 */
	public static BeamDataComponent getInstance() {
		if (theInstance == null) {
			theInstance = Finder.getInstance().findLocal(INSTANCE_NAME);
		}
		return theInstance;
	}

	/**
	 * Sets the singleton {@link BeamDataComponent}.
	 */
	public static void setInstance(BeamDataComponent component) {
		theInstance = component;
	}

	private String filename;

	/**
	 * Creates a {@link BeamDataComponent}, reading the beam data from the file specified by the
	 * {@code gda.images.displayConfigFile} property.
	 */
	public BeamDataComponent() {
		filename = LocalProperties.get(LocalProperties.GDA_IMAGES_DISPLAY_CONFIG_FILE);
		refreshBeamData();
	}

	/**
	 * @return the camera object this object refers to.
	 */
	public Camera getCamera() {
		return opticalCamera;
	}

	public static BeamDataComponent getTestingInstance(String configfile) {
		BeamDataComponent bdc = new BeamDataComponent();
		bdc.filename = configfile;
		theInstance = bdc;
		bdc.refreshBeamData();
		return bdc;
	}

	private boolean fileExists;

	/**
	 * Reads from a configuration file the beam centre and size at different zoom levels for display over the image
	 * display panel.
	 */
	public void refreshBeamData() {
		List<BeamData> newBeamData = new Vector<BeamData>();

		String line = null;

		int singleBeamX = 0;
		int singleBeamY = 0;
		boolean beamPositionXFound = false;
		boolean beamPositionYFound = false;

		if (filename != null) {
			try {
				File file = new File(filename);

				fileExists = (file.exists());
				if (!fileExists) {

					if (isDummyModeEnabled()) {
						logger.info(filename + " does not exist; will create dummy beam data for all zoom levels");
					}

					else {
						logger.warn(filename + " does not exist");
					}
				}

				else {
					logger.debug("Reading display config from " + filename);

					BufferedReader reader = new BufferedReader(new FileReader(file));
					BeamData currentData = new BeamData();
					while ((line = reader.readLine()) != null) {

						if (line.startsWith("zoomLevel")) {
							// then we must have just completed a zoom level, so
							// record
							// the old one
							if (currentData.zoomLevel != null) {
								newBeamData.add(currentData);
							}
							// reset the current data object
							currentData = new BeamData();
							currentData.zoomLevel = Double.parseDouble(line.substring(line.indexOf("=") + 2));
						}

						else if (line.startsWith("crosshairX")) {
							if (!singleBeamCenter) {
								currentData.xCentre = Integer.parseInt(line.substring(line.indexOf("=") + 2));
							} else {
								if (!beamPositionXFound) {
									singleBeamX = Integer.parseInt(line.substring(line.indexOf("=") + 2));
									beamPositionXFound = true;
								}
							}
						}

						else if (line.startsWith("crosshairY")) {
							if (!singleBeamCenter) {
								currentData.yCentre = Integer.parseInt(line.substring(line.indexOf("=") + 2));
							} else {
								if (!beamPositionYFound) {
									singleBeamY = Integer.parseInt(line.substring(line.indexOf("=") + 2));
									beamPositionYFound = true;
								}
							}
						}

						else if (line.startsWith("topLeftX")) {
							currentData.xTopLeft = Integer.parseInt(line.substring(line.indexOf("=") + 2));
						}

						else if (line.startsWith("topLeftY")) {
							currentData.yTopLeft = Integer.parseInt(line.substring(line.indexOf("=") + 2));
						}

						else if (line.startsWith("bottomRightX")) {
							currentData.xBottomRight = Integer.parseInt(line.substring(line.indexOf("=") + 2));
						}

						else if (line.startsWith("bottomRightY")) {
							currentData.yBottomRight = Integer.parseInt(line.substring(line.indexOf("=") + 2));
						}

						if (singleBeamCenter) { // if there aren't lines containing crosshairX or crosshairY
							currentData.xCentre = singleBeamX;
							currentData.yCentre = singleBeamY;
						}
					}
					newBeamData.add(currentData);

					this.beamDataArray = newBeamData;
				}

			} catch (Exception e) {
				logger.error("Could not read display config from " + filename, e);
			}
		}
	}

	/**
	 *
	 */
	public void saveBeamData() {
		String filename = null;
		if ((filename = LocalProperties.get(LocalProperties.GDA_IMAGES_DISPLAY_CONFIG_FILE)) != null) {
			try {
				logger.debug("Writing display config to " + filename);

				File file = new File(filename);
				FileWriter writer = new FileWriter(file);

				for (BeamData beamData : this.beamDataArray) {
					writer.write("zoomLevel = " + beamData.zoomLevel + "\n");
					writer.write("crosshairX = " + beamData.xCentre + "\n");
					writer.write("crosshairY = " + beamData.yCentre + "\n");
					writer.write("topLeftX = " + beamData.xTopLeft + "\n");
					writer.write("topLeftY = " + beamData.yTopLeft + "\n");
					writer.write("bottomRightX = " + beamData.xBottomRight + "\n");
					writer.write("bottomRightY = " + beamData.yBottomRight + "\n");
				}

				writer.close();
			} catch (Exception e) {
				logger.error("Could not write display config to " + filename, e);
			}
		}
		obsComp.notifyIObservers(this, filename);
	}

	/**
	 * @return BeamData
	 */
	public BeamData getCurrentBeamData() {
		// get the zoom level
		double zoom = 0.0;
		if (opticalCamera != null) {
			try {
				zoom = opticalCamera.getZoom();
			} catch (DeviceException e) {
				logger.error("Failed to get current zoom level", e);
			}
		}

		// use this to find the beam data for this zoom level
		BeamData out = null;
		for (BeamData beamData : this.beamDataArray) {
			if (beamData != null && beamData.zoomLevel == zoom) {
				out = beamData;
			}
		}

		if ((out == null) && isDummyModeEnabled() && !fileExists) {
			logger.info(String.format("Creating dummy beam data for zoom level %.1f", zoom));
			out = createDummyBeamData(zoom);
			beamDataArray.add(out);
			return out;
		}

		// if no details found, tell the user
		if (out == null) {
			logger.error("Details for zoom level " + zoom + " not found. This could be due to inaccuracy in the camera position, or you may need to add beam data.");
		}

		return out;
	}

	private BeamData createDummyBeamData(double zoomLevel) {
		BeamData data = new BeamData();
		data.zoomLevel = zoomLevel;
		data.xCentre = 1024/2;
		data.yCentre = 768/2;
		data.xTopLeft = data.xCentre - 10;
		data.yTopLeft = data.yCentre - 10;
		data.xBottomRight = data.xCentre + 10;
		data.yBottomRight = data.yCentre + 10;
		return data;
	}

	// Spring setters
	public void setOpticalCamera(Camera opticalCamera) {
		this.opticalCamera = opticalCamera;
	}

	// IObservable
	@Override
	public void addIObserver(IObserver observer) {
		obsComp.addIObserver(observer);

	}

	@Override
	public void deleteIObserver(IObserver observer) {
		obsComp.deleteIObserver(observer);

	}

	@Override
	public void deleteIObservers() {
		obsComp.deleteIObservers();
	}

}
