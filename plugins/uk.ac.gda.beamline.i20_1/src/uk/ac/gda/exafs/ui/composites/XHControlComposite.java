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

import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.device.DeviceException;
import gda.device.detector.EdeDetector;
import gda.device.detector.NXDetectorData;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.lima.LimaCCD.AccTimeMode;
import gda.device.lima.LimaCCD.AcqMode;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import gda.jython.InterfaceProvider;
import gda.jython.Jython;
import gda.jython.JythonServerStatus;
import gda.observable.IObserver;
import gda.scan.ede.datawriters.EdeDataConstants;

import java.beans.PropertyChangeListener;
import java.util.Date;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace.TraceType;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
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

import uk.ac.gda.beamline.i20_1.Activator;
import uk.ac.gda.beamline.i20_1.I20_1PreferenceInitializer;
import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumCollectionModel;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.ui.components.NumberEditorControl;

import com.swtdesigner.ResourceManager;

public class XHControlComposite extends Composite implements IObserver {

	public static final String ID = "uk.ac.gda.exafs.ui.composites.xhcontrolcomposite"; //$NON-NLS-1$

	private static final Logger logger = LoggerFactory.getLogger(XHControlComposite.class);

	private final IPlottingSystem plottingSystem;

	public volatile boolean continueLiveLoop = false;

	double[] allValues;
	double[][] regionValues;

	private ToolItem start;
	private ToolItem stop;
	private ToolItem snapshot;
	private ToolItem snapshotAndSave;

	private Thread liveLoop;
	private final FormToolkit toolkit;
	private final DetectorControlModel detectorControlModel;

	private NumberEditorControl txtSnapTime;
	private NumberEditorControl txtNumScansPerFrame;
	private NumberEditorControl txtLiveTime;
	private NumberEditorControl txtRefreshPeriod;
	private NumberEditorControl txtVertBinning;

	private final DoubleDataset strips;
	private ILineTrace lineTrace;
	private final EdeDetector detector;

	private NumberEditorControl txtCcdLineBegin;

	private ToolItem configDetector;

	private FrelonCcdDetectorData detectorData;

	private boolean firstTime;

	//	private static StripDetector getDetector(){
	//		return DetectorModel.INSTANCE.getCurrentDetector();
	//	}

	public static class DetectorControlModel extends ObservableModel {
		public static final String LIVE_INTEGRATION_TIME_PROP_NAME = "liveIntegrationTime";
		private double liveIntegrationTime;

		public static final String LIVE_MODE_REFRESH_PERIOD_PROP_NAME = "refreshPeriod";
		private double refreshPeriod;

		public static final String SNAPSHOT_INTEGRATION_TIME_PROP_NAME = "snapshotIntegrationTime";
		private double snapshotIntegrationTime;

		public static final String NUMBER_OF_ACCUMULATIONS_PROP_NAME = "numberOfAccumulations";
		private int numberOfAccumulations;

		public static final String VERTICAL_BINNING_PROP_NAME = "verticalBinning";
		private int verticalBinning;

		public static final String CCD_LINE_BEGIN_PROP_NAME = "ccdLineBegin";
		private int ccdLineBegin;

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
		public int getVerticalBinning() {
			return verticalBinning;
		}
		public void setVerticalBinning(int binValue) {
			firePropertyChange(VERTICAL_BINNING_PROP_NAME, verticalBinning, verticalBinning = binValue);
		}
		public int getCcdLineBegin() {
			return ccdLineBegin;
		}
		public void setCcdLineBegin(int roiBinOffset) {
			firePropertyChange(CCD_LINE_BEGIN_PROP_NAME, ccdLineBegin, ccdLineBegin = roiBinOffset);
		}
	}

