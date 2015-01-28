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

import org.apache.commons.beanutils.BeanUtils;

import uk.ac.gda.util.beans.xml.XMLRichBean;
import uk.ac.gda.util.beans.xml.XMLHelpers;

/**
 * Additional options for users on the EDE branchline.
 */
public class UserOptions implements XMLRichBean {

	static public final URL mappingURL = EdeScanParameters.class.getResource("EdeParametersMapping.xml");
	static public final URL schemaURL = EdeScanParameters.class.getResource("EdeParametersMapping.xsd");

	public static UserOptions createFromXML(String filename) throws Exception {
		return (UserOptions) XMLHelpers.createFromXML(mappingURL, UserOptions.class, schemaURL, filename);
	}

	public static void writeToXML(UserOptions useroptions, String filename) throws Exception {
		XMLHelpers.writeToXML(mappingURL, useroptions, filename);
	}


	private String scriptName;

	public void setScriptName(String scriptName) {
		this.scriptName = scriptName;
	}

	public String getScriptName() {
		return scriptName;
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
		result = prime * result + ((scriptName == null) ? 0 : scriptName.hashCode());
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
		UserOptions other = (UserOptions) obj;
		if (scriptName == null) {
			if (other.scriptName != null) {
				return false;
			}
		} else if (!scriptName.equals(other.scriptName)) {
			return false;
		}
		return true;
	}

}
