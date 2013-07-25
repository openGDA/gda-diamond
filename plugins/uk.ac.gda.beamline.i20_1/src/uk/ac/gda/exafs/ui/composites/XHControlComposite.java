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

package uk.ac.gda.exafs.ui.composites;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.detector.NXDetectorData;
import gda.device.detector.XHDetector;
import gda.device.detector.XHROI;
import gda.device.detector.corba.impl.DetectorAdapter;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.Jython;
import gda.jython.JythonServerStatus;
import gda.observable.IObserver;

import java.util.Date;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IContributionItem;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.SDAPlotter;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.beamline.i20_1.Activator;
import uk.ac.gda.beamline.i20_1.I20_1PreferenceInitializer;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;

import com.swtdesigner.ResourceManager;

public class XHControlComposite extends Composite implements IObserver {

	public static final String ID = "uk.ac.gda.exafs.ui.composites.xhcontrolcomposite"; //$NON-NLS-1$

	private static final Logger logger = LoggerFactory.getLogger(XHControlComposite.class);

	public volatile boolean continueLiveLoop = false;

	private final ViewPart site;
	private Composite contents;
	private Group timesgroup;

	private Text txtSnapTime;
	private Spinner txtRefreshPeriod;
	private Spinner txtNumScansPerFrame;

	double[] allValues;
	double[][] regionValues;

	private Action start;
	private Action stop;
	private Action snapshot;
	private Action snapshotAndSave;

	private Thread liveLoop;

	private Group snapshotgroup;

	private Text txtLiveTime;

	private static Detector xh;

	private static Detector getDetector(){
		if (xh == null){
			xh = (Detector) Finder.getInstance().find("xh");
		}
		return xh;
	}

	public XHControlComposite(Composite parent, ViewPart site) {
		super(parent, SWT.BORDER_DOT);
		this.site = site;

		InterfaceProvider.getJSFObserver().addIObserver(this);
		getDetector().addIObserver(this);

		createUI();
	}

	private void createUI() {
		this.setLayout(new GridLayout());
		rebuildUI();
		createActions();
		initializeToolBar();
	}

	private synchronized void rebuildUI() {

		contents = new Composite(this, SWT.NONE);
		contents.setLayout(new GridLayout(2, true));
		contents.setLayoutData(new GridData(GridData.FILL_BOTH));

		// expandable with data collection parameters
		createTimesGroup();

		createSnapShotGroup();

		contents.pack(true);
	}

