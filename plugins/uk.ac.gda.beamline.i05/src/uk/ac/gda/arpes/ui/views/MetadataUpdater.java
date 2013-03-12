/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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
import gda.device.DeviceException;
import gda.factory.Finder;
import gda.jython.IAllScanDataPointsObserver;
import gda.jython.IJythonServerStatusObserver;
import gda.jython.Jython;
import gda.jython.JythonServerFacade;
import gda.jython.JythonServerStatus;
import gda.observable.IObserver;
import gda.scan.ScanDataPoint;

import java.util.Collection;
import java.util.Date;
import java.util.Iterator;
import java.util.List;
import java.util.StringTokenizer;
import java.util.Vector;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.events.FocusListener;
import org.eclipse.swt.events.KeyAdapter;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A system status display panel updater, this contains all the logic, so the 
 * GUI class be edited by graphical SWT layout editors without breaking functionality.
 */
public class MetadataUpdater implements IObserver, IAllScanDataPointsObserver, IJythonServerStatusObserver {

	private static final Logger logger = LoggerFactory.getLogger(MetadataUpdater.class);

	private SampleMetadataView client;
	private Metadata metadata;
	private JythonServerFacade jsf;
	private List<Integer> scandimensions;
	private String scanstring;
	private Integer totalScanPoints;
	private Date started;


	private class MetadataListener extends KeyAdapter implements FocusListener, IObserver {
		private Text widget;
		private String metadataName;
		private Device blaster;
		public MetadataListener(Text widget, String metadataName, Device blaster) {
			this.widget = widget;
			this.metadataName = metadataName;
			this.blaster = blaster;
			
			widget.addFocusListener(this);
			widget.addKeyListener(this);
			
			blaster.addIObserver(this);
			
			try {
				widget.setText(metadata.getMetadataValue(metadataName));
			} catch (DeviceException e1) {
				widget.setText("");
			}
		}
		
		@Override
		public void keyReleased(KeyEvent e) {
			super.keyReleased(e);
			if (e.character == SWT.CR) {

				try {
					metadata.setMetadataValue(metadataName, widget.getText().trim());
				} catch (Exception e1) {
					widget.setText("");
				}
			}
		}
		@Override
		public void focusGained(FocusEvent e) {
			// TODO Auto-generated method stub
			
		}
		@Override
		public void focusLost(FocusEvent e) {
			try {
				widget.setText(metadata.getMetadataValue(metadataName));
			} catch (DeviceException e1) {
				widget.setText("");
			}
		}
		private void unobserve() {
			blaster.deleteIObserver(this);
		}

		@Override
		public void update(Object source, final Object arg) {
			if (widget.isDisposed()) {
				unobserve();
				return;
			}
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					widget.setText(arg.toString());
					client.currentDirectory.setText(PathConstructor.createFromDefaultProperty());
				}
			});
		}
	}
	
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

			new MetadataListener(client.subDirectory, "subdirectory", (Device) Finder.getInstance().find("observableSubdirectory"));
			new MetadataListener(client.sampleName, "samplename", (Device) Finder.getInstance().find("observableSamplename"));

		} catch (Exception e) {
			logger.warn("could not find required metadata", e);
		}

		jsf = JythonServerFacade.getInstance();
		jsf.addIObserver(this);
		
		client.currentDirectory.setText(PathConstructor.createFromDefaultProperty());
	}

	@Override
	public void update(Object iObservable, Object arg) {
		if (client.frameStatus.isDisposed()) {
			jsf.deleteIObserver(this);
			return;
		}
		Display.getDefault().asyncExec(new Updater(iObservable, arg));
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

		private List<Integer> parseScanDimensions(String string) {
			StringTokenizer st = new StringTokenizer(string, "[], ");
			List<Integer> sd = new Vector<Integer>();
			while (st.hasMoreTokens()) {
				sd.add(Integer.valueOf(st.nextToken()));
			}
			return sd;
		}
		
		private String pointNoAsStr(Integer point) {
			Vector<Integer> currentLoc = new Vector<Integer>(scandimensions);
			int totalsofar = 1;
			for (int j = currentLoc.size()-1; j >= 0 ; j--) {
				int inhere = currentLoc.get(j);
				currentLoc.set(j, point / totalsofar % inhere + 1);
				totalsofar *= inhere;
			}
			return currentLoc.toString();
		}
		
		private Integer multiply(Collection<Integer> c) {
			int a = 1; 
			for (Iterator<Integer> iterator = c.iterator(); iterator.hasNext();) {
				a = a * iterator.next();
			}
			return a;
		}
		
		private String hms4millis(long millis) {
			if (millis == 0) return "--:--:--";
			int h = (int) (millis / (3600 * 1000));
			int m = (int) (millis / (60 * 1000) % 60);
			int s = (int) (millis / 1000 % 60);
			return String.format("%02d:%02d:%02d", h,m,s);
		}
		
		private long noddyETAprediction(int currentpoint, int total, long elapsed) {
			if (currentpoint == 0) return 0;
			return (elapsed * total / currentpoint) - elapsed;
		}
		
		@Override
		public void run() {
			if (arg != null) {
				if (arg instanceof ScanDataPoint) {
					String filename = ((ScanDataPoint) arg).getCurrentFilename();
					client.scanFile.setText(filename);
					int currentPointNumber = ((ScanDataPoint) arg).getCurrentPointNumber();
					client.frameNumber.setText(String.format("%s / %s",pointNoAsStr(currentPointNumber), scanstring));
					client.progressBar.setSelection(10000*currentPointNumber/totalScanPoints);
					long elapsed = (new Date ()).getTime() - started.getTime();
					client.elapsedTime.setText(hms4millis(elapsed));
					client.eta.setText(hms4millis(noddyETAprediction(currentPointNumber, totalScanPoints, elapsed)));
				} else if (arg instanceof JythonServerStatus) {
					JythonServerStatus jss = (JythonServerStatus) arg;
					switch (jss.scanStatus) {
					case Jython.IDLE:
						client.frameStatus.setText("IDLE");
						client.frameNumber.setText("[0] / [0]");
						client.progressBar.setSelection(10000);
						client.elapsedTime.setText("--:--:--");
						client.eta.setText("--:--:--");
						break;
					case Jython.PAUSED:
						client.frameStatus.setText("PAUSED");
						break;
					case Jython.RUNNING:
						started = new Date();
						client.frameStatus.setText("RUNNING");
						client.elapsedTime.setText("00:00:00");
						scanstring = jsf.evaluateCommand("finder.find(\"command_server\").getCurrentScanInformation().getDimensions().tolist()");
						scandimensions = parseScanDimensions(scanstring);
						totalScanPoints = multiply(scandimensions);
						client.frameNumber.setText(String.format("%s / %s",pointNoAsStr(0), scanstring));
						break;
					default:
						client.frameStatus.setText("UNKNOWN");
						break;
					}
				}
			} 
		}
	}
}