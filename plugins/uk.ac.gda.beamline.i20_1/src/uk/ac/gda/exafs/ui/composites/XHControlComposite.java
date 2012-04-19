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
import gda.device.Device;
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
import java.util.List;
import java.util.Vector;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IContributionItem;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridDataFactory;
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
import org.eclipse.ui.IViewReference;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.SDAPlotter;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.enums.OverlayType;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.enums.PrimitiveType;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.overlay.Overlay1DConsumer;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.overlay.Overlay1DProvider;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.overlay.OverlayProvider;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.tools.AreaSelectEvent;
import uk.ac.diamond.scisoft.analysis.rcp.views.PlotView;
import uk.ac.gda.beamline.i20_1.Activator;
import uk.ac.gda.beamline.i20_1.I20_1PreferenceInitializer;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;
import uk.ac.gda.richbeans.components.selector.BeanSelectionEvent;
import uk.ac.gda.richbeans.components.selector.BeanSelectionListener;
import uk.ac.gda.richbeans.components.selector.VerticalListEditor;

import com.swtdesigner.ResourceManager;

public class XHControlComposite extends Composite implements IObserver, Overlay1DConsumer, DetectorSetupComposite {

	public static final String ID = "uk.ac.gda.exafs.ui.composites.xhcontrolcomposite"; //$NON-NLS-1$

	private static final Logger logger = LoggerFactory.getLogger(XHControlComposite.class);

	public volatile boolean continueLiveLoop = false;

	private ViewPart site;
	private Composite contents;
	private Group roisGroup;
	private Group totalsGroup;
	private Group timesgroup;

	private Text txtAll;
	private Text[] txtSectors;
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

	private VerticalListEditor theList;
	private Overlay1DProvider oProvider;

	private int[] lineReferences = new int[0];

	// flags to ensure there is no loop in the refresh of the graph - whenever the table is changed by a mouse event, an
	// necessary redraw of the graph occurs.
	private volatile boolean ignoreTableUpdates = false;
	private volatile boolean displayLockHeld = false;

	private boolean displayOverlay = false;

	private Group snapshotgroup;

	private Text txtLiveTime;

	public XHControlComposite(Composite parent, ViewPart site) {
		super(parent, SWT.NONE);
		this.site = site;

		InterfaceProvider.getJSFObserver().addIObserver(this);

		((Detector) Finder.getInstance().find("XHDetector")).addIObserver(this);

		createUI();
	}

	private void createUI() {
		rebuildUI();
		createActions();
		initializeToolBar();
	}

	private synchronized void rebuildUI() {

		removeOverlay();

		disposeOldUI();

		contents = new Composite(this, SWT.NONE);
		contents.setLayout(new GridLayout(1, true));
		contents.setLayoutData(new GridData(SWT.BEGINNING, SWT.BEGINNING, true, false));

		// expandable with data collection parameters
		createTimesGroup();

		createSnapShotGroup();

		createROIConfigGroup();

		contents.pack(true);
	}

	private void createROIConfigGroup() {
		roisGroup = new Group(contents, SWT.BORDER);
		GridDataFactory.fillDefaults().span(2, 1).applyTo(roisGroup);
		roisGroup.setLayout(new GridLayout(1, false));
		roisGroup.setText("Edit ROIs");

		theList = new VerticalListEditor(roisGroup, SWT.NONE);
		GridDataFactory.fillDefaults().applyTo(theList);
		final XHROIComposite theROIs = new XHROIComposite(theList, SWT.NONE);
		theROIs.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		theList.setEditorClass(XHROI.class);
		theList.setEditorUI(theROIs);
		theList.setNameField("Label");
		theList.setMinItems(0);
		theList.on();

		theList.addBeanSelectionListener(new BeanSelectionListener() {

			@Override
			public void selectionChanged(BeanSelectionEvent evt) {
				if (!ignoreTableUpdates) {
					theROIs.selectionChanged((XHROI) evt.getSelectedBean());
					refreshOverlay();
				}
			}
		});
		fetchLiveValues();
	}

