/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.experiment.ui;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.ArrayUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.apache.commons.math3.util.Pair;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.VerifyEvent;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.dialogs.ListSelectionDialog;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.factory.Finder;
import gda.jython.IJythonServerStatusObserver;
import gda.jython.InterfaceProvider;
import gda.scan.Scan.ScanStatus;
import gda.scan.ScanEvent;
import gda.scan.TurboSlitTimingGroup;
import gda.scan.TurboXasMotorParameters;
import gda.scan.TurboXasNexusTree;
import gda.scan.TurboXasParameters;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.devices.detector.xspress3.Xspress3;
import uk.ac.gda.exafs.calibration.ui.EnergyCalibrationComposite;
import uk.ac.gda.exafs.data.EdeDataStore;
import uk.ac.gda.exafs.experiment.ui.TurboXasTimingGroupTableView.TimingGroupParamType;
import uk.ac.gda.exafs.ui.composites.ScannableListEditor;
import uk.ac.gda.exafs.ui.composites.ScannablePositionsComposite;
import uk.ac.gda.exafs.ui.composites.SpectrumEventsEditor;

/**
 * View for setting up and running TurboXas scans.
 * The GUI is used to setup a {@link TurboXasParameters} object which then be saved to an XML file or
 * used to run a scan. A previously saved XML file can also be loaded into the GUI. <p>
 * Listeners are used to update start, end energy, sample name etc from Text boxes, and a {@link TurboXasTimingGroupTableView} is
 * used to handle editing of the timing groups (via. a JFace {@link TableViewer}.
 * @since May2017
 *
 */
