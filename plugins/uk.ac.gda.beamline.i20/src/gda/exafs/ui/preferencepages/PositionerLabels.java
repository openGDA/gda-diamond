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

package gda.exafs.ui.preferencepages;

import java.net.URL;
import java.util.List;
import java.util.Vector;

import org.apache.commons.beanutils.BeanUtils;

import uk.ac.gda.util.beans.xml.XMLRichBean;

public class PositionerLabels implements XMLRichBean {
	static public final URL mappingURL = PositionerLabels.class.getResource("PositionerLabelMapping.xml");
	static public final URL schemaURL = PositionerLabels.class.getResource("PositionerLabelMapping.xsd");
	private List<PositionerLabelBean> labels;


	public PositionerLabels() {
		labels = new Vector<PositionerLabelBean>(7);
	}

	public List<PositionerLabelBean> getLabels() {
		return labels;
	}

	public void addLabel(PositionerLabelBean e) {
		labels.add(e);
	}

	public void setLabels(List<PositionerLabelBean> e) {
		if (labels != null)
			labels.clear();
		if (e != null)
			this.labels.addAll(e);
	}

	@Override
	public String toString() {
		try {
			return BeanUtils.describe(this).toString();
		} catch (Exception e) {
			return e.getMessage();
		}
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((labels == null) ? 0 : labels.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		PositionerLabels other = (PositionerLabels) obj;
		if (labels == null) {
			if (other.labels != null)
				return false;
		} else if (!labels.equals(other.labels))
			return false;
		return true;
	}

}