/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i08_1.views.statusview;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IConfigurationElement;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.FindableBase;
import gda.rcp.views.FindableExecutableExtension;

public class StatusViewFactory extends FindableBase implements FindableExecutableExtension {
	private static final Logger logger = LoggerFactory.getLogger(StatusViewFactory.class);

	private String iconPlugin = "uk.ac.gda.beamline.i08-1";
	private String iconFilePath = "icons/status.png";

	@Override
	public Object create() throws CoreException {
		logger.info("Creating I08-1 status view: {}", this);
		final StatusView view = new StatusView();
		view.setIconPlugin(iconPlugin);
		view.setIconFilePath(iconFilePath);
		return view;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		// nothing to do
	}

	@Override
	public void setInitializationData(IConfigurationElement config, String propertyName, Object data) throws CoreException {
		// nothing to do
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = super.hashCode();
		result = prime * result + ((iconFilePath == null) ? 0 : iconFilePath.hashCode());
		result = prime * result + ((iconPlugin == null) ? 0 : iconPlugin.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (!super.equals(obj))
			return false;
		if (getClass() != obj.getClass())
			return false;
		StatusViewFactory other = (StatusViewFactory) obj;
		if (iconFilePath == null) {
			if (other.iconFilePath != null)
				return false;
		} else if (!iconFilePath.equals(other.iconFilePath))
			return false;
		if (iconPlugin == null) {
			if (other.iconPlugin != null)
				return false;
		} else if (!iconPlugin.equals(other.iconPlugin))
			return false;
		return true;
	}
}