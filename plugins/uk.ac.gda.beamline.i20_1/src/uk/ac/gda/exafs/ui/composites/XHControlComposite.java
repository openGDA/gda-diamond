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

import org.dawnsci.ede.DataHelper;
import org.dawnsci.ede.EdeDataConstants;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace.TraceType;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.Maths;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.ResourceManager;

import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.device.DeviceException;
import gda.device.detector.EdeDetector;
import gda.device.detector.NXDetectorData;
import gda.jython.InterfaceProvider;
import gda.jython.JythonStatus;
import gda.observable.IObserver;
import gda.scan.Scan.ScanStatus;
import gda.scan.ScanEvent;
import uk.ac.diamond.daq.concurrent.Async;
import uk.ac.gda.beamline.i20_1.Activator;
import uk.ac.gda.beamline.i20_1.I20_1PreferenceInitializer;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumCollectionModel;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.ui.components.NumberEditorControl;

public class XHControlComposite extends Composite implements IObserver {

	public static final String ID = "uk.ac.gda.exafs.ui.composites.xhcontrolcomposite"; //$NON-NLS-1$

	private static final Logger logger = LoggerFactory.getLogger(XHControlComposite.class);

	private final IPlottingSystem<Composite> plottingSystem;

	private volatile boolean continueLiveLoop = false;

	private ToolItem startLiveModeButton;
	private ToolItem stopLiveModeButton;
	private ToolItem takeSnapShotButton;
	private ToolItem takeSnapShotAndSaveButton;

	private Thread liveLoop;
	private final FormToolkit toolkit;
	private final DetectorControlModel detectorControlModel;

	private NumberEditorControl txtSnapTime;
	private NumberEditorControl txtNumScansPerFrame;
	private NumberEditorControl txtLiveTime;
	private NumberEditorControl txtLiveNumScansPerFrame;
	private NumberEditorControl txtRefreshPeriod;
	private ILineTrace lineTrace;
	private EdeDetector detector;

	private Dataset countsForI0;
	private Button showLiveI0ItCheckbox;
	protected boolean liveModeIsRunning;

	public static class DetectorControlModel extends ObservableModel {
		public static final String LIVE_INTEGRATION_TIME_PROP_NAME = "liveIntegrationTime";
		private double liveIntegrationTime;

		public static final String LIVE_MODE_REFRESH_PERIOD_PROP_NAME = "refreshPeriod";
		private double refreshPeriod;

		private static final String LIVE_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "liveNumberOfAccumulations";
		private int liveNumberOfAccumulations;

		private static final String LIVE_MODE_SHOW_I0IT = "liveModeShowI0It";
		private boolean liveModeShowI0It;

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

		public int getLiveNumberOfAccumulations() {
			return liveNumberOfAccumulations;
		}
		public void setLiveNumberOfAccumulations(int numberOfAccumulations) {
			firePropertyChange(LIVE_NUMBER_OF_ACCUMULATIONS_PROP_NAME, liveNumberOfAccumulations, liveNumberOfAccumulations = numberOfAccumulations);
		}

