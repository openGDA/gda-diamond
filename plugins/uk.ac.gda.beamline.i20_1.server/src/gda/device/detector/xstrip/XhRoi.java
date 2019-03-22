/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package gda.device.detector.xstrip;

import java.io.Serializable;

/**
 * Holds the definition of a Region of Interest for the XH detector. ROIs must not overlap.
 */
public class XhRoi implements Serializable {

	private static final long serialVersionUID = 1L;

	private String name = "";
	private int lowerLevel;
	private int upperLevel;

	public XhRoi(){
	}


	public XhRoi(String string) {
		name = string;
	}

	@Override
	public String toString() {
		return "XHROI [name=" + name + ", lowerLevel=" + lowerLevel + ", upperLevel=" + upperLevel + "]";
	}

	public String getName() {
		return name;
	}

	public String getLabel() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public void setLabel(String name) {
		this.name = name;
	}

	public int getLowerLevel() {
		return lowerLevel;
	}

	public void setLowerLevel(int lowerLevel) {
		this.lowerLevel = lowerLevel;
	}

	public int getUpperLevel() {
		return upperLevel;
	}

	public void setUpperLevel(int upperLevel) {
		this.upperLevel = upperLevel;
	}
}
