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

import java.io.IOException;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.FileConfiguration;

import gda.images.camera.BeamDataComponent.BeamData;
import uk.ac.diamond.daq.persistence.jythonshelf.LocalParameters;

/**
 * Singleton object which, given the location on a image of the sample in pixels, returns where an xyz stage supporting
 * the sample should move to so that whatever was at that pixel location is now in the beam.
 * <p>
 * This relies on the data file and objects use by the BeamDataComponent class working properly.
 * <p>
 * This also relies on a correct calibration file.
 * <p>
 * NOT IN USE AT THE MOMENT!! This is for a possible upgrade to sample viewing camera calibrations only
 */
public class PixelToMicronConvertor {

	static final String CONFIGFILENAME = "sampleDisplayConfiguration";

	static final double IMAGEPIXELWIDTH = 1024;

	static final double IMAGEPIXELHEIGHT = 768;

	static PixelToMicronConvertor theInstance = null;

	BeamDataComponent beamDataStore = BeamDataComponent.getInstance();

	/**
	 * @return the singleton PixelToMicronConvertor object
	 */
	public static PixelToMicronConvertor getInstance() {

		if (theInstance == null) {
			theInstance = new PixelToMicronConvertor();
		}

		return theInstance;

	}

	/**
	 * Given a pixel location, returns the three element array required to move an object at that
	 * point into the beam.
	 *
	 * @param xPixel
	 * @param yPixel
	 * @return the micron movement required
	 * @throws IOException
	 * @throws ConfigurationException
	 */
	public double[] movePointToBeam(int xPixel, int yPixel) throws ConfigurationException, IOException {

		// reread the file in case the GUI panel has updated it
		beamDataStore.refreshBeamData();

		// get the current beam data
		BeamData currentBeamData = beamDataStore.getCurrentBeamData();
		String zoomLevelString = currentBeamData.zoomLevel.toString();

		// determine the calibration vectors for this zoom level and the beam's
		// location in pixels
		FileConfiguration configFile = LocalParameters.getXMLConfiguration(CONFIGFILENAME);

		// get the xyz coordinates of the top-left, top-right and bottom-left
		// corners of the image.
		// The movement will be based on those vectors, but normalised by the
		// size of the image in pixels.
		int tlX = configFile.getInt(zoomLevelString + ".tlX");
		int tlY = configFile.getInt(zoomLevelString + ".tlY");
		int tlZ = configFile.getInt(zoomLevelString + ".tlZ");
		int trX = configFile.getInt(zoomLevelString + ".trX");
		int trY = configFile.getInt(zoomLevelString + ".trY");
		int trZ = configFile.getInt(zoomLevelString + ".trZ");
		int blX = configFile.getInt(zoomLevelString + ".blX");
		int blY = configFile.getInt(zoomLevelString + ".blY");
		int blZ = configFile.getInt(zoomLevelString + ".blZ");

		// calculate the micron move in each axis:
		double x = ((currentBeamData.xCentre - xPixel) / IMAGEPIXELWIDTH) * (trX - tlX)
				+ ((currentBeamData.yCentre - yPixel) / IMAGEPIXELHEIGHT) * (blX - tlX);
		double y = ((currentBeamData.xCentre - xPixel) / IMAGEPIXELWIDTH) * (trY - tlY)
				+ ((currentBeamData.yCentre - yPixel) / IMAGEPIXELHEIGHT) * (blY - tlY);
		double z = ((currentBeamData.xCentre - xPixel) / IMAGEPIXELWIDTH) * (trZ - tlZ)
				+ ((currentBeamData.yCentre - yPixel) / IMAGEPIXELHEIGHT) * (blZ - tlZ);

		return new double[] { x, y, z };

	}
}
