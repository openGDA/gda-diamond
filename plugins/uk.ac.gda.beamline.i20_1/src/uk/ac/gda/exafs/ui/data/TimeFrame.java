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

package uk.ac.gda.exafs.ui.data;

import uk.ac.gda.util.beans.xml.XMLRichBean;

public class TimeFrame implements XMLRichBean {


	private String label;  // unique id within the TFGParameters
	private double deadTime;
	private double liveTime;
	private int lemoIn;
	private int lemoOut;


	public void setLabel(String label) {
		this.label = label;
	}


	public String getLabel() {
		return label;
	}


	public double getDeadTime() {
		return deadTime;
	}


	public void setDeadTime(double deadTime) {
		this.deadTime = deadTime;
	}


	public double getLiveTime() {
		return liveTime;
	}


	public void setLiveTime(double liveTime) {
		this.liveTime = liveTime;
	}


	public int getLemoIn() {
		return lemoIn;
	}


	public void setLemoIn(int lemoIn) {
		this.lemoIn = lemoIn;
	}


	public int getLemoOut() {
		return lemoOut;
	}


	public void setLemoOut(int lemoOut) {
		this.lemoOut = lemoOut;
	}


	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		long temp;
		temp = Double.doubleToLongBits(deadTime);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		result = prime * result + ((label == null) ? 0 : label.hashCode());
		result = prime * result + lemoIn;
		result = prime * result + lemoOut;
		temp = Double.doubleToLongBits(liveTime);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		return result;
	}


	@Override
	public boolean equals(Object obj) {
		if (this == obj) {
			return true;
		}
		if (obj == null) {
			return false;
		}
		if (getClass() != obj.getClass()) {
			return false;
		}
		TimeFrame other = (TimeFrame) obj;
		if (Double.doubleToLongBits(deadTime) != Double.doubleToLongBits(other.deadTime)) {
			return false;
		}
		if (label == null) {
			if (other.label != null) {
				return false;
			}
		} else if (!label.equals(other.label)) {
			return false;
		}
		if (lemoIn != other.lemoIn) {
			return false;
		}
		if (lemoOut != other.lemoOut) {
			return false;
		}
		if (Double.doubleToLongBits(liveTime) != Double.doubleToLongBits(other.liveTime)) {
			return false;
		}
		return true;
	}
}
