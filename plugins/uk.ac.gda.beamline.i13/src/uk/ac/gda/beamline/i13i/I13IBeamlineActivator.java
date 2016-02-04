/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i;

import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;

import uk.ac.gda.common.rcp.NamedServiceProvider;

/**
 * The activator class controls the plug-in life cycle
 */
public class I13IBeamlineActivator extends AbstractUIPlugin {
	private static BundleContext bundleContext;

	// The plug-in ID
	public static final String PLUGIN_ID = "uk.ac.gda.beamline.i13i";

	// The shared instance
	private static I13IBeamlineActivator plugin;

	/**
	 * The constructor
	 */
	public I13IBeamlineActivator() {
	}

	@Override
	public void start(BundleContext context) throws Exception {
		super.start(context);
		bundleContext = context;
		plugin = this;
	}

	@Override
	public void stop(BundleContext context) throws Exception {
		plugin = null;
		super.stop(context);
		if (namedServiceProvider != null) {
			namedServiceProvider.close();
			namedServiceProvider = null;
		}
		bundleContext = null;
	}

	/**
	 * Returns the shared instance
	 *
	 * @return the shared instance
	 */
	public static I13IBeamlineActivator getDefault() {
		return plugin;
	}

	/**
	 * Returns an image descriptor for the image file at the given plug-in relative path
	 *
	 * @param path
	 *            the path
	 * @return the image descriptor
	 */
	public static ImageDescriptor getImageDescriptor(String path) {
		return imageDescriptorFromPlugin(PLUGIN_ID, path);
	}

	private static NamedServiceProvider namedServiceProvider;

	public static Object getNamedService(@SuppressWarnings("rawtypes") Class clzz, final String name) {
		if (namedServiceProvider == null) {
			namedServiceProvider = new NamedServiceProvider(bundleContext);
		}
		return namedServiceProvider.getNamedService(clzz, "SERVICE_NAME", name);
	}
}