public class TurboXasExperimentView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.turboXasExperimentView";

	private static Logger logger = LoggerFactory.getLogger(TurboXasExperimentView.class);

	protected FormToolkit toolkit;

	private Text sampleNameTextbox;
	private Text startEnergyTextbox;
	private Text endEnergyTextbox;
	private Text energyStepsizeTextbox;

	private Text startPositionTextbox;
	private Text endPositionTextbox;
	private Text positionStepsizeTextbox;
	private Button usePositionsForScanButton;

	private EnergyCalibrationComposite calibrationComposite;
	private Button createAsciiFileButton;

	private Section energySection;
	private Section positionSection;

	private TurboXasTimingGroupTableView timingGroupTable;
	private TurboXasParameters turboXasParameters; // parameters being viewed in gui

	private String unitStringForPosition = "[mm]";

	private String[] motorNames = new String[]{"turbo_xas_slit"};

	private Combo motorCombo;

	private String[] detectorNames = new String[]{"scaler_for_zebra"};

	private Map<String,String> detectorNamesMap;
	private Map<String, String> defaultPlottedFields;
	private List<String> defaultExtraScannables;

	private Button[] detectorCheckboxes;

	private Button useTrajectoryScanButton;

	private Button useTwoWayScanButton;

	private Button startScanButton;

	private Shell shell;

	private static String PREFERENCE_STORE_KEY = "turboxas_settings_key";

	private List<Pair<String, String>> namesOfDatasetsToAverage = new ArrayList<>();

	private ScannablePositionsComposite scannablePositionsComposite;

	@Override
	public void createPartControl(final Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		shell = parent.getShell();

		if (detectorNamesMap == null) {
			detectorNamesMap = new LinkedHashMap<>();
			for(String name : detectorNames) {
				detectorNamesMap.put(name, name);
			}
		}

		final SashForm parentComposite = new SashForm(parent, SWT.VERTICAL);
		parentComposite.SASH_WIDTH = 3;
		try {
			turboXasParameters = new TurboXasParameters();
			createSections(parentComposite);
		} catch (Exception e) {
			UIHelper.showWarning("Problem creating controls for TurboXas Experiment view", e.getMessage());
			logger.warn("Problem creating controls", e);
		}
		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);

		// Update parameters from gui when view is disposed (but before widgets have been disposed).
		// The 'dispose()' function is called later, which saves the values to preference store.
		parent.addDisposeListener(disposeEvent -> updateParametersFromGui());
	}

	/**
	 * Store the last scan filename, update widgets in gui in response to scan starts/stop status.
	 */
	final IJythonServerStatusObserver serverObserver = (theObserved, changeCode) -> Display.getDefault().asyncExec(() -> {
		if (changeCode instanceof ScanEvent) {
			ScanEvent scanEvent = (ScanEvent) changeCode;
			ScanStatus status = scanEvent.getLatestStatus();
			logger.debug("ScanEvent = {}, ScanStatus = {}",changeCode.toString(), status.toString());
			if (status.isRunning()) {
				updateWidgets(true);
			} else if (status.isComplete() || status.isAborting()) {
				updateWidgets(false);
			}
		}
	});


	/**
	 * Update widgets when scan is running/stopped
	 * @param scanIsRunning
	 */
	private void updateWidgets(boolean scanIsRunning) {
		startScanButton.setEnabled(!scanIsRunning);
	}

	protected void createSections(final SashForm parent) {
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1,false));
		ScrolledForm scrolledform = toolkit.createScrolledForm(composite);
		scrolledform.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Form form = scrolledform.getForm();

		form.getBody().setLayout(new GridLayout(1, true));
		toolkit.decorateFormHeading(form);

		scrolledform.setText("Turbo XAS experiment setup");
		createSampleNameEnergySections(form.getBody());
		createEnergyCalibrationSection(form.getBody());
		createExtraScannablesSection(form.getBody());
		createTimingGroupSection(form.getBody());
		createScannablePositionsSection(form.getBody());
		createSpectrumEventsSection(form.getBody());
		createHardwareOptionsSection(form.getBody());
		createRunningAverageSection(form.getBody());
		createLoadSaveSection(form.getBody());
		loadSettingsFromPreferenceStore();
		addDefaultExtraScannablesToParameters();

		addListenersVerifiers();
		form.layout();
	}

	public void createScannablePositionsSection(Composite parent) {
		Section section = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE);
		section.setText("Set scannable positions");
		section.setExpanded(true);
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite mainComposite = toolkit.createComposite(section, SWT.NONE);
		mainComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		section.setClient(mainComposite);

		scannablePositionsComposite = new ScannablePositionsComposite(mainComposite, toolkit);
		scannablePositionsComposite.addSection();
		scannablePositionsComposite.addIObserver(this::updateScannablePositionsInModel);
	}

	public void createSpectrumEventsSection(Composite parent) {
		Section section = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE);
		section.setText("Set spectrum events");
		section.setExpanded(true);
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite mainComposite = toolkit.createComposite(section, SWT.NONE);
		mainComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		section.setClient(mainComposite);

		Button openEditorButton = new Button(mainComposite, SWT.PUSH);
		openEditorButton.setText("Edit spectrum events...");
		openEditorButton.setSelection(false);
		openEditorButton.addListener(SWT.Selection, e -> {
			SpectrumEventsEditor editor = new SpectrumEventsEditor(mainComposite.getShell());
			editor.setTableValues(turboXasParameters.getSpectrumEvents());
			editor.setBlockOnOpen(true);
			if (editor.open() == Window.OK) {
				turboXasParameters.setSpectrumEvents(editor.getTableValues());
			}
		});
	}

	/**
	 * Updates values in {@link #scannablePositionsComposite} from values in TurboXasParameters object
	 */
	private void setScannablePositionsFromModel() {
		scannablePositionsComposite.setCollectMultipleSpectra(turboXasParameters.isRunMappingScan());
		scannablePositionsComposite.setScannableName(turboXasParameters.getScannableToMove());
		scannablePositionsComposite.setScannablePositions(turboXasParameters.getScannablePositions());
	}

	/**
	 * Update TurboXasParameters mapping parameters from values currently stored in {@link #scannablePositionsComposite}.
	 * @param source
	 * @param arg
	 */
	private void updateScannablePositionsInModel(Object source, Object arg) {
		turboXasParameters.setRunMappingScan(scannablePositionsComposite.isCollectMultipleSpectra());
		turboXasParameters.setScannableToMove(scannablePositionsComposite.getScannableName());
		turboXasParameters.setScannablePositions(scannablePositionsComposite.getScannablePositions());
	}

	private void createHardwareOptionsSection(Composite parent) {
		Composite mainComposite = makeSectionAndComposite(parent, "Detector and motor options", 2);

		makeLabel(mainComposite, "Motor to move during scan");
		motorCombo = new Combo(mainComposite, SWT.READ_ONLY);
		motorCombo.setItems(motorNames);
		motorCombo.select(0);

		useTrajectoryScanButton = new Button(mainComposite, SWT.CHECK);
		useTrajectoryScanButton.setText("Use trajectory scan ");
		useTrajectoryScanButton.setSelection(false);

		useTwoWayScanButton = new Button(mainComposite, SWT.CHECK);
		useTwoWayScanButton.setText("Do bi-drectional scan ");
		useTwoWayScanButton.setSelection(false);

		addDetectorSelectionControls(mainComposite);
	}

	/**
	 *
	 * @return Names of the currently selected detectors
	 */
	private String[] getSelectedDetectors() {
		String[] selectedDetectors = new String[]{};
		for(Button detectorCheckbox : detectorCheckboxes) {
			if (detectorCheckbox.getSelection()) {
				selectedDetectors = (String[]) ArrayUtils.add(selectedDetectors, detectorCheckbox.getData());
			}
		}
		return selectedDetectors;
	}

	/**
	 *
	 * @return User friendly names of the the currently selected detectors
	 */
	private String[] getSelectedDetectorNames() {
		String[] selectedDetectors = new String[]{};
		for(Button detectorCheckbox : detectorCheckboxes) {
			if (detectorCheckbox.getSelection()) {
				selectedDetectors = (String[]) ArrayUtils.add(selectedDetectors, detectorCheckbox.getText());
			}
		}
		return selectedDetectors;
	}

	private void addDetectorSelectionControls(Composite parent) {

		makeLabel(parent, "Detectors to use during scan : ");

		Composite detComp = new Composite(parent, SWT.NONE);
		int numDetectors = detectorNamesMap.size();
		detComp.setLayout(new GridLayout(numDetectors, false));
		detectorCheckboxes = new Button[numDetectors];
		int i=0;
		for(String name : detectorNamesMap.keySet() ) {
			detectorCheckboxes[i] = new Button(detComp, SWT.CHECK);
			detectorCheckboxes[i].setText(name);  // GUI label for the detector
			detectorCheckboxes[i].setData(detectorNamesMap.get(name)); // name of the detector object
			detectorCheckboxes[i].setToolTipText(detectorNamesMap.get(name));
			detectorCheckboxes[i].setSelection(false);
			detectorCheckboxes[i].setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			i++;
		}
	}

	/**
	 * @return Return motor parameters for current turboXasParameter settings.
	 * It tries to set the high and low limits from the currently selected motor.
	 */
	private TurboXasMotorParameters getMotorParameters() {
		TurboXasMotorParameters motorParams = turboXasParameters.getMotorParameters();

		// Try to get motor to be moved so can find upper and lower motion limits
		String motorName = motorCombo.getText();
		Scannable motor = Finder.getInstance().find(motorName);
		if (motor!=null) {
			motorParams.setMotorLimits(motor);
		}
		return motorParams;
	}

	private Label makeLabel(Composite parent, String labelText) {
		Label label = toolkit.createLabel(parent, labelText, SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		return label;
	}

	private Text makeLabelAndTextBox(Composite parent, String labelText) {
		return makeLabelAndTextBox(parent, labelText, SWT.BORDER);
	}

	private Text makeLabelAndTextBox(Composite parent, String labelText, String unitString) {
		return makeLabelAndTextBox(parent, labelText+" "+unitString, SWT.BORDER);
	}

	private Text makeLabelAndTextBox(Composite parent, String labelText, int style) {
		makeLabel(parent, labelText);

		Text textBox = toolkit.createText(parent, "", style);
		textBox.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		return textBox;
	}

	private Button makeButton(Composite parent, String label) {
		Button button = toolkit.createButton(parent, label, SWT.PUSH);
		button.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		return button;
	}

	private Composite makeSectionAndComposite(Composite parent, String sectionName, int numColumns) {
		final Section section;
		if (StringUtils.isNotEmpty(sectionName)) {
			section = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE);
			section.setText(sectionName);
			section.setExpanded(true);
		} else {
			section = toolkit.createSection(parent, ExpandableComposite.NO_TITLE);
		}

		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite mainComposite = toolkit.createComposite(section, SWT.NONE);
		mainComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(numColumns, false));
		section.setClient(mainComposite);

		return mainComposite;
	}

	/**
	 * Add some empty labels to parent composite (for padding in grid layout)
	 * @param parent
	 * @param num
	 */
	private void addEmptyLabels(Composite parent, int num) {
		while(num-- >0) {
			new Label(parent, SWT.NONE);
		}
	}

	/**
	 * Set horizontal span of the GridLayout for supplied Control widget
	 * @param controlWidget
	 * @param span
	 */
	private void setRowSpan(Control controlWidget, int span) {
		Object layoutData = controlWidget.getLayoutData();
		if (layoutData instanceof GridData) {
			GridData grid = (GridData) layoutData;
			grid.horizontalSpan = span;
		}
	}

	private void setWidthHint(Control controlWidget, int widthHint) {
		Object layoutData = controlWidget.getLayoutData();
		if (layoutData instanceof GridData) {
			GridData grid = (GridData) layoutData;
			grid.widthHint = widthHint;
		}
	}

	/**
	 * Create timing group section part of GUI. The {@link TurboXasTimingGroupTableView} is used for this (based on JFace {@link TableViewer}).
	 * @param parent
	 */
	private void createTimingGroupSection(Composite parent) {
		Composite mainComposite = makeSectionAndComposite(parent, "Timing Groups", 1);
		timingGroupTable = new TurboXasTimingGroupTableView(mainComposite);

		timingGroupTable.setColumnOrderInTable(new TimingGroupParamType[] {TimingGroupParamType.NAME, TimingGroupParamType.NUM_SPECTRA,
			TimingGroupParamType.TIME_PER_SPECTRUM, TimingGroupParamType.TIME_BETWEEN_SPECTRA});

		timingGroupTable.createTable();

		timingGroupTable.setTimingGroups(turboXasParameters);

		addGroupAddRemoveButtons(mainComposite);
	}

	/**
	 * Add controls to Add, remove timing groups from the timing group list.
	 * @param parent
	 */
	private void addGroupAddRemoveButtons(Composite parent) {
		Composite mainComposite = makeSectionAndComposite(parent, "", 4);
		Button addGroupButton = makeButton(mainComposite, "Add timing group");
		addGroupButton.setToolTipText("Add new timing group");

		Button removeGroupButton = makeButton(mainComposite, "Remove timing group");
		removeGroupButton.setToolTipText("Remove timing group(s) currently highlighted in table");

		// Add new timing group to model, update the table
		addGroupButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				turboXasParameters.addTimingGroup(new TurboSlitTimingGroup("New group", 1.5, 1.0, 10));
				timingGroupTable.refresh();
			}
		});

		// Remove timing group from the model, update the table
		removeGroupButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				timingGroupTable.removeSelectedTimingGroupFromModel();
				timingGroupTable.refresh();
			}
		});
	}

	private void addListenersVerifiers() {
		startEnergyTextbox.addVerifyListener(doubleVerifier);
		endEnergyTextbox.addVerifyListener(doubleVerifier);
		energyStepsizeTextbox.addVerifyListener(doubleVerifier);
	}

	private void createSampleNameEnergySections(Composite parent) {
		Composite mainComposite = makeSectionAndComposite(parent, "", 1);

		Composite nameComp = makeSectionAndComposite(mainComposite, "", 4);
		sampleNameTextbox = makeLabelAndTextBox(nameComp, "Sample name");
		setRowSpan(sampleNameTextbox, 3);

		Composite energyComp = makeSectionAndComposite(mainComposite, "Energy", 4);
		startEnergyTextbox = makeLabelAndTextBox(energyComp, "Start energy [eV]");
		endEnergyTextbox = makeLabelAndTextBox(energyComp, "End energy [eV]");
		energyStepsizeTextbox = makeLabelAndTextBox(energyComp, "Energy step size [eV]");

		Composite positionComp = makeSectionAndComposite(mainComposite, "Position", 4);
		startPositionTextbox = makeLabelAndTextBox(positionComp, "Start position", unitStringForPosition);
		endPositionTextbox = makeLabelAndTextBox(positionComp, "End position", unitStringForPosition);
		positionStepsizeTextbox = makeLabelAndTextBox(positionComp, "Position step size", unitStringForPosition);

		positionSection = (Section) positionComp.getParent();
		positionSection.setExpanded(false);

		energySection = (Section) energyComp.getParent();
		energySection.setExpanded(false);

		Composite buttonsComp = makeSectionAndComposite(mainComposite, "", 2);
		createAsciiFileButton = toolkit.createButton(buttonsComp, "Write ascii file", SWT.CHECK);
		createAsciiFileButton.setToolTipText("Create ascii file at end of scan. Relevant data from all detectors will be included");
		createAsciiFileButton.setSelection(false);
		createAsciiFileButton.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		usePositionsForScanButton = toolkit.createButton(buttonsComp, "Use positions for scan", SWT.CHECK);
		usePositionsForScanButton.setToolTipText("Select to have scan parameters set using start, end positions directly rather than positions calculated from the start, end energies");
		usePositionsForScanButton.setSelection(false);
		usePositionsForScanButton.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		usePositionsForScanButton.addListener(SWT.Selection, (event) -> expandPositionEnergySections() );
	}

	private void expandPositionEnergySections() {
		boolean showPositions = usePositionsForScanButton.getSelection();
		positionSection.setExpanded(showPositions);
		energySection.setExpanded(!showPositions);
	}

	private void createExtraScannablesSection(Composite parent) {
		Composite mainComposite = makeSectionAndComposite(parent, "Record extra values", 2);

		makeLabel(mainComposite, "Configure additional values to be recorded during scan    ");
		Button extraScannableButton = toolkit.createButton(mainComposite, "Setup...", SWT.PUSH);
		extraScannableButton.setLayoutData(new GridData(SWT.LEFT, SWT.BEGINNING, false, false));
		extraScannableButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				openExtraScannableDialog(mainComposite);
			}
		});
	}

	private void openExtraScannableDialog(Composite parent) {
		ScannableListEditor scannableListEditor = new ScannableListEditor(parent.getShell());
		scannableListEditor.setScannableInfoFromMap(turboXasParameters.getScannablesToMonitorDuringScan());
		scannableListEditor.setBlockOnOpen(true);
		int retCode = scannableListEditor.open();
		if (retCode == Window.OK) {
			turboXasParameters.setScannablesToMonitorDuringScan( scannableListEditor.getScannableMapFromList() );
		}
	}

	private void createEnergyCalibrationSection(Composite parent) {
		calibrationComposite = new EnergyCalibrationComposite(parent);
		calibrationComposite.setShowPositions(true);
		calibrationComposite.setAfterCalibrationRunnable(this::updateParametersFromGui);
		calibrationComposite.createSection("Energy calibration polynomial");
	}

	private void createRunningAverageSection(Composite parent) {
		Composite mainComposite = makeSectionAndComposite(parent, "Calculate running averages", 2);
		makeLabel(mainComposite, "Select datasets to compute running averages of during scan    ");
		Button setupButton = toolkit.createButton(mainComposite, "Setup...", SWT.PUSH);
		setupButton.addListener(SWT.Selection, event -> showRunningAverageDialog() );
	}

	/**
	 *
	 * @return List of Pairs of 'extra names' for each currently selected detector.
	 * key=detector name, value=data name
	 */
	private List<Pair<String,String>> getDetectorDatasetNames() {
		String[] selectedDetectors = getSelectedDetectorNames();
		List<Pair<String,String>> allDatasetNames = new ArrayList<>();
		for(String detName : selectedDetectors) {
			Scannable detector = Finder.getInstance().find(detectorNamesMap.get(detName));
			if (detector != null) {
				String[] extraNames = detector.getExtraNames();
				for(String datasetName : extraNames) {
					allDatasetNames.add(Pair.create(detName, datasetName));
				}

				// Xspress3 detector has extra FF_sum/I0 calculated by TurboXasNexusTree. This is not
				// part of the detector 'extra names' so add it here to make is available to select as well.
				if (detector instanceof Xspress3) {
					allDatasetNames.add(Pair.create(detName,TurboXasNexusTree.FF_SUM_IO_NAME));
				}
			}
		}
		return allDatasetNames;
	}

	private void showRunningAverageDialog() {
		List<Pair<String,String>> allDatasets = getDetectorDatasetNames();

		// Return if no detectors have been selected
		if (allDatasets.isEmpty()) {
			MessageDialog.openInformation(Display.getDefault().getActiveShell(), "No detectors have been selected",
					"No detectors have been selected for use in the scan - no detector datasets available to select from!");
			return;
		}

		ListSelectionDialog dialog =
				new ListSelectionDialog(Display.getDefault().getActiveShell(), allDatasets,
						new ArrayContentProvider(),
						new LabelProvider() {
							@Override
							public String getText(Object element) {
								if (element == null) {
									return "";
								}
								Pair<String,String> el = (Pair<String,String>)element;
								return el.getFirst()+" : "+el.getSecond();
							}
						},
						"Select datasets to compute running average");

		// Set the initial checkbox selection
		if (namesOfDatasetsToAverage != null && !namesOfDatasetsToAverage.isEmpty()) {
			dialog.setInitialSelections(namesOfDatasetsToAverage.toArray());
		}

		// Update the dataset name list from user selection
		if (dialog.open() == Window.OK) {
			Object[] selection = dialog.getResult();
			if (selection != null) {
				namesOfDatasetsToAverage = new ArrayList<>();
				for(Object sel : selection) {
					logger.info("Selected dataset : {}", sel);
					Pair<String, String> item = (Pair<String, String>) sel;
					namesOfDatasetsToAverage.add(Pair.create(item.getKey(), item.getValue()));
				}
			}
		}
	}

	/**
	 * TurboXas experiment specific implementation of SaveLoadButtons class
	 */
	private class SaveLoadButtonsForTurboXasExperiment extends SaveLoadButtonsComposite {

		public SaveLoadButtonsForTurboXasExperiment(Composite parent, FormToolkit toolkit) {
			super(parent, toolkit);
		}

		@Override
		protected void saveParametersToFile(String filename) throws DeviceException {
			updateParametersFromGui();
			turboXasParameters.saveToFile(filename);
		}

		@Override
		protected void loadParametersFromFile(String filename) throws Exception {
			turboXasParameters = TurboXasParameters.loadFromFile(filename);
			addDefaultExtraScannablesToParameters();
			timingGroupTable.setTimingGroups(turboXasParameters);
			timingGroupTable.refresh();
			updateGuiFromParameters();
		}
	}

	private void createLoadSaveSection(Composite parent) {
		final Composite mainComposite = makeSectionAndComposite(parent, "Load, save settings", 4);

		addShowMotorParametersButton(mainComposite);
		addEmptyLabels(mainComposite, 1);

		new SaveLoadButtonsForTurboXasExperiment(mainComposite, toolkit);

		startScanButton = makeButton(mainComposite, "Start scan");
		startScanButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				updateParametersFromGui();
				TurboXasMotorParameters motorParams = getMotorParameters();
				if (tryToCalculatePositions(motorParams, false)) {
					runScan();
				} else {
					showMotorParameterDialog();
				}
			}
		});
	}

	private void addShowMotorParametersButton(Composite parent) {
		Button showMotorParamButton = makeButton(parent, "Show motor parameters...");
		showMotorParamButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				updateParametersFromGui();
				showMotorParameterDialog();
			}
		});
	}

	private void showMotorParameterDialog() {
		TurboXasMotorParameters motorParams = getMotorParameters();
		if (tryToCalculatePositions(motorParams, true)) {
			TurboXasMotorParameterInfoDialog dialog = new TurboXasMotorParameterInfoDialog(shell);
			dialog.setTurboXasMotorParameters(motorParams);
			dialog.create();
			dialog.open();
		}
	}

	/**
	 * Try to calculate set motor positions and speeds on motorParams object from user specified energies for first timing group.
	 * Catches any IllegalArgumentExceptions thrown by {@link TurboXasMotorParameters#getPositionForEnergy(double)} due to
	 * out of range energies and optionally displays warning dialog.
	 *
	 * @param motorParams
	 * @param showDialog set to true to show warning dialog with error message if energy to position conversion failed.
	 * @return true if parameters could be calculated and positions set correctly, false otherwise
	 */
	private boolean tryToCalculatePositions(TurboXasMotorParameters motorParams, boolean showDialog) {
		try {
			motorParams.setMotorParametersForTimingGroup(0);
			return true;
		}catch(IllegalArgumentException e) {
			if (showDialog) {
				UIHelper.showWarning("Invalid motor parameters", e.getMessage());
			}
			return false;
		}
	}

	/**
	 * Run a scan using the current TurboXasParameters. <p>
	 * The parameters are serialised to an XML string which is then used to
	 * construct a string of Jython commands to setup and run the scan.
	 */
	private void runScan() {
		// Get name of data to be selected by default in the plot view (e.g. lnI0It, FFI0 etc)
		// use last detector (Xspress3 if selected);
		String[] selectedDetectors = turboXasParameters.getDetectors();
		int numDetectors = selectedDetectors.length;
		String lastDetector = selectedDetectors[numDetectors-1];
		String defaultSelectedDataName = defaultPlottedFields.get(lastDetector);
		// Create Jython command string to set the data name :
		String setPlotString = "txasScan.setDataNameToSelectInPlot(\""+defaultSelectedDataName+"\")\n";
		String paramString = turboXasParameters.toXML().replace("\n", " ");

		String imports = "from gda.scan import TurboXasParameters\n";
		String command = "turboXasParams = TurboXasParameters.fromXML(\""+paramString+"\") \n"+
				"txasScan = turboXasParams.createScan() \n" +
				setPlotString +
				"txasScan.runScan()";

		logger.info("Scan run command : {}", imports+command);
		InterfaceProvider.getCommandRunner().runCommand(imports+command);
	}

	/**
	 *
	 * @param string
	 * @return True if string is a single digit and a valid prefix for a number (i.e. -); false otherwise
	 */
	boolean isNumberPrefix(String string) {
		if (string!=null) {
			return (string.length()==1 && string.startsWith("-"));
		} else {
			return false;
		}
	}

	/**
	 * Evaluate string to check if it is a valid number; provides true if string is allowed, false otherwise
	 * (For use in {@link VerifyListener} to set value of doit field of {@link VerifyEvent}).
	 * @param clazz type of number (Double, Integer)
	 * @param string string to be checked
	 * @return
	 */
	private boolean verifyNumber(Class<?> clazz, String string) {
		boolean doit = true;
		if (!StringUtils.isEmpty(string)) {
			try {
				if (clazz == Double.class) {
					// Only one 'e' allowed
					if (StringUtils.countMatches(string, "e")>1) {
						doit = false;
					} else {
						// Split string to check mantissa and exponent separately
						String[] parts = string.split("e");

						// Check mantissa (floating point)...
						if (parts.length>0 && !isNumberPrefix(parts[0])) {
							Double.parseDouble(parts[0]);
						}
						// Check exponent (integer)
						if (parts.length>1 && !isNumberPrefix(parts[1])) {
							Integer.parseInt(parts[1]);
						}
					}
				} else if (clazz == Integer.class) {
					if (!isNumberPrefix(string)) {
						Integer.parseInt(string);
					}
				}
			} catch (NumberFormatException nfe) {
				doit = false;
			}
		}
		return doit;
	}

	private VerifyListener doubleVerifier = new VerifyListener() {
		@Override
		public void verifyText(VerifyEvent e) {
			String currentText = ((Text) e.widget).getText();
			String string = currentText.substring(0, e.start) + e.text + currentText.substring(e.end);
			e.doit = verifyNumber(Double.class, string);
		}
	};

	/**
	 * Update the gui to show the current TurboXasParameters settings.
	 */
	public void updateGuiFromParameters() {
		sampleNameTextbox.setText(turboXasParameters.getSampleName());

		startEnergyTextbox.setText(String.valueOf(turboXasParameters.getStartEnergy()));
		endEnergyTextbox.setText(String.valueOf(turboXasParameters.getEndEnergy()));
		energyStepsizeTextbox.setText(String.valueOf(turboXasParameters.getEnergyStep()));

		startPositionTextbox.setText(String.valueOf(turboXasParameters.getStartPosition()));
		endPositionTextbox.setText(String.valueOf(turboXasParameters.getEndPosition()));
		positionStepsizeTextbox.setText(String.valueOf(turboXasParameters.getPositionStepSize()));
		usePositionsForScanButton.setSelection(turboXasParameters.isUsePositionsForScan());
		expandPositionEnergySections();

		calibrationComposite.setPolynomialString(turboXasParameters.getEnergyCalibrationPolynomial());
		calibrationComposite.setReferenceFileName(turboXasParameters.getEnergyCalibrationReferenceFile());
		calibrationComposite.setCalibrationMinPosition(turboXasParameters.getEnergyCalibrationMinPosition());
		calibrationComposite.setCalibrationMaxPosition(turboXasParameters.getEnergyCalibrationMaxPosition());
		calibrationComposite.setSampleFileName(turboXasParameters.getEnergyCalibrationFile());
		calibrationComposite.updateGuiFromParameters();

		int selectionIndex = motorCombo.indexOf(turboXasParameters.getMotorToMove());
		motorCombo.select(Math.max(selectionIndex, 0));

		useTrajectoryScanButton.setSelection(turboXasParameters.getUseTrajectoryScan());
		useTwoWayScanButton.setSelection(turboXasParameters.isTwoWayScan());

		List<String> selectedDetectors = Arrays.asList(turboXasParameters.getDetectors());
		for(Button box : detectorCheckboxes) {
			boolean selected = selectedDetectors.contains(box.getData());
			box.setSelection(selected);
		}

		// Set tooltip on energy calibration polynomial to shows calibration energy range
		PolynomialFunction polynomial = getMotorParameters().getPositionToEnergyPolynomial();
		if (polynomial != null) {
			double minEnergy = polynomial.value(0);
			double maxEnergy = polynomial.value(1);
			calibrationComposite.getPolynomialTextbox().setToolTipText(String.format("Energy range : %.3f ... %.3f eV", minEnergy, maxEnergy));
		}

		createAsciiFileButton.setSelection(turboXasParameters.getWriteAsciiData());

		namesOfDatasetsToAverage = getPairListOfDatasetsToAverage(turboXasParameters.getNamesOfDatasetsToAverage());

		setScannablePositionsFromModel();
	}

	private double getDoubleFromTextbox(Text textbox) {
		String text = textbox.getText();
		if (StringUtils.isEmpty(text) || isNumberPrefix(text)){
			return 0;
		} else {
			return Double.parseDouble(text);
		}
	}

	/**
	 * Update TurboXasParameters from the current gui settings
	 */
	public void updateParametersFromGui() {
		turboXasParameters.setSampleName(sampleNameTextbox.getText());
		turboXasParameters.setStartEnergy(getDoubleFromTextbox(startEnergyTextbox));
		turboXasParameters.setEndEnergy(getDoubleFromTextbox(endEnergyTextbox));
		turboXasParameters.setEnergyStep(getDoubleFromTextbox(energyStepsizeTextbox));
		turboXasParameters.setStartPosition(getDoubleFromTextbox(startPositionTextbox));
		turboXasParameters.setEndPosition(getDoubleFromTextbox(endPositionTextbox));
		turboXasParameters.setPositionStepSize(getDoubleFromTextbox(positionStepsizeTextbox));
		turboXasParameters.setUsePositionsForScan(usePositionsForScanButton.getSelection());

		turboXasParameters.setEnergyCalibrationPolynomial(calibrationComposite.getPolynomialString());
		turboXasParameters.setEnergyCalibrationMinPosition(calibrationComposite.getCalibrationMinPosition());
		turboXasParameters.setEnergyCalibrationMaxPosition(calibrationComposite.getCalibrationMaxPosition());
		turboXasParameters.setEnergyCalibrationFile(calibrationComposite.getSampleFileName());
		turboXasParameters.setEnergyCalibrationReferenceFile(calibrationComposite.getReferenceFileName());

		turboXasParameters.setUseTrajectoryScan(useTrajectoryScanButton.getSelection());
		turboXasParameters.setTwoWayScan(useTwoWayScanButton.getSelection());
		turboXasParameters.setDetectors(getSelectedDetectors());
		turboXasParameters.setMotorToMove(motorCombo.getText());

		turboXasParameters.setWriteAsciiData(createAsciiFileButton.getSelection());
		turboXasParameters.setNamesOfDatasetsToAverage(getStringListOfDatasetsToAverage(namesOfDatasetsToAverage));

		updateScannablePositionsInModel(null, null);
	}

	private String getNiceNameForDetector(String detectorName) {
		return detectorNamesMap.entrySet()
				.stream()
				.filter(entry -> entry.getValue().equals(detectorName))
				.map(Entry::getKey)
				.findFirst()
				.orElse(detectorName);
	}

	/**
	 * Convert from list of {@code <detector name>/<dataset>} to map with key=nice dataset name, value=list of names of datasets
	 * @param values
	 * @return
	 */
	private List<Pair<String,String>> getPairListOfDatasetsToAverage(List<String> values) {
		if (values == null) {
			return Collections.emptyList();
		}
		List<Pair<String,String>> selectedDatasets = new ArrayList<>();  // key=nice detector name, value=list of datasetnames
		values.forEach(val -> {
			String detector = FilenameUtils.getPathNoEndSeparator(val);
			String dataset = FilenameUtils.getName(val);
			String niceName = getNiceNameForDetector(detector);
			selectedDatasets.add(Pair.create(niceName, dataset));
		});
		return selectedDatasets;
	}

	private List<String> getStringListOfDatasetsToAverage(List<Pair<String,String>> values) {
		if (values == null) {
			return Collections.emptyList();
		}
		List<String> selectedDatasets = new ArrayList<>();  // key=nice detector name, value=list of datasetnames
		values.forEach(val -> {
			String detector = detectorNamesMap.get(val.getKey());
			String dataset = val.getValue();
			selectedDatasets.add(detector+"/"+dataset);
		});
		return selectedDatasets;
	}

	/**
	 * Load TurboXasParameters from value saved in the preference store and update the GUI.
	 */
	private void loadSettingsFromPreferenceStore(){
		String savedParamsXmlString = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(PREFERENCE_STORE_KEY, String.class);
		if (StringUtils.isNotEmpty(savedParamsXmlString)) {
			turboXasParameters = TurboXasParameters.fromXML(savedParamsXmlString);
			timingGroupTable.setTimingGroups(turboXasParameters);
			timingGroupTable.refresh();
			updateGuiFromParameters();
		}
	}

	/**
	 * Add the default extra scannables to the TurboXasParameters bean.
	 */
	private void addDefaultExtraScannablesToParameters() {
		if (defaultExtraScannables == null) {
			return;
		}

		List<String> extraScannables = turboXasParameters.getExtraScannables();
		if (extraScannables == null) {
			turboXasParameters.setExtraScannables(defaultExtraScannables);
		} else {
			// Add default scannables to extraScannable if they aren't already there.
			defaultExtraScannables.stream()
				.filter(name -> !extraScannables.contains(name))
				.forEach(extraScannables::add);
		}
	}

	/**
	 * Save the current TurboXasParameters to preference store.
	 */
	private void saveSettingsToPreferenceStore(){
		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(PREFERENCE_STORE_KEY, turboXasParameters.toXML());
	}

	@Override
	public void dispose() {
		logger.debug("dispose called");
		saveSettingsToPreferenceStore();
		toolkit.dispose();
		scannablePositionsComposite.deleteIObservers();
		InterfaceProvider.getScanDataPointProvider().deleteScanEventObserver(serverObserver);
	}

	@Override
	public void setFocus() {
	}

	public String[] getDetectorNames() {
		return detectorNames;
	}

	/**
	 * Set the list of detector names that can be used during a scan (should be {@link BufferedDetector}s)
	 * @param detectorNames
	 */
	public void setDetectorNames(String[] detectorNames) {
		this.detectorNames = detectorNames;
	}

	public void setDetectorNamesMap(Map<String,String> detectorNamesMap) {
		this.detectorNamesMap = detectorNamesMap;
	}

	public String[] getMotorNames() {
		return motorNames;
	}

	/**
	 * Set names of motors that can be moved during a scan (should be {@lin ContinuouslyScannable})
	 * @param motorNames
	 */
	public void setMotorNames(String[] motorNames) {
		this.motorNames = motorNames;
	}

	public void setDefaultPlottedFields(Map<String, String> defaultPlottedFields) {
		this.defaultPlottedFields = defaultPlottedFields;
	}

	public void setDefaultExtraScannables(List<String> defaultExtraScannables) {
		this.defaultExtraScannables = defaultExtraScannables;
	}
}