	public XHControlComposite(Composite parent, IPlottingSystem plottingSystem) {
		super(parent, SWT.None);
		detector = DetectorModel.INSTANCE.getCurrentDetector();
		this.plottingSystem = plottingSystem;
		setupEnergySpectrumTraceLine();
		toolkit = new FormToolkit(parent.getDisplay());
		detectorControlModel = new DetectorControlModel();
		strips = detector.createDatasetForPixel();
		createUI();
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

	public void updateView(EdeDetector ededetector) {
		// TODO Auto-generated method stub
		if (ededetector instanceof EdeFrelon) {
			detectorData=(FrelonCcdDetectorData) detector.getDetectorData();
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					txtVertBinning.setEnabled(true);
					txtCcdLineBegin.setEnabled(true);
					configDetector.setEnabled(true);
				}
			});
		} else {
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					txtVertBinning.setEnabled(false);
					txtCcdLineBegin.setEnabled(false);
					configDetector.setEnabled(false);
				}
			});
		}
	}

	private synchronized void buildSections() {
		ScrolledForm scrolledform = toolkit.createScrolledForm(this);
		scrolledform.setLayoutData(new GridData(SWT.FILL,SWT.FILL, true, true));
		Form form = scrolledform.getForm();
		TableWrapLayout layout1 = new TableWrapLayout();
		layout1.numColumns = 3;
		form.getBody().setLayout(layout1);
		try {
			createTimesGroup(form.getBody());
			createSnapShotGroup(form.getBody());
			createFrelonBinAndOffsetGroup(form.getBody());
		} catch (Exception e) {
			UIHelper.showError("Unable to create sections", e.getMessage());
			logger.error("Unable to create sections", e);
		}
	}

	private void createFrelonBinAndOffsetGroup(Composite parentForm) throws Exception {
		@SuppressWarnings("static-access")
		final Section section = toolkit.createSection(parentForm, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		toolkit.paintBordersFor(section);
		section.setText("Frelon detector settings");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite frelonSectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(frelonSectionComposite);
		frelonSectionComposite.setLayout(new GridLayout(2, false));
		section.setClient(frelonSectionComposite);

		// vertical binning
		Label lbl  = toolkit.createLabel(frelonSectionComposite, "Vertical Binning", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		int storedVerticalBinning = Activator.getDefault().getPreferenceStore().getInt(I20_1PreferenceInitializer.VERTICALBINNING);
		if (storedVerticalBinning == 0) {
			storedVerticalBinning = 1;
		}
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.VERTICAL_BINNING_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(java.beans.PropertyChangeEvent evt) {
				Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.VERTICALBINNING, (int) evt.getNewValue());
			}
		});
		detectorControlModel.setVerticalBinning(storedVerticalBinning);
		//TODO replace the following with a combo having a fixed list
		txtVertBinning = new NumberEditorControl(frelonSectionComposite, SWT.None, detectorControlModel, DetectorControlModel.VERTICAL_BINNING_PROP_NAME, true);
		txtVertBinning.setUnit(UnitSetup.PIXEL.getText());
		txtVertBinning.setRange(1, FrelonCcdDetectorData.VERTICAL_BIN_SIZE_LIMIT);
		txtVertBinning.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		// ROI BIN Offset
		lbl = toolkit.createLabel(frelonSectionComposite, "CCD Line Begin", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		int ccdLineBegin = Activator.getDefault().getPreferenceStore().getInt(I20_1PreferenceInitializer.CCDLINEBEGIN);
		if (ccdLineBegin != 0) {
			ccdLineBegin = 0;
		}
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.CCD_LINE_BEGIN_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(java.beans.PropertyChangeEvent evt) {
				Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.CCDLINEBEGIN, (int) evt.getNewValue());
			}
		});
		detectorControlModel.setNumberOfAccumulations(ccdLineBegin);
		txtCcdLineBegin = new NumberEditorControl(frelonSectionComposite, SWT.None, detectorControlModel, DetectorControlModel.CCD_LINE_BEGIN_PROP_NAME, true);
		txtCcdLineBegin.setRange(0, FrelonCcdDetectorData.MAX_PIXEL-1);
		txtCcdLineBegin.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final ToolBar motorSectionTbar = new ToolBar(section, SWT.FLAT | SWT.HORIZONTAL);
		configDetector = new ToolItem(motorSectionTbar, SWT.NULL);
		configDetector.setImage(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/arrow_refresh.png").createImage());
		configDetector.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				configureFrelondetector(detectorControlModel.getVerticalBinning(), detectorControlModel.getCcdLineBegin());
			}
		});
		section.setTextClient(motorSectionTbar);

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}

	private void configureFrelondetector(int verticalBinning, int ccdLineBegin) {
		detectorData.setVerticalBinValue(verticalBinning);
		detectorData.setRoiBinOffset(ccdLineBegin);
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
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.SNAPSHOT_INTEGRATION_TIME_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(java.beans.PropertyChangeEvent evt) {
				Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.SNAPSHOTTIME, (double) evt.getNewValue());
			}
		});
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
		detectorControlModel.addPropertyChangeListener(DetectorControlModel.NUMBER_OF_ACCUMULATIONS_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(java.beans.PropertyChangeEvent evt) {
				Activator.getDefault().getPreferenceStore().setValue(I20_1PreferenceInitializer.SCANSPERFRAME, (int) evt.getNewValue());
			}
		});
		detectorControlModel.setNumberOfAccumulations(numberOfAccumulations);
		txtNumScansPerFrame = new NumberEditorControl(snapshotSectionComposite, SWT.None, detectorControlModel, DetectorControlModel.NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		txtNumScansPerFrame.setRange(1, SingleSpectrumCollectionModel.MAX_NO_OF_ACCUMULATIONS);
		txtNumScansPerFrame.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final ToolBar motorSectionTbar = new ToolBar(section, SWT.FLAT | SWT.HORIZONTAL);
		snapshot = new ToolItem(motorSectionTbar, SWT.NULL);
		snapshot.setImage(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/camera.png").createImage());
		snapshot.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					firstTime=true;
					collectAndPlotSnapshot(false, detectorControlModel.getSnapshotIntegrationTime(), detectorControlModel.getNumberOfAccumulations(), detectorControlModel.getSnapshotIntegrationTime() + "ms Snapshot");
				} catch (DeviceException | InterruptedException e) {
					UIHelper.showError("Unable to collect data", e.getMessage());
					logger.error("Unable to collect data", e);
				}
			}
		});
		snapshotAndSave = new ToolItem(motorSectionTbar, SWT.NULL);
		snapshotAndSave.setImage(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/camera_edit.png").createImage());
		snapshotAndSave.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					firstTime=true;
					collectAndPlotSnapshot(true, detectorControlModel.getSnapshotIntegrationTime(), detectorControlModel.getNumberOfAccumulations(), detectorControlModel.getSnapshotIntegrationTime() + "ms Snapshot");
				} catch (DeviceException | InterruptedException e) {
					UIHelper.showError("Unable to collect data", e.getMessage());
					logger.error("Unable to collect data", e);
				}
			}
		});
		section.setTextClient(motorSectionTbar);

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}

	@SuppressWarnings("static-access")
	private void createTimesGroup(Composite parentForm) throws Exception {
		final Section section = toolkit.createSection(parentForm, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		toolkit.paintBordersFor(section);
		section.setText("Live mode time settings");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite bendSelectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(bendSelectionComposite);
		bendSelectionComposite.setLayout(new GridLayout(2, false));
		section.setClient(bendSelectionComposite);

		Label lbl = toolkit.createLabel(bendSelectionComposite, "Accumulation time", SWT.NONE);
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
		txtLiveTime.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
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
		txtRefreshPeriod.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		final ToolBar motorSectionTbar = new ToolBar(section, SWT.FLAT | SWT.HORIZONTAL);
		start = new ToolItem(motorSectionTbar, SWT.NULL);
		start.setImage(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/control_play_blue.png").createImage());
		start.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				firstTime=true;
				startCollectingRates();
			}
		});

		stop = new ToolItem(motorSectionTbar, SWT.NULL);
		stop.setImage(ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/control_stop_blue.png").createImage());
		stop.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				stopCollectingRates();
			}
		});
		stop.setEnabled(false);
		section.setTextClient(motorSectionTbar);

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}


	private void collectData(Double collectionPeriod, int numberOfFrames, Integer scansPerFrame) throws DeviceException, InterruptedException {
		EdeScanParameters simpleParams = new EdeScanParameters();
		// collect data from XHDetector and send the spectrum to local Plot 1 window
		simpleParams.setIncludeCountsOutsideROIs(true);
		TimingGroup group1 = new TimingGroup();
		group1.setDelayBetweenFrames(0);
		group1.setLabel("group1");
		group1.setNumberOfFrames(numberOfFrames);
		group1.setNumberOfScansPerFrame(scansPerFrame);
		group1.setTimePerScan(collectionPeriod/1000);
		group1.setTimePerFrame(collectionPeriod/1000*scansPerFrame);
		if (firstTime) {
			if (detector instanceof EdeFrelon) {
				detectorData = (FrelonCcdDetectorData) detector.getDetectorData();
				detectorData.setTriggerMode(AcqTriggerMode.INTERNAL_TRIGGER);
				if (continueLiveLoop) {
					// live
					detectorData.setAcqMode(AcqMode.SINGLE);
					// detectorData.setExposureTime(collectionPeriod);
				} else { // snapshot
					detectorData.setAcqMode(AcqMode.ACCUMULATION);
					detectorData.setAccumulationTimeMode(AccTimeMode.LIVE);
				}
			}
			firstTime=false;
		}
		simpleParams.addGroup(group1);
		detector.prepareDetectorwithScanParameters(simpleParams, true);
		detector.collectData();
		detector.waitWhileBusy();
	}

	/**
	 * Collects a single frame of data and plots it.
	 *
	 * @param writeData - writes a file of the data
	 * @param collectionPeriod - ms
	 * @param title
	 * @return double values from the detector - the FF and sector totals
	 * @throws InterruptedException
	 * @throws DeviceException
	 */
	public Double[] collectAndPlotSnapshot(boolean writeData, Double collectionPeriod, Integer scansPerFrame,
			final String title) throws DeviceException, InterruptedException {

		collectData(collectionPeriod, 1,scansPerFrame);

		//get pixel corrected data from detector
		NXDetectorData readout = (NXDetectorData) detector.readout();
		final NexusGroupData ydata = readout.getData(detector.getName(), EdeDataConstants.DATA_COLUMN_NAME, NexusExtractor.SDSClassName);
		final double[] counts=(double[]) ydata.getBuffer();
		//Note: scientist wanted the live mode always plot in pixels not energy.
		//		final NexusGroupData xdata=readout.getData(detector.getName(), EdeDataConstants.ENERGY_COLUMN_NAME, NexusExtractor.SDSClassName);
		//		final double[] energies=(double[]) xdata.getBuffer();
		Integer[] pixels = detector.getPixels();
		final double[] xdata=new double[pixels.length];
		for (int i=0; i<pixels.length; i++) {
			xdata[i]=pixels[i].doubleValue();
		}

		if (counts != null) {
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					updatePlotWithData(title, new DoubleDataset(xdata, null), new DoubleDataset(counts, null));
				}
			});
		} else {
			logger.info("Nothing returned!");
		}

		if (writeData) {
			detector.writeLiveDataFile();
		}
		return readout.getDoubleVals();
	}

	private void updatePlotWithData(final String title, final DoubleDataset energies, final DoubleDataset results) {
		plottingSystem.getSelectedXAxis().setAxisAutoscaleTight(true);
		lineTrace.setData(energies, results);
		if (!plottingSystem.getTitle().equals(title)) {
			plottingSystem.setTitle(title);
		}
		plottingSystem.repaint();
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
					txtNumScansPerFrame.setEditable(false);
					txtRefreshPeriod.setEditable(false);
					txtSnapTime.setEditable(false);
				}
			});
			liveLoop = uk.ac.gda.util.ThreadManager.getThread(new Runnable() {
				@Override
				public void run() {
					try {
						int numberSectors = detector.getDetectorData().getRois().length;
						allValues = new double[0];
						regionValues = new double[numberSectors][0];
						while (continueLiveLoop
								&& InterfaceProvider.getScanStatusHolder().getScanStatus() == Jython.IDLE) {
							Date snapshotTime = new Date();

							String collectionPeriod_ms = DataHelper.roundDoubletoString(detectorControlModel.getLiveIntegrationTime());
							final Double[] results = collectAndPlotSnapshot(false, detectorControlModel.getLiveIntegrationTime(), 1,
									"Live reading (" + collectionPeriod_ms + " ms integration, every " + detectorControlModel.getRefreshPeriod()
									+ " s)");

							allValues = ArrayUtils.add(allValues, results[2]);
							for (int i = 3; i < results.length; i++) {
								regionValues[i - 3] = ArrayUtils.add(regionValues[i - 3], results[i]);
							}

							waitForRefreshPeriod(snapshotTime);
						}
					} catch (Exception e) {
						logger.error("Exception in loop refreshing the live XH detector rate", e);
					} finally {
						Display.getDefault().asyncExec(new Runnable() {
							@Override
							public void run() {
								// update the UI
								stopCollectingRates();
							}
						});
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
				txtNumScansPerFrame.setEditable(true);
				txtRefreshPeriod.setEditable(true);
				txtSnapTime.setEditable(true);
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
