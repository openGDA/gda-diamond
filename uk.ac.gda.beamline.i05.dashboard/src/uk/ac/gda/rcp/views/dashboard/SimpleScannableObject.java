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

package uk.ac.gda.rcp.views.dashboard;

import gda.jython.JythonServerFacade;

public class SimpleScannableObject {

	private String scannableName, toolTip;
	private String lastPosition;

	public SimpleScannableObject() {
	}

	public SimpleScannableObject(String name) {
		this.setScannableName(name);
	}

	public String getScannableName() {
		return scannableName;
	}

	public void setScannableName(String scannableName) {
		this.scannableName = scannableName;
	}

	public String getToolTip() {
		return toolTip;
	}

	public void setToolTip(String toolTip) {
		this.toolTip = toolTip;
	}

	public String getFormattedLastPosition() {
		if (lastPosition == null)
			refresh();
		return lastPosition;
	}

	public void refresh() {
		try {
			lastPosition = JythonServerFacade.getInstance().evaluateCommand("gda.device.scannable.ScannableUtils.getFormattedCurrentPosition("
				+ scannableName + ")");
		} catch (Exception e) {

		}
	}
}