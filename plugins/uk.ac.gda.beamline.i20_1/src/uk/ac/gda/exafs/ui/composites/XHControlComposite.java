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

import gda.device.DeviceException;
import gda.device.detector.NXDetectorData;
import gda.device.detector.StripDetector;
import gda.device.detector.XHDetector;
import gda.jython.Jython;
import gda.jython.JythonServerStatus;
import gda.observable.IObserver;

import java.beans.PropertyChangeListener;
import java.util.Date;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IContributionItem;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.SDAPlotter;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.beamline.i20_1.Activator;
import uk.ac.gda.beamline.i20_1.I20_1PreferenceInitializer;
import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorConfig;
import uk.ac.gda.exafs.data.ObservableModel;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;

import com.swtdesigner.ResourceManager;

public class XHControlComposite extends Composite implements IObserver {

	public static final String ID = "uk.ac.gda.exafs.ui.composites.xhcontrolcomposite"; //$NON-NLS-1$

	private static final Logger logger = LoggerFactory.getLogger(XHControlComposite.class);

	public volatile boolean continueLiveLoop = false;

	private final ViewPart site;

	//	private Spinner txtRefreshPeriod;

	double[] allValues;
	double[][] regionValues;

	private Action start;
	private Action stop;
	private Action snapshot;
	private Action snapshotAndSave;

	private Thread liveLoop;

	//	private Text txtLiveTime;

	private final FormToolkit toolkit;

	private final DetectorControlModel detectorControlModel;

	private NumberEditorControl txtSnapTime;

	private NumberEditorControl txtNumScansPerFrame;

	private NumberEditorControl txtLiveTime;

	private NumberEditorControl txtRefreshPeriod;

	private static StripDetector getDetector(){
		return DetectorConfig.INSTANCE.getCurrentDetector();
	}

	public static class DetectorControlModel extends ObservableModel {
		public static final String LIVE_INTEGRATION_TIME_PROP_NAME = "liveIntegrationTime";
		private double liveIntegrationTime;

		public static final String LIVE_MODE_REFRESH_PERIOD_PROP_NAME = "refreshPeriod";
		private double refreshPeriod;

		public static final String SNAPSHOT_INTEGRATION_TIME_PROP_NAME = "snapshotIntegrationTime";
		private double snapshotIntegrationTime;

		public static final String NUMBER_OF_ACCUMULATIONS_PROP_NAME = "numberOfAccumulations";
		private int numberOfAccumulations;

		public double getLiveIntegrationTime() {
			return liveIntegrationTime;
		}
		public void setLiveIntegrationTime(double liveIntegrationTime) {
			firePropertyChange(LIVE_INTEGRATION_TIME_PROP_NAME, this.liveIntegrationTime, this.liveIntegrationTime = liveIntegrationTime);
		}
		public double getRefreshPeriod() {
			return refreshPeriod;
		}
		public void setRefreshPeriod(double refreshPeriod) {
			firePropertyChange(LIVE_MODE_REFRESH_PERIOD_PROP_NAME, this.refreshPeriod, this.refreshPeriod = refreshPeriod);
		}
		public double getSnapshotIntegrationTime() {
			return snapshotIntegrationTime;
		}
		public void setSnapshotIntegrationTime(double snapshotIntegrationTime) {
			firePropertyChange(SNAPSHOT_INTEGRATION_TIME_PROP_NAME, this.snapshotIntegrationTime, this.snapshotIntegrationTime = snapshotIntegrationTime);
		}
		public int getNumberOfAccumulations() {
			return numberOfAccumulations;
		}
		public void setNumberOfAccumulations(int numberOfAccumulations) {
			firePropertyChange(NUMBER_OF_ACCUMULATIONS_PROP_NAME, this.numberOfAccumulations, this.numberOfAccumulations = numberOfAccumulations);
		}
	}

	public XHControlComposite(Composite parent, ViewPart site) {
		super(parent, SWT.BORDER_DOT);
		this.site = site;
		toolkit = new FormToolkit(parent.getDisplay());
		detectorControlModel = new DetectorControlModel();
		createUI();
	}

	private void createUI() {
		this.setLayout(new GridLayout());
		buildSections();
		createActions();
		initializeToolBar();
		// FIXME this is a hack to hide the margin!
		this.setBackground(Display.getDefault().getSystemColor(SWT.COLOR_WHITE));
	}

	private synchronized void buildSections() {
		ScrolledForm scrolledform = toolkit.createScrolledForm(this);
		scrolledform.setLayoutData(new GridData(SWT.FILL,SWT.FILL,true, true));
		Form form = scrolledform.getForm();
		TableWrapLayout layout1 = new TableWrapLayout();
		layout1.numColumns = 2;
		form.getBody().setLayout(layout1);
		try {
			createTimesGroup(form.getBody());
			createSnapShotGroup(form.getBody());
		} catch (Exception e) {
			UIHelper.showError("Unable to create sections", e.getMessage());
			logger.error("Unable to create sections", e);
		}
	}

