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

package uk.ac.gda.arpes.ui.views;

import gda.data.PathConstructor;
import gda.data.metadata.GDAMetadataProvider;
import gda.data.metadata.Metadata;
import gda.device.Device;
import gda.factory.Finder;
import gda.jython.IAllScanDataPointsObserver;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.scan.ScanDataPoint;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A system status display panel
 */
public class MetadataUpdater implements IObserver, IAllScanDataPointsObserver {

	private static final Logger logger = LoggerFactory.getLogger(MetadataUpdater.class);

	private SampleMetadataView client;
	private String subdirectory;
	private Metadata metadata;

	/**
	 * Constructor
	 * 
	 * @param client
	 *            who to update
	 */
	public MetadataUpdater(final SampleMetadataView client) {
		this.client = client;

		try {
			metadata = GDAMetadataProvider.getInstance();
			subdirectory = metadata.getMetadataValue("subdirectory");

			Device blaster = Finder.getInstance().find("observableSubdirectory");
			blaster.addIObserver(this);

			meUpdate();
		} catch (Exception e) {
			logger.warn("could not find subdirectory metadata", e);
		}

		InterfaceProvider.getScanDataPointProvider().addIScanDataPointObserver(this);

		client.subDirectory.addKeyListener(new org.eclipse.swt.events.KeyAdapter() {
			@Override
			public void keyReleased(KeyEvent e) {
				super.keyReleased(e);
				if (e.character == SWT.CR) {

					try {
						metadata.setMetadataValue("subdirectory", client.subDirectory.getText().trim());
					} catch (Exception e1) {
						client.subDirectory.setText("");
					}
				}
			}
		});
	}

	@Override
	public void update(Object iObservable, Object arg) {
		Display.getDefault().asyncExec(new Updater(iObservable, arg));
	}

	private void meUpdate() {
		client.subDirectory.setText(subdirectory);
		client.currentDirectory.setText(PathConstructor.createFromDefaultProperty());
	}

	private class Updater implements Runnable {
		private Object iObservable;
		private Object arg;

		/**
		 * @param iObservable
		 * @param arg
		 */
		public Updater(Object iObservable, Object arg) {
			this.iObservable = iObservable;
			this.arg = arg;
		}

		@Override
		public void run() {
			if (arg != null) {
				if (arg instanceof String) {
						subdirectory = arg.toString();
						meUpdate();
				} else if (arg instanceof ScanDataPoint) {
					String filename = ((ScanDataPoint) arg).getCurrentFilename();
					client.scanFile.setText(filename);
				}
			} 
		}
	}
}