/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i14.views;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IConfigurationElement;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.FindableBase;
import gda.rcp.views.FindableExecutableExtension;

/**
 * Factory class to create a {@link StatusView} for I14
 */
public class StatusViewFactory extends FindableBase implements FindableExecutableExtension {

	private static final Logger logger = LoggerFactory.getLogger(StatusViewFactory.class);

	private String viewName = "Status";
	private String iconPlugin = "uk.ac.gda.beamline.i14";
	private String iconFilePath = "icons/status.png";
	private Double ringCurrentAlarmThreshold;
	private Double timeToRefillAlarmThreshold;

	@Override
	public void afterPropertiesSet() throws Exception {
		// nothing to do
	}

	@Override
	public void setInitializationData(IConfigurationElement config, String propertyName, Object data) throws CoreException {
		// nothing to do
	}

	@Override
	public Object create() throws CoreException {
		logger.info("Creating I14 status view: {}", this);
		final StatusView view = new StatusView();
		view.setName(viewName);
		view.setIconPlugin(iconPlugin);
		view.setIconFilePath(iconFilePath);
		view.setRingCurrentAlarmThreshold(ringCurrentAlarmThreshold);
		view.setTimeToRefillAlarmThreshold(timeToRefillAlarmThreshold);
		return view;
	}

	public void setViewName(String viewName) {
		this.viewName = viewName;
	}

	public void setIconPlugin(String iconPlugin) {
		this.iconPlugin = iconPlugin;
	}

	public void setIconFilePath(String iconFilePath) {
		this.iconFilePath = iconFilePath;
	}

	public void setRingCurrentAlarmThreshold(Double ringCurrentAlarmThreshold) {
		this.ringCurrentAlarmThreshold = ringCurrentAlarmThreshold;
	}

	public void setTimeToRefillAlarmThreshold(Double timeToRefillAlarmThreshold) {
		this.timeToRefillAlarmThreshold = timeToRefillAlarmThreshold;
	}

	@Override
	public String toString() {
		return "I14StatusViewFactory [viewName=" + viewName + ", iconPlugin=" + iconPlugin + ", iconFilePath="
				+ iconFilePath + ", ringCurrentAlarmThreshold=" + ringCurrentAlarmThreshold
				+ ", timeToRefillAlarmThreshold=" + timeToRefillAlarmThreshold + "]";
	}
}