	@SuppressWarnings("static-access")
	private void createSnapShotGroup(Composite parentForm) throws Exception {
		final Section snapshotSection = toolkit.createSection(parentForm, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		toolkit.paintBordersFor(snapshotSection);
		snapshotSection.setText("Snapshot mode time settings");
		toolkit.paintBordersFor(snapshotSection);
		snapshotSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite snapshotSectionComposite = toolkit.createComposite(snapshotSection, SWT.NONE);
		toolkit.paintBordersFor(snapshotSectionComposite);
		snapshotSectionComposite.setLayout(new GridLayout(2, false));
		snapshotSection.setClient(snapshotSectionComposite);

		// Integration time
		Label lbl  = toolkit.createLabel(snapshotSectionComposite, "Integration time", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Double storedSnapShotTime = Activator.getDefault().getPreferenceStore()
				.getDouble(I20_1PreferenceInitializer.SNAPSHOTTIME);
		if (storedSnapShotTime == 0.0) {
			storedSnapShotTime = 1.0;
		}
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.SNAPSHOT_INTEGRATION_TIME_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(java.beans.PropertyChangeEvent evt) {
				Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.SNAPSHOTTIME, (double) evt.getNewValue());
			}
		});
		detectorControlModel.setSnapshotIntegrationTime(storedSnapShotTime);
		txtSnapTime = new NumberEditorControl(snapshotSectionComposite, SWT.None, detectorControlModel, DetectorControlModel.SNAPSHOT_INTEGRATION_TIME_PROP_NAME, true);
		txtSnapTime.setUnit(UnitSetup.MILLI_SEC.getText());
		txtSnapTime.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		// Number of accumulations
		lbl = toolkit.createLabel(snapshotSectionComposite, "Number of accumulations", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		int numberOfAccumulations = Activator.getDefault().getPreferenceStore()
				.getInt(I20_1PreferenceInitializer.SCANSPERFRAME);
		if (numberOfAccumulations == 0) {
			numberOfAccumulations = 1;
		}
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.NUMBER_OF_ACCUMULATIONS_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(java.beans.PropertyChangeEvent evt) {
				Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.SCANSPERFRAME, (int) evt.getNewValue());
			}
		});
		detectorControlModel.setNumberOfAccumulations(numberOfAccumulations);
		txtNumScansPerFrame = new NumberEditorControl(snapshotSectionComposite, SWT.None, detectorControlModel, DetectorControlModel.NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		txtNumScansPerFrame.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	@SuppressWarnings("static-access")
	private void createTimesGroup(Composite parentForm) throws Exception {
		final Section bendSection = toolkit.createSection(parentForm, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		toolkit.paintBordersFor(bendSection);
		bendSection.setText("Live mode time settings");
		toolkit.paintBordersFor(bendSection);
		bendSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite bendSelectionComposite = toolkit.createComposite(bendSection, SWT.NONE);
		toolkit.paintBordersFor(bendSelectionComposite);
		bendSelectionComposite.setLayout(new GridLayout(2, false));
		bendSection.setClient(bendSelectionComposite);

		Label lbl = toolkit.createLabel(bendSelectionComposite, "Integration time", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Double storedLiveTime = Activator.getDefault().getPreferenceStore()
				.getDouble(I20_1PreferenceInitializer.LIVEMODETIME);
		if (storedLiveTime == 0.0) {
			storedLiveTime = 1.0;
		}
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.LIVE_INTEGRATION_TIME_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(java.beans.PropertyChangeEvent evt) {
				Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.LIVEMODETIME, (double) evt.getNewValue());
			}
		});
		detectorControlModel.setLiveIntegrationTime(storedLiveTime);
		txtLiveTime = new NumberEditorControl(bendSelectionComposite, SWT.None, detectorControlModel, DetectorControlModel.LIVE_INTEGRATION_TIME_PROP_NAME, true);
		txtLiveTime.setUnit(UnitSetup.MILLI_SEC.getText());
		txtLiveTime.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		// Live mode refresh period
		lbl =  toolkit.createLabel(bendSelectionComposite, "Refresh period", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		double refreshPeroid = Activator.getDefault().getPreferenceStore()
				.getDouble(I20_1PreferenceInitializer.REFRESHRATE);
		if (refreshPeroid == 0.0) {
			refreshPeroid = 1.0;
		}
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.LIVE_MODE_REFRESH_PERIOD_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(java.beans.PropertyChangeEvent evt) {
				Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.REFRESHRATE, (double) evt.getNewValue());
			}
		});
		detectorControlModel.setRefreshPeriod(refreshPeroid);
		txtRefreshPeriod = new NumberEditorControl(bendSelectionComposite, SWT.None, detectorControlModel, DetectorControlModel.LIVE_MODE_REFRESH_PERIOD_PROP_NAME, true);
		txtRefreshPeriod.setUnit(UnitSetup.SEC.getText());
		txtRefreshPeriod.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		txtRefreshPeriod.setIncrement(DataHelper.getDecimalPlacePowValue(ClientConfig.DEFAULT_DECIMAL_PLACE));
		txtRefreshPeriod.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
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
				collectAndPlotSnapshot(false, detectorControlModel.getSnapshotIntegrationTime(), detectorControlModel.getNumberOfAccumulations(), detectorControlModel.getSnapshotIntegrationTime() + "ms Snapshot");
			}
		};
		snapshot.setId(ID + ".snap");
		snapshot.setImageDescriptor(ResourceManager.getImageDescriptor(XHControlComposite.class, "/icons/camera.png"));

		snapshotAndSave = new Action(null, SWT.NONE) {
			@Override
			public void run() {
				collectAndPlotSnapshot(true, detectorControlModel.getSnapshotIntegrationTime(), detectorControlModel.getNumberOfAccumulations(), detectorControlModel.getSnapshotIntegrationTime() + "ms Snapshot");
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
						int numberSectors = getDetector().getRois().length;
						allValues = new double[0];
						regionValues = new double[numberSectors][0];

						while (continueLiveLoop) {
							Date snapshotTime = new Date();

							double collectionPeriod_ms = detectorControlModel.getLiveIntegrationTime();
							final Double[] results = collectAndPlotSnapshot(false, collectionPeriod_ms, 1,
									"Live reading (" + collectionPeriod_ms + "ms integration, every " + detectorControlModel.getRefreshPeriod()
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
					double refreshPeriod_ms = detectorControlModel.getRefreshPeriod() * 1000;

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
		}
	}
}
