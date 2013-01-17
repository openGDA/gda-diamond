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

package uk.ac.gda.beamline.i13i.ADViewerImpl;

import gda.device.Scannable;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i13i.ADViewer.ADControllerImpl;

public class I13ADControllerImpl extends ADControllerImpl {
	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(I13ADControllerImpl.class);

	private Scannable lensScannable;

	public Scannable getLensScannable() {
		return lensScannable;
	}

	public void setLensScannable(Scannable lensScannable) {
		this.lensScannable = lensScannable;
	}

}