		public boolean getLiveModeShowI0It() {
			return liveModeShowI0It;
		}
		public void setLiveModeShowI0It(boolean showI0It) {
			firePropertyChange(LIVE_MODE_SHOW_I0IT, liveModeShowI0It, liveModeShowI0It = showI0It);
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

	public XHControlComposite(Composite parent, IPlottingSystem<Composite> plottingSystem) {
		super(parent, SWT.None);
		detector = DetectorModel.INSTANCE.getCurrentDetector();
		this.plottingSystem = plottingSystem;
		setupEnergySpectrumTraceLine();
		toolkit = new FormToolkit(parent.getDisplay());
		detectorControlModel = new DetectorControlModel();
		createUI();

		// Update detector reference when current detector changes.
		DetectorModel.INSTANCE.addPropertyChangeListener(event -> {
			if (event.getPropertyName().equals(DetectorModel.DETECTOR_CONNECTED_PROP_NAME)) {
				detector = DetectorModel.INSTANCE.getCurrentDetector();
				logger.debug("Updating live view to use {} detector", detector.getName());
			}
		});

		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(this);

	}

	private void setupEnergySpectrumTraceLine() {
		plottingSystem.getSelectedXAxis().setAxisAutoscaleTight(true);
		plottingSystem.setShowLegend(false);
		lineTrace = plottingSystem.createLineTrace("Detector Live Data");
		lineTrace.setLineWidth(1);
		lineTrace.setTraceColor(Display.getDefault().getSystemColor(SWT.COLOR_BLUE));
		lineTrace.setTraceType(TraceType.SOLID_LINE);
		plottingSystem.addTrace(lineTrace);
	}

	private void createUI() {
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		buildSections();
	}

	private synchronized void buildSections() {
		ScrolledForm scrolledform = toolkit.createScrolledForm(this);
		scrolledform.setLayoutData(new GridData(SWT.FILL,SWT.FILL, true, true));
		Form form = scrolledform.getForm();
		TableWrapLayout layout1 = new TableWrapLayout();
		layout1.numColumns = 3;
		form.getBody().setLayout(layout1);
		try {
			createLiveModeGroup(form.getBody());
			createSnapShotGroup(form.getBody());
		} catch (Exception e) {
			displayAndLogMessage("Unable to create sections", e);
		}
	}

	@SuppressWarnings("static-access")
	private void createSnapShotGroup(Composite parentForm) throws Exception {
		final Section section = toolkit.createSection(parentForm, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		toolkit.paintBordersFor(section);
		section.setText("Snapshot mode time settings");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite snapshotSectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(snapshotSectionComposite);
		snapshotSectionComposite.setLayout(new GridLayout(2, false));
		section.setClient(snapshotSectionComposite);

		// Integration time
		Label lbl  = toolkit.createLabel(snapshotSectionComposite, "Accumulation time", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Double storedSnapShotTime = Activator.getDefault().getPreferenceStore()
				.getDouble(I20_1PreferenceInitializer.SNAPSHOTTIME);
		if (storedSnapShotTime == 0.0) {
			storedSnapShotTime = 1.0;
		}
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.SNAPSHOT_INTEGRATION_TIME_PROP_NAME, event ->
			Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.SNAPSHOTTIME, (double) event.getNewValue()));

		detectorControlModel.setSnapshotIntegrationTime(storedSnapShotTime);
		txtSnapTime = new NumberEditorControl(snapshotSectionComposite, SWT.None, detectorControlModel, DetectorControlModel.SNAPSHOT_INTEGRATION_TIME_PROP_NAME, true);
		txtSnapTime.setUnit(UnitSetup.MILLI_SEC.getText());
		txtSnapTime.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		txtSnapTime.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		// Number of accumulations
		lbl = toolkit.createLabel(snapshotSectionComposite, "Number of accumulations", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		int numberOfAccumulations = Activator.getDefault().getPreferenceStore()
				.getInt(I20_1PreferenceInitializer.SCANSPERFRAME);
		if (numberOfAccumulations == 0) {
			numberOfAccumulations = 1;
		}
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.NUMBER_OF_ACCUMULATIONS_PROP_NAME, event ->
			Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.SCANSPERFRAME, (int) event.getNewValue()));
		detectorControlModel.setNumberOfAccumulations(numberOfAccumulations);
		txtNumScansPerFrame = new NumberEditorControl(snapshotSectionComposite, SWT.None, detectorControlModel, DetectorControlModel.NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		txtNumScansPerFrame.setRange(1, SingleSpectrumCollectionModel.MAX_NO_OF_ACCUMULATIONS);
		txtNumScansPerFrame.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final ToolBar motorSectionTbar = new ToolBar(section, SWT.FLAT | SWT.HORIZONTAL);
		takeSnapShotButton = new ToolItem(motorSectionTbar, SWT.NULL);
		takeSnapShotButton.setToolTipText("Take snapshot");
		takeSnapShotButton.setImage(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/camera.png").createImage());
		takeSnapShotButton.addListener(SWT.Selection, event ->  {
			try {
				prepareDetector(detectorControlModel.getSnapshotIntegrationTime(), 1, detectorControlModel.getNumberOfAccumulations());
				collectAndPlotSnapshot(false, detectorControlModel.getSnapshotIntegrationTime() + "ms Snapshot");
			} catch (DeviceException | InterruptedException e) {
				displayAndLogMessage("Unable to collect data", e);
			}
		});
		takeSnapShotAndSaveButton = new ToolItem(motorSectionTbar, SWT.NULL);
		takeSnapShotAndSaveButton.setToolTipText("Take snapshot and save to file");
		takeSnapShotAndSaveButton.setImage(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/camera_edit.png").createImage());
		takeSnapShotAndSaveButton.addListener(SWT.Selection, event -> {
			try {
				prepareDetector(detectorControlModel.getSnapshotIntegrationTime(), 1, detectorControlModel.getNumberOfAccumulations());
				collectAndPlotSnapshot(true, detectorControlModel.getSnapshotIntegrationTime() + "ms Snapshot");
			} catch (DeviceException | InterruptedException e) {
				displayAndLogMessage("Unable to collect data", e);
			}
		});

		section.setTextClient(motorSectionTbar);

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}

	@SuppressWarnings("static-access")
	private void createLiveModeGroup(Composite parentForm) throws Exception {

		// ... Setup listener for model changes and get initial values from preference store

		// Live mode integration time
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.LIVE_INTEGRATION_TIME_PROP_NAME, event ->
			Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.LIVEMODETIME, (double) event.getNewValue()));
		Double storedLiveTime = Activator.getDefault().getPreferenceStore()
				.getDouble(I20_1PreferenceInitializer.LIVEMODETIME);
		if (storedLiveTime == 0.0) {
			storedLiveTime = 1.0;
		}
		detectorControlModel.setLiveIntegrationTime(storedLiveTime);

		// Live mode refresh period
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.LIVE_MODE_REFRESH_PERIOD_PROP_NAME, event ->
			Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.REFRESHRATE, (double) event.getNewValue()));
		double refreshPeroid = Activator.getDefault().getPreferenceStore()
				.getDouble(I20_1PreferenceInitializer.REFRESHRATE);
		if (refreshPeroid == 0.0) {
			refreshPeroid = 1.0;
		}
		detectorControlModel.setRefreshPeriod(refreshPeroid);

