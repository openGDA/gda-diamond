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

import gda.rcp.views.FindableExecutableExtension;

/**
 * Factory class to create I14StatusView (q.v.)
 */
public class I14ShuttersViewFactory implements FindableExecutableExtension {

	private static final Logger logger = LoggerFactory.getLogger(I14ShuttersViewFactory.class);

	private String name;

	private String viewName = "Shutters";
	private String iconPlugin = "uk.ac.gda.core";
	private String iconFilePath = "icons/GDAlogos/GDALogo16.png";
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
		logger.info("Creating I14ShuttersView: {}", this);
		final I14ShuttersView view = new I14ShuttersView();
		view.setName(viewName);
		view.setIconPlugin(iconPlugin);
		view.setIconFilePath(iconFilePath);
		view.setRingCurrentAlarmThreshold(ringCurrentAlarmThreshold);
		view.setTimeToRefillAlarmThreshold(timeToRefillAlarmThreshold);
		return view;
	}

	@Override
	public void setName(String name) {
		this.name = name;
	}

	@Override
	public String getName() {
		return name;
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
		return "I14ShuttersViewFactory [viewName=" + viewName + ", iconPlugin=" + iconPlugin + ", iconFilePath="
				+ iconFilePath + ", ringCurrentAlarmThreshold=" + ringCurrentAlarmThreshold
				+ ", timeToRefillAlarmThreshold=" + timeToRefillAlarmThreshold + "]";
	}
}