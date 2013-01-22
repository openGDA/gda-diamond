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
import gda.jython.InterfaceProvider;
import gda.rcp.views.CompositeFactory;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import uk.ac.gda.epics.adviewer.ADControllerImpl;

public class I13ADControllerImpl extends  ADControllerImpl implements InitializingBean {
	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(I13ADControllerImpl.class);

	private String setExposureTimeCmd;

	@Override
	public void setExposure(double d) {
		final String cmd = String.format(getSetExposureTimeCmd(), d);
		InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
	}

	private String getSetExposureTimeCmd() {
		return setExposureTimeCmd;
	}

	public void setSetExposureTimeCmd(String setExposureTimeCmd) {
		this.setExposureTimeCmd = setExposureTimeCmd;
	}

	private Scannable lensScannable;

	private CompositeFactory compositeFactory;

	public Scannable getLensScannable() {
		return lensScannable;
	}

	public void setLensScannable(Scannable lensScannable) {
		this.lensScannable = lensScannable;
	}


	@Override
	public void afterPropertiesSet() throws Exception {
		if (setExposureTimeCmd == null)
			throw new IllegalArgumentException("setExposureTimeCmd == null");		
		
	}

	public CompositeFactory getCompositeFactory(){
		return compositeFactory;
	}

	public void setCompositeFactory(CompositeFactory compositeFactory) {
		this.compositeFactory = compositeFactory;
	}
	
	

}