	private void createSnapShotGroup() {
		snapshotgroup = new Group(contents, SWT.BORDER);
		snapshotgroup.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		snapshotgroup.setLayout(new GridLayout(3, false));
		snapshotgroup.setText("Single Spectrum (snapshot) time settings");

		Label lbl = new Label(snapshotgroup, SWT.NONE);
		lbl.setText("Integration Time");
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));
		txtSnapTime = new Text(snapshotgroup, SWT.NONE);
		txtSnapTime.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Double storedSnapShotTime = Activator.getDefault().getPreferenceStore()
				.getDouble(I20_1PreferenceInitializer.SNAPSHOTTIME);
		if (storedSnapShotTime == 0.0) {
			storedSnapShotTime = 1.0;
		}
		txtSnapTime.setText(Double.toString(storedSnapShotTime));
		// button listener
		txtSnapTime.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				try {
					Double newValue = Double.parseDouble(txtSnapTime.getText());
					Activator.getDefault().getPreferenceStore()
					.setValue(I20_1PreferenceInitializer.SNAPSHOTTIME, newValue);
				} catch (NumberFormatException e1) {
					// ignore bad formats
				}
			}
		});
		// properties listener
		Activator.getDefault().getPreferenceStore().addPropertyChangeListener(new IPropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent event) {
				if (event.getProperty().equals(I20_1PreferenceInitializer.SNAPSHOTTIME)) {
					String newValue = event.getNewValue().toString();
					if (!newValue.equals(txtSnapTime.getText())) {
						txtSnapTime.setText(newValue);
					}
				}
			}
		});
		lbl = new Label(snapshotgroup, SWT.NONE);
		lbl.setText("ms");
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));

		lbl = new Label(snapshotgroup, SWT.NONE);
		lbl.setText("Number of accumulations");
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));
		txtNumScansPerFrame = new Spinner(snapshotgroup, SWT.NONE);
		txtNumScansPerFrame.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		txtNumScansPerFrame.setMinimum(1);
		txtNumScansPerFrame.setIncrement(1);
		txtNumScansPerFrame.setSelection(Activator.getDefault().getPreferenceStore()
				.getInt(I20_1PreferenceInitializer.SCANSPERFRAME));
		// button listener
		txtNumScansPerFrame.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				try {
					int newValue = Integer.parseInt(txtNumScansPerFrame.getText());
					Activator.getDefault().getPreferenceStore()
					.setValue(I20_1PreferenceInitializer.SCANSPERFRAME, newValue);
				} catch (NumberFormatException e1) {
					// ignore bad formats
				}
			}
		});
		// properties listener
		Activator.getDefault().getPreferenceStore().addPropertyChangeListener(new IPropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent event) {
				if (event.getProperty().equals(I20_1PreferenceInitializer.SCANSPERFRAME)) {
					String newValue = event.getNewValue().toString();
					if (!newValue.equals(txtNumScansPerFrame.getText())) {
						txtNumScansPerFrame.setSelection(Integer.parseInt(newValue));
					}
				}
			}
		});
		lbl = new Label(snapshotgroup, SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));
	}

	private void createTimesGroup() {
		timesgroup = new Group(contents, SWT.BORDER);
		timesgroup.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		timesgroup.setLayout(new GridLayout(3, false));
		timesgroup.setText("Live Mode time settings");

		Label lbl = new Label(timesgroup, SWT.NONE);
		lbl.setText("Integration Time");
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));
		txtLiveTime = new Text(timesgroup, SWT.NONE);
		txtLiveTime.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Double storedLiveTime = Activator.getDefault().getPreferenceStore()
				.getDouble(I20_1PreferenceInitializer.LIVEMODETIME);
		if (storedLiveTime == 0) {
			storedLiveTime = 1.0;
		}
		txtLiveTime.setText(Double.toString(storedLiveTime));
		// button listener
		txtLiveTime.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				try {
					Double newValue = Double.parseDouble(txtLiveTime.getText());
					Activator.getDefault().getPreferenceStore()
					.setValue(I20_1PreferenceInitializer.LIVEMODETIME, newValue);
				} catch (NumberFormatException e1) {
					// ignore bad formats
				}
			}
		});
		// properties listener
		Activator.getDefault().getPreferenceStore().addPropertyChangeListener(new IPropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent event) {
				if (event.getProperty().equals(I20_1PreferenceInitializer.LIVEMODETIME)) {
					String newValue = event.getNewValue().toString();
					if (!newValue.equals(txtLiveTime.getText())) {
						txtLiveTime.setText(newValue);
					}
				}
			}
		});
		lbl = new Label(timesgroup, SWT.NONE);
		lbl.setText("ms");
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));

		lbl = new Label(timesgroup, SWT.NONE);
		lbl.setText("Refresh Period");
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));
		txtRefreshPeriod = new Spinner(timesgroup, SWT.NONE);
		txtRefreshPeriod.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		txtRefreshPeriod.setMinimum(1);
		txtRefreshPeriod.setMaximum(60);
		txtRefreshPeriod.setIncrement(1);
		txtRefreshPeriod.setSelection(Activator.getDefault().getPreferenceStore()
				.getInt(I20_1PreferenceInitializer.REFRESHRATE));
		// button listener
		txtRefreshPeriod.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				try {
					int newValue = Integer.parseInt(txtRefreshPeriod.getText());
					Activator.getDefault().getPreferenceStore()
					.setValue(I20_1PreferenceInitializer.REFRESHRATE, newValue);
				} catch (NumberFormatException e1) {
					// ignore bad formats
				}
			}
		});
		// properties listener
		Activator.getDefault().getPreferenceStore().addPropertyChangeListener(new IPropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent event) {
				if (event.getProperty().equals(I20_1PreferenceInitializer.REFRESHRATE)) {
					String newValue = event.getNewValue().toString();
					if (!newValue.equals(txtRefreshPeriod.getText())) {
						txtRefreshPeriod.setSelection(Integer.parseInt(newValue));
					}
				}
			}
		});
		lbl = new Label(timesgroup, SWT.NONE);
		lbl.setText("s");
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));

	}

	private XHROI[] getROI() throws DeviceException {
		return (XHROI[]) getDetector().getAttribute(XHDetector.ATTR_ROIS);
	}

	private void createActions() {

		// actions are created here programmatically as then it is simpler to enable/disable them by holding that logic
		// in this class.

		start = new Action(null, SWT.NONE) {
			@Override
			public void run() {
				startCollectingRates();
			}
		};
		start.setId(ID + ".start");
		start.setImageDescriptor(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/control_play_blue.png"));

		stop = new Action(null, SWT.NONE) {
			@Override
			public void run() {
				stopCollectingRates();
			}
		};
		stop.setId(ID + ".stop");
		stop.setImageDescriptor(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/control_stop_blue.png"));

		snapshot = new Action(null, SWT.NONE) {
			@Override
			public void run() {
				try {
					final Double snapshotIntTime = Activator.getDefault().getPreferenceStore()
							.getDouble(I20_1PreferenceInitializer.SNAPSHOTTIME);
					final Integer scansPerFrame = Activator.getDefault().getPreferenceStore()
							.getInt(I20_1PreferenceInitializer.SCANSPERFRAME);
					collectAndPlotSnapshot(false, snapshotIntTime, scansPerFrame, snapshotIntTime + "ms Snapshot");
				} catch (Exception e) {
					logger.error("Error trying to collect detector snapshot", e);
				}
			}
		};
		snapshot.setId(ID + ".snap");
		snapshot.setImageDescriptor(ResourceManager.getImageDescriptor(XHControlComposite.class, "/icons/camera.png"));

		snapshotAndSave = new Action(null, SWT.NONE) {
			@Override
			public void run() {
				try {
					final Double snapshotIntTime_ms = Activator.getDefault().getPreferenceStore()
							.getDouble(I20_1PreferenceInitializer.SNAPSHOTTIME);
					final Integer scansPerFrame = Activator.getDefault().getPreferenceStore()
							.getInt(I20_1PreferenceInitializer.SCANSPERFRAME);
					collectAndPlotSnapshot(true, snapshotIntTime_ms, scansPerFrame, snapshotIntTime_ms + "ms Snapshot");
				} catch (Exception e) {
					logger.error("Error trying to collect detector snapshot", e);
				}
			}
		};
		snapshotAndSave.setId(ID + ".snapsave");
		snapshotAndSave.setImageDescriptor(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/camera_edit.png"));
	}

	private static void collectData(Double collectionPeriod, int numberScans, Integer scansPerFrame) throws DeviceException, InterruptedException {

		// collect data from XHDetector and send the spectrum to local Plot 1 window
		EdeScanParameters simpleParams = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setDelayBetweenFrames(0);
		group1.setLabel("group1");
		group1.setNumberOfFrames(numberScans);
		if (scansPerFrame > 0) {
			group1.setNumberOfScansPerFrame(scansPerFrame);
			group1.setTimePerScan(new Double(collectionPeriod) / 1000);
		} else {
			group1.setTimePerFrame(new Double(collectionPeriod) / 1000);
		}
		simpleParams.addGroup(group1);

		getDetector().setAttribute(XHDetector.ATTR_LOADPARAMETERS, simpleParams);
		getDetector().collectData();
		getDetector().waitWhileBusy();
	}

	/**
	 * Collects a single frame of data and plots it.
	 * 
	 * @param writeData - writes a file of the data
	 * @param collectionPeriod - ms
	 * @param title
	 * @return double values from the detector - the FF and sector totals
	 */
	public static Double[] collectAndPlotSnapshot(boolean writeData, Double collectionPeriod, Integer scansPerFrame,
			String title) {

		try {
			collectData(collectionPeriod, 1,scansPerFrame);

			// will return a double[] of corrected data
			Object results = getDetector().getAttribute(XHDetector.ATTR_READFIRSTFRAME);

			if (results != null) {
				DoubleDataset resultsDataSet = new DoubleDataset((double[]) results);
				SDAPlotter.plot(AlignmentPerspective.SPECTRAPLOTNAME, title, resultsDataSet);
			} else {
				logger.info("Nothing returned!");
			}

			if (writeData) {
				getDetector().getAttribute(XHDetector.ATTR_WRITEFIRSTFRAME);
			}

			NXDetectorData readout = (NXDetectorData) getDetector().readout();
			return readout.getDoubleVals();

		} catch (Exception e) {
			logger.error("exception while collecting snapshot from XHDetector", e);
			// popup
			MessageDialog
			.openError(
					PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell(),
					"Error collecting snapshot",
					"Error while collecting snapshot from XHDetector.\nAre your parameters correct? Do you hold the baton?\nSee log for details.");
			return new Double[0];
		}
	}

	private void initializeToolBar() {
		IToolBarManager toolbarManager = site.getViewSite().getActionBars().getToolBarManager();
		if (checkMenuItemsMissing()) {
			toolbarManager.add(start);
			toolbarManager.add(stop);
			toolbarManager.add(snapshot);
			toolbarManager.add(snapshotAndSave);
		}
	}

	private boolean checkMenuItemsMissing() {
		if (start == null) {
			return true;
		}

		IToolBarManager toolbarManager = site.getViewSite().getActionBars().getToolBarManager();
		IContributionItem[] items = toolbarManager.getItems();

		boolean found = false;
		for (IContributionItem item : items) {
			if (item.getId() == start.getId()) {
				found = true;
			}
		}

		return !found;
	}

	public void startCollectingRates() {
		if (liveLoop == null || !liveLoop.isAlive()) {
			continueLiveLoop = true;
			liveLoop = null;
			start.setEnabled(false);
			stop.setEnabled(true);
			snapshot.setEnabled(false);
			snapshotAndSave.setEnabled(false);
			PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
				@Override
				public void run() {
					txtLiveTime.setEnabled(false);
					txtNumScansPerFrame.setEnabled(false);
					txtRefreshPeriod.setEnabled(false);
					txtSnapTime.setEnabled(false);
				}
			});
			liveLoop = uk.ac.gda.util.ThreadManager.getThread(new Runnable() {
				@Override
				public void run() {
					try {
						int numberSectors = getROI().length;
						allValues = new double[0];
						regionValues = new double[numberSectors][0];

						while (continueLiveLoop) {
							Date snapshotTime = new Date();

							final Integer refreshPeriod_s = Activator.getDefault().getPreferenceStore()
									.getInt(I20_1PreferenceInitializer.REFRESHRATE);

							final Double collectionPeriod_ms = Activator.getDefault().getPreferenceStore()
									.getDouble(I20_1PreferenceInitializer.LIVEMODETIME);
							final Double[] results = collectAndPlotSnapshot(false, collectionPeriod_ms, 1,
									"Live reading (" + collectionPeriod_ms + "ms integration, every " + refreshPeriod_s
									+ " s)");

							allValues = ArrayUtils.add(allValues, results[2]);
							for (int i = 3; i < results.length; i++) {
								regionValues[i - 3] = ArrayUtils.add(regionValues[i - 3], results[i]);
							}

							waitForRefreshPeriod(snapshotTime);
						}
					} catch (Exception e) {
						logger.error("Exception in loop refreshing the live XH detector rate", e);
						stopCollectingRates();
					}
				}

				private void waitForRefreshPeriod(Date snapshotTime) throws InterruptedException {
					Date now = new Date();
					Integer refreshPeriod_s = Activator.getDefault().getPreferenceStore()
							.getInt(I20_1PreferenceInitializer.REFRESHRATE);
					Integer refreshPeriod_ms = refreshPeriod_s * 1000;

					while (now.getTime() - snapshotTime.getTime() < refreshPeriod_ms) {
						now = new Date();
						Thread.sleep(50);
					}
				}
			});
			liveLoop.start();
		}
	}

	public void stopCollectingRates() {
		continueLiveLoop = false;
		start.setEnabled(true);
		stop.setEnabled(false);
		snapshot.setEnabled(true);
		snapshotAndSave.setEnabled(true);
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				txtLiveTime.setEnabled(true);
				txtNumScansPerFrame.setEnabled(true);
				txtRefreshPeriod.setEnabled(true);
				txtSnapTime.setEnabled(true);
			}
		});
	}

	@Override
	public void update(Object source, Object arg) {
		if (arg instanceof JythonServerStatus) {
			JythonServerStatus status = (JythonServerStatus) arg;

			boolean canContinue = true;
			if (status.scanStatus != Jython.IDLE || status.scriptStatus != Jython.IDLE) {
				canContinue = false;
				stopCollectingRates();
			}
			start.setEnabled(canContinue);
			stop.setEnabled(canContinue);
			snapshot.setEnabled(canContinue);
			snapshotAndSave.setEnabled(canContinue);
		} else if (source instanceof DetectorAdapter && arg instanceof String) {
			if (((String) arg).equals(XHDetector.ROIS_CHANGED)) {
				PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
					@Override
					public void run() {
						rebuildUI();
					}
				});
			}
		}
	}
}