	private void createSnapShotGroup() {
		snapshotgroup = new Group(contents, SWT.BORDER);
		snapshotgroup.setLayoutData(new GridData(SWT.FILL, SWT.FILL, false, false));
		snapshotgroup.setLayout(new GridLayout(2, false));
		snapshotgroup.setText("Single Spectrum (snapshot) time settings");

		Label lbl = new Label(snapshotgroup, SWT.NONE);
		lbl.setText("Integration Time");
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));
		txtSnapTime = new Text(snapshotgroup, SWT.NONE);
		txtSnapTime.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		txtSnapTime.setText(Integer.toString(Activator.getDefault().getPreferenceStore()
				.getInt(I20_1PreferenceInitializer.SNAPSHOTTIME)));
		// button listener
		txtSnapTime.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				try {
					int newValue = Integer.parseInt(txtSnapTime.getText());
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
		lbl.setText("Scans per frame");
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
	}

	private void createTimesGroup() {
		timesgroup = new Group(contents, SWT.BORDER);
		timesgroup.setLayoutData(new GridData(SWT.FILL, SWT.FILL, false, false));
		timesgroup.setLayout(new GridLayout(2, false));
		timesgroup.setText("Live Mode time settings");

		Label lbl = new Label(timesgroup, SWT.NONE);
		lbl.setText("Integration Time");
		lbl.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, false, false));
		txtLiveTime = new Text(timesgroup, SWT.NONE);
		txtLiveTime.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		txtLiveTime.setText(Integer.toString(Activator.getDefault().getPreferenceStore()
				.getInt(I20_1PreferenceInitializer.LIVEMODETIME)));
		// button listener
		txtLiveTime.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				try {
					int newValue = Integer.parseInt(txtLiveTime.getText());
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
	}

	private void disposeOldUI() {
		if (txtAll == null) {
			return;
		}
		txtAll.dispose();
		txtAll = null;
		for (Text sector : txtSectors) {
			sector.dispose();
			sector = null;
		}
		txtSectors = null;

		txtSnapTime.dispose();
		txtSnapTime = null;
		txtRefreshPeriod.dispose();
		txtRefreshPeriod = null;
		txtNumScansPerFrame.dispose();
		txtNumScansPerFrame = null;

		totalsGroup.dispose();
		totalsGroup = null;
		timesgroup.dispose();
		timesgroup = null;
		roisGroup.dispose();
		roisGroup = null;
		theList.dispose();
		theList = null;

		contents.dispose();
		contents = null;
	}

	private XHROI[] getROI() throws DeviceException {
		Detector xhdet = Finder.getInstance().find("XHDetector");
		return (XHROI[]) xhdet.getAttribute(XHDetector.ATTR_ROIS);
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
					final Integer snapshotIntTime = Activator.getDefault().getPreferenceStore()
							.getInt(I20_1PreferenceInitializer.SNAPSHOTTIME);
					final Integer numScans = Activator.getDefault().getPreferenceStore()
							.getInt(I20_1PreferenceInitializer.SCANSPERFRAME);
					collectAndPlotSnapshot(false, snapshotIntTime, numScans, snapshotIntTime + "s Snapshot");
				} catch (Exception e) {
					logger.error("Error trying to collect detector snapshot", e);
				}
			}
		};
		snapshot.setId(ID + ".snap");
		snapshot.setImageDescriptor(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/camera.png"));

		snapshotAndSave = new Action(null, SWT.NONE) {
			@Override
			public void run() {
				try {
					final Integer snapshotIntTime = Activator.getDefault().getPreferenceStore()
							.getInt(I20_1PreferenceInitializer.SNAPSHOTTIME);
					final Integer numScans = Activator.getDefault().getPreferenceStore()
							.getInt(I20_1PreferenceInitializer.SCANSPERFRAME);
					collectAndPlotSnapshot(true, snapshotIntTime,numScans, snapshotIntTime + "s Snapshot");
				} catch (Exception e) {
					logger.error("Error trying to collect detector snapshot", e);
				}
			}
		};
		snapshotAndSave.setId(ID + ".snapsave");
		snapshotAndSave.setImageDescriptor(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/camera_edit.png"));
	}

	private static void collectData(int collectionPeriod, int numberScans) throws DeviceException, InterruptedException {

		// collect data from XHDetector and send the spectrum to local Plot 1 window
		EdeScanParameters simpleParams = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setDelayBetweenFrames(0);
		group1.setLabel("group1");
		group1.setNumberOfFrames(numberScans);
		group1.setTimePerScan(collectionPeriod);
		group1.setTimePerFrame(collectionPeriod);
		simpleParams.addGroup(group1);

		Detector xhdet = Finder.getInstance().find("XHDetector");
		xhdet.setAttribute(XHDetector.ATTR_LOADPARAMETERS, simpleParams);

		xhdet.collectData();

		xhdet.waitWhileBusy();
	}

	/**
	 * Collects a single frame of data and plots it.
	 * 
	 * @param writeData
	 *            - writes a file of the data
	 * @return double values from the detector - the FF and sector totals
	 */
	public static Double[] collectAndPlotSnapshot(boolean writeData, Integer collectionPeriod, Integer numberScans, String title) {

		try {
			collectData(collectionPeriod, numberScans);

			// will return a double[] of corrected data
			Detector xhdet = Finder.getInstance().find("XHDetector");
			Object results = xhdet.getAttribute(XHDetector.ATTR_READFIRSTFRAME);

			if (results != null) {
				DoubleDataset resultsDataSet = new DoubleDataset((double[]) results);
				SDAPlotter.plot(AlignmentPerspective.SPECTRAPLOTNAME, title, resultsDataSet);
			} else {
				logger.info("Nothing returned!");
			}

			if (writeData) {
				xhdet.getAttribute(XHDetector.ATTR_WRITEFIRSTFRAME);
			}

			NXDetectorData readout = (NXDetectorData) xhdet.readout();
			return readout.getDoubleVals();

		} catch (Exception e) {
			logger.error("exception while collecting snapshot from XHDetector", e);
			// popup
			MessageDialog
					.openError(PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell(),
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
							
							final Integer collectionPeriod = Activator.getDefault().getPreferenceStore()
									.getInt(I20_1PreferenceInitializer.LIVEMODETIME);
							final Double[] results = collectAndPlotSnapshot(false, collectionPeriod, 1, "Live reading ("
									+ collectionPeriod + "s integration, every " + refreshPeriod_s + " s)");

							allValues = ArrayUtils.add(allValues, results[1]);
							for (int i = 2; i < results.length; i++) {
								regionValues[i - 2] = ArrayUtils.add(regionValues[i - 2], results[i]);
							}

							PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
								@Override
								public void run() {
									txtAll.setText(String.format("%.1f", results[1]));
									for (int i = 2; i < results.length; i++) {
										txtSectors[i - 2].setText(String.format("%.1f", results[i]));
									}
								}
							});

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
	}

	@Override
	public void setROIs() {
		try {
			@SuppressWarnings("unchecked")
			List<? extends XHROI> regions = ((List<? extends XHROI>) theList.getValue());
			Device det = Finder.getInstance().find("XHDetector");
			det.setAttribute(XHDetector.ATTR_ROIS, regions.toArray(new XHROI[0]));
		} catch (DeviceException e) {
			logger.error("Exception fetching ROIs from XHDetector", e);
		}
	}

	@Override
	public void fetchLiveValues() {
		try {
			Device det = Finder.getInstance().find("XHDetector");
			XHROI[] regions = (XHROI[]) det.getAttribute(XHDetector.ATTR_ROIS);
			if (regions.length > 0) {
				Vector<XHROI> items = new Vector<XHROI>();
				for (XHROI region : regions) {
					items.add(region);
				}
				theList.setValue(items);
			}
		} catch (DeviceException e) {
			logger.error("Exception fetching ROIs from XHDetector", e);
		}
	}

	@Override
	public void showHideOverlay() {
		if (oProvider == null) {
			registerWithPlot1();
		}
		displayOverlay = !displayOverlay;
		refreshOverlay();
	}

	private void refreshOverlay() {
		removeOverlay();
		if (displayOverlay && !displayLockHeld) {
			addOverlayToPlot();
		}
	}

	private void registerWithPlot1() {
		getPlot1().getMainPlotter().registerOverlay(this);
	}

	private PlotView getPlot1() {
		IWorkbenchPage page = PlatformUI.getWorkbench().getWorkbenchWindows()[0].getActivePage();
		final IViewReference viewReference = page.findViewReference(PlotView.ID + "1", null);
		return ((PlotView) viewReference.getPart(true));
	}

	@Override
	public void registerProvider(OverlayProvider provider) {
		oProvider = (Overlay1DProvider) provider;

	}

	@Override
	public void unregisterProvider() {
		oProvider = null;
	}

	@Override
	public void removePrimitives() {
	}

	@Override
	public void areaSelected(final AreaSelectEvent event) {

		if (!displayOverlay) {
			return;
		}

		if (event.getMode() == 0) {
			// let go again
			final double x = event.getX();
			// fetch the current mouse position
			PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
				@Override
				public void run() {
					updateSelectedRegion(x, true, false);
				}
			});
		} else if (event.getMode() == 1) {
			// move while pressed
			final double x = event.getX();
			// fetch the current mouse position
			PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
				@Override
				public void run() {
					updateSelectedRegion(x, false, true);
				}

			});
		} else

		if (event.getMode() == 2) {
			// let go again
			final double x = event.getX();
			// fetch the current mouse position
			PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
				@Override
				public void run() {
					updateSelectedRegion(x, false, true);
					ignoreTableUpdates = false;
				}
			});
		}
	}

	private void updateSelectedRegion(final double x, final boolean xIsLower, boolean refresh) {
		int selectedValue = theList.getSelectedIndex();
		@SuppressWarnings("unchecked")
		List<? extends XHROI> regions = ((List<? extends XHROI>) theList.getValue());
		int upperLevel;
		int lowerLevel;
		if (xIsLower) {
			lowerLevel = (int) Math.round(x);
			upperLevel = regions.get(selectedValue).getUpperLevel();
		} else {
			lowerLevel = regions.get(selectedValue).getLowerLevel();
			upperLevel = (int) Math.round(x);
		}
		if (upperLevel > lowerLevel) {
			regions.get(selectedValue).setLowerLevel(lowerLevel);
			regions.get(selectedValue).setUpperLevel(upperLevel);
		} else {
			if (xIsLower) {
				regions.get(selectedValue).setLowerLevel(lowerLevel);
				regions.get(selectedValue).setUpperLevel(lowerLevel);
			} else {
				regions.get(selectedValue).setLowerLevel(upperLevel);
				regions.get(selectedValue).setUpperLevel(lowerLevel);
			}
		}
		ignoreTableUpdates = true;
		theList.setValue(regions);
		theList.setSelectedIndex(selectedValue);
		if (refresh) {
			// update the roi limit and change the overlay with a new line
			refreshOverlay();
		}
	}

	private void addOverlayToPlot() {

		displayLockHeld = true;
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {

				try {
					int selectedValue = theList.getSelectedIndex();

					int ymax = getCurrentYMax();

					@SuppressWarnings("unchecked")
					List<? extends XHROI> regions = ((List<? extends XHROI>) theList.getValue());

					for (int regionNum = 0; regionNum < regions.size(); regionNum++) {

						XHROI region = regions.get(regionNum);
						int minValue = region.getLowerLevel();
						int maxvalue = region.getUpperLevel();

						oProvider.begin(OverlayType.VECTOR2D);
						int minline = oProvider.registerPrimitive(PrimitiveType.LINE);
						int maxline = oProvider.registerPrimitive(PrimitiveType.LINE);
						if (regionNum == selectedValue) {
							oProvider.setColour(minline, java.awt.Color.RED);
							oProvider.setColour(maxline, java.awt.Color.RED);
						} else {
							oProvider.setColour(minline, java.awt.Color.GRAY);
							oProvider.setColour(maxline, java.awt.Color.GRAY);
						}
						oProvider.drawLine(minline, minValue, 0, minValue, ymax);
						oProvider.drawLine(maxline, maxvalue, 0, maxvalue, ymax);
						oProvider.end(OverlayType.VECTOR2D);
						lineReferences = ArrayUtils.add(lineReferences, minline);
						lineReferences = ArrayUtils.add(lineReferences, maxline);
					}
				} finally {
					displayLockHeld = false;
				}
			}
		});
	}

	private int getCurrentYMax() {
		Number yMax = getPlot1().getMainPlotter().getCurrentDataSet().max();
		return yMax.intValue();
	}

	private void removeOverlay() {
		for (int line : lineReferences) {
			oProvider.unregisterPrimitive(line);
		}
		lineReferences = new int[0];
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
