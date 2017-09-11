package uk.ac.gda.beamline.i21;

import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.preference.PreferenceStore;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.scanning.device.ui.Activator;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;

public class I21BeamlineActivator extends AbstractUIPlugin {

	// The plug-in ID
	public static final String PLUGIN_ID = "uk.ac.gda.beamline.i21"; //$NON-NLS-1$

	// The shared instance
	private static I21BeamlineActivator plugin;
	private BundleContext context;

	/**
	 * The constructor
	 */
	public I21BeamlineActivator() {
	}

	/*
	 * (non-Javadoc)
	 * @see org.eclipse.ui.plugin.AbstractUIPlugin#start(org.osgi.framework.BundleContext)
	 */
	@Override
	public void start(BundleContext context) throws Exception {
		super.start(context);
		plugin = this;
		this.context = context;
	}

	/*
	 * (non-Javadoc)
	 * @see org.eclipse.ui.plugin.AbstractUIPlugin#stop(org.osgi.framework.BundleContext)
	 */
	@Override
	public void stop(BundleContext context) throws Exception {
		plugin = null;
		this.context = null;
		super.stop(context);
	}

	/**
	 * Returns the shared instance
	 *
	 * @return the shared instance
	 */
	public static I21BeamlineActivator getDefault() {
		return plugin;
	}

	private static IPreferenceStore store;
	public static IPreferenceStore getStore() {
		if (plugin!=null) return plugin.getPreferenceStore();
		if (store==null) store = new PreferenceStore();
		return store;
	}

	public static ImageDescriptor getImageDescriptor(String path) {
		if (plugin==null) {
			final ImageData data = new ImageData("../"+PLUGIN_ID+"/"+path);
			return new ImageDescriptor() {
				@Override
				public ImageData getImageData() {
					return data;
				}
			};
		}
		return imageDescriptorFromPlugin(PLUGIN_ID, path);
	}


}
