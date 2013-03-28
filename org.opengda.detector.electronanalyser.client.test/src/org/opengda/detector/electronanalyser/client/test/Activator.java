package org.opengda.detector.electronanalyser.client.test;

import gda.util.SpringObjectServer;

import java.io.File;

import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;

public class Activator implements BundleActivator {

	private static BundleContext context;

	static BundleContext getContext() {
		return context;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.framework.BundleActivator#start(org.osgi.framework.BundleContext
	 * )
	 */
	public void start(BundleContext bundleContext) throws Exception {
		Activator.context = bundleContext;
//		SpringObjectServer s = new SpringObjectServer(
//				new File(
//						"D:/gda/gda-i09/workspace/org.opengda.detector.electronanalyser.client.test/client.xml"),
//				true);
//		s.configure();
//		 FileSystemXmlApplicationContext applicationContext = new
//		 FileSystemXmlApplicationContext(
//		 "file:D:\\gda\\gda-i09\\workspace\\org.opengda.detector.electroanalyser.client\\client.xml");
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.framework.BundleActivator#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext bundleContext) throws Exception {
		Activator.context = null;
	}

}
