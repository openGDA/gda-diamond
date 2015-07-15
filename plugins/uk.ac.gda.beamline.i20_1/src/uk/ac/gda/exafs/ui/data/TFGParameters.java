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

import java.net.URL;
import java.util.List;
import java.util.Vector;

import uk.ac.gda.util.beans.xml.XMLHelpers;
import uk.ac.gda.util.beans.xml.XMLRichBean;

public class TFGParameters implements XMLRichBean {

	static public final URL mappingURL = EdeScanParameters.class.getResource("EdeParametersMapping.xml");
	static public final URL schemaURL = EdeScanParameters.class.getResource("EdeParametersMapping.xsd");

	public static TFGParameters createFromXML(String filename) throws Exception {
		return (TFGParameters) XMLHelpers.createFromXML(mappingURL, TFGParameters.class, schemaURL, filename);
	}

	boolean autoRearm =false;
	List<TimeFrame> timeFrames = new Vector<TimeFrame>();

	public boolean isAutoRearm() {
		return autoRearm;
	}

	public void setAutoRearm(boolean autoRearm) {
		this.autoRearm = autoRearm;
	}

	public List<TimeFrame> getTimeFrames() {
		return timeFrames;
	}

	public void setTimeFrames(List<TimeFrame> timeFrames) {
		this.timeFrames = timeFrames;
	}

	public void addTimeFrame(TimeFrame tf1) {
		timeFrames.add(tf1);
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + (autoRearm ? 1231 : 1237);
		result = prime * result + ((timeFrames == null) ? 0 : timeFrames.hashCode());
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
		TFGParameters other = (TFGParameters) obj;
		if (autoRearm != other.autoRearm) {
			return false;
		}
		if (timeFrames == null) {
			if (other.timeFrames != null) {
				return false;
			}
		} else if (!timeFrames.equals(other.timeFrames)) {
			return false;
		}
		return true;
	}
}
