/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

import gda.epics.LazyPVFactory;
import gda.epics.PV;

import java.io.IOException;

import org.eclipse.swt.graphics.ImageData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class I18MotionJpegOverHttpReceiverSwt extends MotionJpegOverHttpReceiverSwt {

	private static final Logger logger = LoggerFactory.getLogger(I18MotionJpegOverHttpReceiverSwt.class);
	ImageData data;
	private PV<Integer> acquirePV;
	
	public I18MotionJpegOverHttpReceiverSwt() {
		super();
		acquirePV = LazyPVFactory.newIntegerPV("BL18I-DI-DCAM-01:CAM:CAM:Acquire");
	}
	
	@Override
	public void start() {
		try {
			acquirePV.putWait(1);
		} catch (IOException e1) {
			logger.error("Exception whiole trying to start the Motion JPEG strem", e1);
		}
	}

	@Override
	public void stop() {
		try {
			acquirePV.putWait(0);
		} catch (IOException e1) {
			logger.error("Exception whiole trying to start the Motion JPEG strem", e1);
		}
	}

}
