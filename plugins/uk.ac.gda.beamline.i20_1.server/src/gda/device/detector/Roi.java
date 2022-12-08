/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package gda.device.detector;

import java.io.Serializable;


public class Roi implements Serializable {

	private static final long serialVersionUID = 1L;

	private String name = "";
	private int lowerLevel;
	private int upperLevel;

	public String getName() {
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

	public boolean isInsideRio(int elementNumber) {
		return elementNumber >= getLowerLevel() && elementNumber <= getUpperLevel();
	}

	@Override
	public String toString() {
		return "Roi [name=" + name + ", lowerLevel=" + lowerLevel + ", upperLevel=" + upperLevel + "]";
	}
}
