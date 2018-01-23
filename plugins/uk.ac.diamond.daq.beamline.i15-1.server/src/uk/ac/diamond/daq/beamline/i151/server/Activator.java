package uk.ac.diamond.daq.beamline.i151.server;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;

/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

public class Activator implements BundleActivator {

	private static BundleContext bundleContext;

	@Override
	public void start(BundleContext context) throws Exception {
		Activator.bundleContext = context;
	}

	@Override
	public void stop(BundleContext context) throws Exception {
		Activator.bundleContext = null;
	}

	public static <T> T getService(Class<T> serviceClass) {
		ServiceReference<T> ref = bundleContext.getServiceReference(serviceClass);
		return bundleContext.getService(ref);
	}

}