		// Live mode num accumulations.
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.LIVE_NUMBER_OF_ACCUMULATIONS_PROP_NAME, event ->
			Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.LIVEMODESCANSPERFRAME, (int) event.getNewValue()));

		int storedLiveNumAccumulations = Activator.getDefault().getPreferenceStore()
				.getInt(I20_1PreferenceInitializer.LIVEMODESCANSPERFRAME);
		if (storedLiveNumAccumulations < 1) {
			storedLiveNumAccumulations = 1;
		}

		detectorControlModel.setLiveNumberOfAccumulations(storedLiveNumAccumulations);
		detectorControlModel.setLiveModeShowI0It(false);

		// ... Setup the widgets and initialise using values from preference store

		final Section section = toolkit.createSection(parentForm, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		toolkit.paintBordersFor(section);
		section.setText("Live mode time settings");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite bendSelectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(bendSelectionComposite);
		bendSelectionComposite.setLayout(new GridLayout(2, false));
		section.setClient(bendSelectionComposite);

		// Live mode accumulation time
		Label lbl = toolkit.createLabel(bendSelectionComposite, "Accumulation time", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		txtLiveTime = new NumberEditorControl(bendSelectionComposite, SWT.None, detectorControlModel, DetectorControlModel.LIVE_INTEGRATION_TIME_PROP_NAME, true);
		txtLiveTime.setUnit(UnitSetup.MILLI_SEC.getText());
		txtLiveTime.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		txtLiveTime.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		// Live mode number of accumulations widgets. imh 14/9/2015
		lbl = toolkit.createLabel(bendSelectionComposite, "Number of accumulations", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		txtLiveNumScansPerFrame = new NumberEditorControl(bendSelectionComposite, SWT.None, detectorControlModel, DetectorControlModel.LIVE_NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		txtLiveNumScansPerFrame.setRange(1, SingleSpectrumCollectionModel.MAX_NO_OF_ACCUMULATIONS);
		txtLiveNumScansPerFrame.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		// Live mode refresh period
		lbl =  toolkit.createLabel(bendSelectionComposite, "Refresh period", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		txtRefreshPeriod = new NumberEditorControl(bendSelectionComposite, SWT.None, detectorControlModel, DetectorControlModel.LIVE_MODE_REFRESH_PERIOD_PROP_NAME, true);
		txtRefreshPeriod.setUnit(UnitSetup.SEC.getText());
		txtRefreshPeriod.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		txtRefreshPeriod.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		// Show live I0It checkbox widget.
		lbl =  toolkit.createLabel(bendSelectionComposite, "Live ln(I0/It) mode", SWT.NONE);
		lbl.setToolTipText("Enable/disable live ln(I0/It) mode.\n(Take a snapshot to set the data used for I0)");
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		showLiveI0ItCheckbox = toolkit.createButton(bendSelectionComposite, "", SWT.CHECK);
		showLiveI0ItCheckbox.setToolTipText("Take a snapshot to enable live ln(I0/It) mode");
		showLiveI0ItCheckbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		showLiveI0ItCheckbox.setEnabled(false); // intitially disabled, will be enabled after snaphot has been taken

		// Setup listener used to update model when I0It checkbox is (de)selected
		SelectionListener listener = new SelectionListener() {
			@Override
			public void widgetSelected( SelectionEvent e ) {
				boolean isChecked =  showLiveI0ItCheckbox.getSelection();
				detectorControlModel.setLiveModeShowI0It(isChecked);
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				widgetSelected(e);
			}
		};
		showLiveI0ItCheckbox.addSelectionListener(listener);
		showLiveI0ItCheckbox.setSelection(detectorControlModel.getLiveModeShowI0It());
		liveModeIsRunning = false;

		// 'Start' live mode button
		final ToolBar motorSectionTbar = new ToolBar(section, SWT.FLAT | SWT.HORIZONTAL);
		startLiveModeButton = new ToolItem(motorSectionTbar, SWT.NULL);
		startLiveModeButton.setToolTipText("Start live mode");
		startLiveModeButton.setImage(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/control_play_blue.png").createImage());
		startLiveModeButton.addListener(SWT.Selection, event-> {
			liveModeIsRunning = true;
			startCollectingRates();
		});

		// 'Stop' live mode button
		stopLiveModeButton = new ToolItem(motorSectionTbar, SWT.NULL);
		stopLiveModeButton.setToolTipText("Stop live mode");
		stopLiveModeButton.setImage(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/control_stop_blue.png").createImage());
		stopLiveModeButton.addListener(SWT.Selection, event -> stopCollectingRates());
		stopLiveModeButton.setEnabled(false);
		section.setTextClient(motorSectionTbar);

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}

	/**
	 * Setup detector with spectrum acquisition parameters
	 * @param accumulationTime
	 * @param numberOfFrames
	 * @param numAccumulations
	 * @throws DeviceException
	 */
	private void prepareDetector(Double accumulationTime, int numberOfFrames, Integer numAccumulations) throws DeviceException {
		logger.debug("Preparing {} detector with scan parameters : {} frames, {} ms accumulation time, {} accumulations",
				detector.getName(), numberOfFrames, accumulationTime, numAccumulations);
		EdeScanParameters simpleParams = new EdeScanParameters();
		// collect data from XHDetector and send the spectrum to local Plot 1 window
		simpleParams.setIncludeCountsOutsideROIs(true);
		TimingGroup group1 = new TimingGroup();
		group1.setDelayBetweenFrames(0);
		group1.setLabel("group1");
		group1.setNumberOfFrames(numberOfFrames);
		group1.setNumberOfScansPerFrame(numAccumulations);
		group1.setTimePerScan(accumulationTime/1000);
		group1.setTimePerFrame(accumulationTime/1000*numAccumulations);
		simpleParams.addGroup(group1);
		detector.prepareDetectorwithScanParameters(simpleParams);
		if (detector.getName().equals("frelon")) {
			detector.configureDetectorForTimingGroup(simpleParams.getGroups().get(0));
		}
	}

	private void collectData() throws DeviceException, InterruptedException {
		detector.collectData();
		detector.waitWhileBusy();
	}

	/**
	 * Collects a single frame of data and plots it.
	 *
	 * @param writeData - writes a file of the data
	 * @param collectionPeriod - ms
	 * @param title
	 * @throws InterruptedException
	 * @throws DeviceException
	 */
	private void collectAndPlotSnapshot(boolean writeData, final String title) throws DeviceException, InterruptedException {

		collectData();

		// Readout count data from detector and put into dataset
		NXDetectorData readout = (NXDetectorData) detector.readout();
		final NexusGroupData ydata = readout.getData(detector.getName(), EdeDataConstants.DATA_COLUMN_NAME, NexusExtractor.SDSClassName);

		if (ydata.getBuffer() != null) {

			Dataset detectorCounts = ydata.toDataset().copy(DoubleDataset.class);

			// Make copy of the count data for using with live I0/It view (if taking a snapshot, i.e. not currently in 'live' mode).
			if (!liveModeIsRunning) {
				countsForI0 = detectorCounts.copy(DoubleDataset.class);
				// Enable live ln(I0/It) mode button once I0 data has been collected
				runInGuiThread(() -> showLiveI0ItCheckbox.setEnabled(true));
			}

			// If live mode is running and show live I0It is selected, convert 'counts' to ln( I0/It )
			if (liveModeIsRunning && detectorControlModel.getLiveModeShowI0It() &&
					countsForI0 != null && countsForI0.getSize() == detectorCounts.getSize()) {
				Dataset div = Maths.divide(countsForI0, detectorCounts);
				// Calculate logItI0 and put the values in detectorCounts dataset
				Maths.log(div, detectorCounts);
			}

			//Note : X axis for live mode plot is always pixels, not energy.
			Dataset pixelIndex = DatasetFactory.createFromObject(DoubleDataset.class, detector.getPixels());

			runInGuiThread(() -> updatePlotWithData(title, pixelIndex, detectorCounts));

		} else {
			logger.info("Nothing returned!");
		}

		if (writeData) {
			detector.writeLiveDataFile();
		}
	}

	private void updatePlotWithData(final String title, final Dataset xData, final Dataset yData) {
		plottingSystem.getSelectedXAxis().setAxisAutoscaleTight(true);
		lineTrace.setData(xData, yData);
		if (!plottingSystem.getTitle().equals(title)) {
			plottingSystem.setTitle(title);
		}
		plottingSystem.repaint();
	}

	private void setAllowLiveLoop(boolean allowLiveLoop) {
		continueLiveLoop = allowLiveLoop;
	}

	private boolean liveLoopIsAllowed() throws DeviceException {
		return continueLiveLoop
				&& InterfaceProvider.getScanStatusHolder().getScanStatus() == JythonStatus.IDLE
				&& !detector.isBusy();
	}

	private void startCollectingRates() {
		if (liveLoop != null && liveLoop.isAlive()) {
			//live loop is already running
			return;
		}

		setAllowLiveLoop(true);
		liveLoop = null;

		runInGuiThread(() -> {
			startLiveModeButton.setEnabled(false);
			stopLiveModeButton.setEnabled(true);
			takeSnapShotButton.setEnabled(false);
			takeSnapShotAndSaveButton.setEnabled(false);
			txtNumScansPerFrame.setEditable(false);
			txtRefreshPeriod.setEditable(false);
			txtSnapTime.setEditable(false);
		});

		liveLoop = new Thread( () -> {
			try {
				double lastIntegrationTime = 0;
				int lastNumAccumulations = 0;

				while (liveLoopIsAllowed()) {
					long startTime = System.currentTimeMillis();

					double integrationTime = detectorControlModel.getLiveIntegrationTime();
					int numAccumulations = detectorControlModel.getLiveNumberOfAccumulations();
					if (integrationTime != lastIntegrationTime || numAccumulations != lastNumAccumulations) {
						prepareDetector(integrationTime, 1, numAccumulations);
						lastIntegrationTime = integrationTime;
						lastNumAccumulations = numAccumulations;
					}

					String title = String.format("Live reading (%s ms integration, %d accumulations every %s sec)",
							DataHelper.roundDoubletoStringWithOptionalDigits(integrationTime), numAccumulations,
							DataHelper.roundDoubletoStringWithOptionalDigits(detectorControlModel.getRefreshPeriod()));

					collectAndPlotSnapshot(false, title);
					// Sleep for a bit to get the required refresh interval (convert refresh period from secs to milliseconds)
					double sleepTime = 1000*detectorControlModel.getRefreshPeriod() - (System.currentTimeMillis() - startTime);
					if (sleepTime > 0) {
						logger.info("Sleeping for {} ms", sleepTime);
						Thread.sleep((long) sleepTime);
					}
				}
			} catch (Exception ex) {
				StringBuilder message = new StringBuilder();
				message.append("Problem collecting data in live mode view : \n");
				if (!detector.isConfigured()) {
					message.append(detector.getName()+" detector has not been configured.");
				} else {
					message.append(ex.getMessage());
				}
				runInGuiThread(() -> MessageDialog.openWarning(getParent().getShell(), "Problem collecting data", message.toString()));
				logger.error(message.toString(), ex);
			} finally {
				setAllowLiveLoop(false);
				runInGuiThread(this::stopCollectingRates);
			}
		});

		liveLoop.start();
	}

	public void stopCollectingRates() {
		// Wait for collection thread to finish and update start/stop button status.
		// This is done in a separate thread so GUI doesn't lock up while waiting for collection to finish.
		Async.execute(() -> {
			try {
				setAllowLiveLoop(false);

				// Wait for collection thread to finish current acquisition
				liveLoop.join();

				liveModeIsRunning = false;

				// Get GUI thread and update button status
				runInGuiThread(() -> {
					startLiveModeButton.setEnabled(true);
					stopLiveModeButton.setEnabled(false);
					takeSnapShotButton.setEnabled(true);
					takeSnapShotAndSaveButton.setEnabled(true);
				});
			} catch (InterruptedException e) {
				logger.error("Exception in stopCollectingRates : ", e);
				Thread.currentThread().interrupt();
			}
		});

		runInGuiThread(() -> {
			txtNumScansPerFrame.setEditable(true);
			txtRefreshPeriod.setEditable(true);
			txtSnapTime.setEditable(true);
		});
	}

	@Override
	public void update(Object source, Object arg) {
		if (arg instanceof ScanEvent) {
			ScanEvent scanEvent = (ScanEvent) arg;
			ScanStatus status = scanEvent.getLatestStatus();

			// disable start, stop buttons at scan start/if scan is running
			Boolean enable = false;
			if (status.isRunning()) { // NB isRunning == *false* when cscan is running! (status = 'Not started')
				// stop the live collection loop
				if (continueLiveLoop) {
					stopCollectingRates();
				}
			} else 	if (status.isComplete() || status.isAborting()) {
				// enable start/stop buttons at end of scan
				enable = true;
			}

			final boolean enableWidgets = enable;
			logger.debug("update' called : Scan status {}, Enable widgets ? : {}", status, enableWidgets);
			runInGuiThread(() -> {
				if (startLiveModeButton.getEnabled() != enableWidgets
				    || stopLiveModeButton.getEnabled() != enableWidgets) {
					logger.debug("Updating widget enabled state in GUI");
					startLiveModeButton.setEnabled(enableWidgets);
					stopLiveModeButton.setEnabled(enableWidgets);
					takeSnapShotButton.setEnabled(enableWidgets);
					takeSnapShotAndSaveButton.setEnabled(enableWidgets);
				}
			});
		}
	}

	/**
	 * Asynchronously execute the call method of the runnable in the GUI thread.
	 * @param runnable
	 */
	private void runInGuiThread(Runnable runnable) {
		PlatformUI.getWorkbench().getDisplay().asyncExec(runnable);
	}

	/**
	 * Display a message warning dialog box and put stack trace into in the log.
	 * @param info
	 * @param t
	 */
	private void displayAndLogMessage(String info, Throwable t) {
		UIHelper.showError(info, t.getMessage());
		logger.error(info, t);
	}
}
