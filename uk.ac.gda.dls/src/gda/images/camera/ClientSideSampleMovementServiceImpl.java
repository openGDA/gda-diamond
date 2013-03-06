/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

import gda.device.DeviceException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

/**
 * Service that can move a sample using pixels.
 */
public class ClientSideSampleMovementServiceImpl implements ClientSideSampleMovementService, InitializingBean {
	
	private static final Logger logger = LoggerFactory.getLogger(ClientSideSampleMovementServiceImpl.class);
	
	private Boolean gonioOnLeftOfImage;
	
	/**
	 * Sets whether the image is shown with the sample coming into the image from the left. This setting is taken into
	 * account when an on-screen movement is requested: the horizontal movement may be negated when converting from
	 * an on-screen movement in pixels to a real-world movement in microns.
	 */
	public void setGonioOnLeftOfImage(boolean gonioOnLeftOfImage) {
		this.gonioOnLeftOfImage = gonioOnLeftOfImage;
	}
	
	private ImageScaleProvider imageScaleProvider;
	
	/**
	 * Sets the {@link ImageScaleProvider} instance that is used to convert a move in pixels to a move in microns.
	 */
	public void setImageScaleProvider(ImageScaleProvider imageScaleProvider) {
		this.imageScaleProvider = imageScaleProvider;
	}
	
	private SampleMovementService sampleMovementService;
	
	public void setSampleMovementService(SampleMovementService sampleMovementService) {
		this.sampleMovementService = sampleMovementService;
	}
	
	@Override
	public void afterPropertiesSet() throws Exception {
		if (gonioOnLeftOfImage == null) {
			throw new IllegalArgumentException("The 'gonioOnLeftOfImage' property is required");
		}
		if (imageScaleProvider == null) {
			throw new IllegalArgumentException("The 'imageScaleProvider' property is required");
		}
		if (sampleMovementService == null) {
			throw new IllegalArgumentException("The 'sampleMovementService' property is required");
		}
	}
	
	@Override
	public void moveSampleByPixels(int x, int y) throws DeviceException {
		logger.debug(String.format("move in pixels: (x=%d, y=%d)", x, y));
		
		if (!gonioOnLeftOfImage) {
			x = -x;
		}
		
		final double micronsPerXPixel = imageScaleProvider.getMicronsPerXPixel();
		final double micronsPerYPixel = imageScaleProvider.getMicronsPerYPixel();
		logger.debug("image scale is (%.2f, %.2f)", micronsPerXPixel, micronsPerYPixel);
		
		final double h = x * micronsPerXPixel;
		final double v = y * micronsPerYPixel;
		final double b = 0;
		
		sampleMovementService.moveSampleByMicrons(h, v, b);
	}
	
	@Override
	public void moveSampleByMicrons(double h, double v, double b) throws DeviceException {
		if (!gonioOnLeftOfImage) {
			h = -h;
		}
		sampleMovementService.moveSampleByMicrons(h, v, b);
	}
	
}
