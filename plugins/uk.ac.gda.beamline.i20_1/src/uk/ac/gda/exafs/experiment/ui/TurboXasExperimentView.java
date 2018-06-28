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



import java.io.File;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang.ArrayUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.apache.commons.math3.exception.NoDataException;
import org.apache.commons.math3.exception.NullArgumentException;
import org.dawnsci.ede.EnergyCalibration;
import org.dawnsci.ede.PolynomialParser;
import org.dawnsci.ede.rcp.herebedragons.EnergyCalibrationWizard;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.window.Window;
import org.eclipse.jface.wizard.WizardDialog;
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
import gda.scan.TurboXasParameters;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.calibration.ui.EDECalibrationSection;
import uk.ac.gda.exafs.data.AlignmentParametersModel;
import uk.ac.gda.exafs.data.EdeDataStore;
import uk.ac.gda.exafs.experiment.ui.TurboXasTimingGroupTableView.TimingGroupParamType;
import uk.ac.gda.exafs.ui.composites.ScannableListEditor;

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
	private Text energyCalibrationPolyTextbox;
	private Text energyCalibrationPolyMinPositionTextbox;
	private Text energyCalibrationPolyMaxPositionTextbox;
	private Text energyCalibrationFileTextbox;
	private String lastScanFilename = "";
	private Button createAsciiFileButton;

	private TurboXasTimingGroupTableView timingGroupTable;
	private TurboXasParameters turboXasParameters; // parameters being viewed in gui

	private boolean updatingGuiFromParameters = false;

	private String[] motorNames = new String[]{"turbo_xas_slit"};

	private Combo motorCombo;

	private String[] detectorNames = new String[]{"scaler_for_zebra"};

	private Map<String,String> detectorNamesMap;

	private Button[] detectorCheckboxes;

	private Button useTrajectoryScanButton;

	private Button startScanButton;

	private Shell shell;

	private static String PREFERENCE_STORE_KEY = "turboxas_settings_key";

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
				String nexusFilename = scanEvent.getLatestInformation().getFilename();
				if (!StringUtils.isEmpty(nexusFilename)) {
					lastScanFilename = nexusFilename;
				}
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
		if (!StringUtils.isEmpty(lastScanFilename)) {
			energyCalibrationFileTextbox.setToolTipText("Last scan : " + lastScanFilename);
		}
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
		createHardwareOptionsSection(form.getBody());
		createLoadSaveSection(form.getBody());
		loadSettingsFromPreferenceStore();

		addListenersVerifiers();
		form.layout();
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
		addEmptyLabels(mainComposite, 1);

		addDetectorSelectionControls(mainComposite);
	}

	private String[] getSelectedDetectors() {
		String[] selectedDetectors = new String[]{};
		for(Button detectorCheckbox : detectorCheckboxes) {
			if (detectorCheckbox.getSelection()) {
				selectedDetectors = (String[]) ArrayUtils.add(selectedDetectors, detectorCheckbox.getData());
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
			detectorCheckboxes[i].setSelection(true);
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
		final Section experimentDetailsSection;
		if (StringUtils.isNotEmpty(sectionName)) {
			experimentDetailsSection = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE);
			experimentDetailsSection.setText(sectionName);
			experimentDetailsSection.setExpanded(true);
		} else {
			experimentDetailsSection = toolkit.createSection(parent, ExpandableComposite.NO_TITLE);
		}

		experimentDetailsSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite mainComposite = toolkit.createComposite(experimentDetailsSection, SWT.NONE);
		mainComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(numColumns, false));
		experimentDetailsSection.setClient(mainComposite);

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
		energyCalibrationPolyMinPositionTextbox.addVerifyListener(doubleVerifier);
		energyCalibrationPolyMaxPositionTextbox.addVerifyListener(doubleVerifier);
	}

	private void createSampleNameEnergySections(Composite parent) {
		Composite mainComposite = makeSectionAndComposite(parent, "", 4);

		sampleNameTextbox = makeLabelAndTextBox(mainComposite, "Sample name");
		setRowSpan(sampleNameTextbox, 3);

		startEnergyTextbox = makeLabelAndTextBox(mainComposite, "Start energy [eV]");
		endEnergyTextbox = makeLabelAndTextBox(mainComposite, "End energy [eV]");
		energyStepsizeTextbox = makeLabelAndTextBox(mainComposite, "Energy step size [eV]");

		createAsciiFileButton = toolkit.createButton(mainComposite, "Write ascii file", SWT.CHECK);
		createAsciiFileButton.setToolTipText("Create ascii file at end of scan. Relevant data from all detectors will be included");
		createAsciiFileButton.setSelection(false);
		createAsciiFileButton.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false));

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
		Composite energyCalPolyComposite = makeSectionAndComposite(parent, "Energy calibration polynomial", 4);
		energyCalibrationPolyTextbox = makeLabelAndTextBox(energyCalPolyComposite, "Energy calibration polynomial");
		setRowSpan(energyCalibrationPolyTextbox, 3);
		energyCalibrationPolyMinPositionTextbox = makeLabelAndTextBox(energyCalPolyComposite, "Min Position [mm]");
		energyCalibrationPolyMaxPositionTextbox = makeLabelAndTextBox(energyCalPolyComposite, "Max Position [mm]");

		// Non user editable - set from EnergyCalibrationWizard
		energyCalibrationPolyTextbox.setEditable(false);
		energyCalibrationPolyMinPositionTextbox.setEditable(false);
		energyCalibrationPolyMaxPositionTextbox.setEditable(false);

		energyCalibrationFileTextbox = makeLabelAndTextBox(energyCalPolyComposite, "Energy calibration file", SWT.BORDER | SWT.RIGHT);
		setRowSpan(energyCalibrationFileTextbox, 2);
		// If using long path, then textbox is made very wide and it *doesn't shrink* to fit smaller window.
		// Set widthhint on gridlayout to something small to make it the box small initially, and have normal resize behaviour.
		setWidthHint(energyCalibrationFileTextbox, 100);

		Composite buttonComposite = toolkit.createComposite(energyCalPolyComposite, SWT.NONE);
		buttonComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		buttonComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		Button runCalibrationButton = makeButton(buttonComposite, "Run energy Calibration");
		runCalibrationButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				openEnergyCalibrationDialog(energyCalPolyComposite);
			}
		});
	}

	private void openEnergyCalibrationDialog(final Composite parent) {

		// Get name of reference file from Alignment parameters.
		// Opening the 'Optics' view in Alignment perspective case would normally load settings from preference store
		// Load preferences here, to get element and edge values for reference file in case that view hasn't been opened...
		AlignmentParametersModel.INSTANCE.loadAlignmentParametersFromStore();
		String referenceDataFileName = EDECalibrationSection.getCurrentReferenceDataPath();
		String energyCalPolynomialString = energyCalibrationPolyTextbox.getText();

		// Set name of sample file, use nexus file from last run scan if not set
		String sampleFileName = energyCalibrationFileTextbox.getText();
		if (StringUtils.isEmpty(sampleFileName)) {
			sampleFileName = lastScanFilename; //might be empty/null
		}
		EnergyCalibration calibrationModel = new EnergyCalibration();
		try {
			String message = "";
			if (StringUtils.isEmpty(referenceDataFileName) || !new File(referenceDataFileName).isFile() ) {
				message += "Reference data " + referenceDataFileName + " was not found.\n";
			} else {
				calibrationModel.setRefData(referenceDataFileName);
			}

			if (StringUtils.isEmpty(sampleFileName) || !new File(sampleFileName).isFile() ) {
				message += "Sample data " + sampleFileName + " was not found.\n";
			} else {
				calibrationModel.setSampleData(sampleFileName);
			}

			// Show warning message, but still display calibration tool if data cannot be set automatically
			if (message.length() > 0) {
				UIHelper.showWarning("Unable to set input for energy calibration tool automatically", message);
			}

			// Try to set the initial energy calibration polynomial
			if (!StringUtils.isEmpty(energyCalPolynomialString)) {
				try {
					PolynomialFunction poly = new PolynomialFunction(PolynomialParser.extractCoefficientsFromString(energyCalPolynomialString));
					calibrationModel.getCalibrationDetails().setCalibrationResult(poly);
				} catch(NullArgumentException | NoDataException ex) {
					logger.warn("Problem setting polynomial function from string {}", energyCalPolynomialString);
				}
			}

			WizardDialog wizardDialog = new WizardDialog(parent.getShell(),
					new EnergyCalibrationWizard(calibrationModel)) {
				@Override
				protected void createButtonsForButtonBar(Composite parent) {
					super.createButtonsForButtonBar(parent);
					this.getButton(IDialogConstants.FINISH_ID).setText("Apply Calibration");
					((GridData) this.getButton(IDialogConstants.FINISH_ID).getLayoutData()).widthHint = 200;
					this.getButton(IDialogConstants.FINISH_ID).getParent().layout();
				}
			};

			wizardDialog.setPageSize(1024, 768);
			if (wizardDialog.open() == Window.OK) {
				PolynomialFunction function = calibrationModel.getCalibrationDetails().getCalibrationResult();

				if (calibrationModel.getCalibrationDetails().getCalibrationResult() != null) {
					logger.info("Updating energy calibration polynomial details : function = {}", function.toString());
					turboXasParameters.setEnergyCalibrationPolynomial(function.toString());
					turboXasParameters.setEnergyCalibrationReferenceFile(calibrationModel.getRefData().getFileName());
					turboXasParameters.setEnergyCalibrationFile(calibrationModel.getSampleData().getFileName());
					Dataset positions = calibrationModel.getSampleData().getEnergyNode();
					if (positions != null) {
						double minPos = positions.min().doubleValue();
						double maxPos = positions.max().doubleValue();
						turboXasParameters.setEnergyCalibrationMinPosition(minPos);
						turboXasParameters.setEnergyCalibrationMaxPosition(maxPos);
						logger.info("Calibration polynomial range );range = {} .. {}", minPos, maxPos);
					}

					updateGuiFromParameters();
				}
			}
		} catch (Exception e) {
			logger.error("Unable to perform energy calibration", e);
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
		String paramString = turboXasParameters.toXML().replace("\n", " ");
		String imports = "from gda.scan import TurboXasParameters\n";
		String command = "turboXasParams = TurboXasParameters.fromXML(\""+paramString+"\") \n"+
				"txasScan = turboXasParams.createScan() \n" +
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
		updatingGuiFromParameters = true;
		sampleNameTextbox.setText(turboXasParameters.getSampleName());

		startEnergyTextbox.setText(String.valueOf(turboXasParameters.getStartEnergy()));
		endEnergyTextbox.setText(String.valueOf(turboXasParameters.getEndEnergy()));
		energyStepsizeTextbox.setText(String.valueOf(turboXasParameters.getEnergyStep()));

		energyCalibrationPolyTextbox.setText(turboXasParameters.getEnergyCalibrationPolynomial());
		energyCalibrationPolyMinPositionTextbox.setText(String.valueOf(turboXasParameters.getEnergyCalibrationMinPosition()));
		energyCalibrationPolyMaxPositionTextbox.setText(String.valueOf(turboXasParameters.getEnergyCalibrationMaxPosition()));

		energyCalibrationFileTextbox.setText(turboXasParameters.getEnergyCalibrationFile());
		energyCalibrationFileTextbox.setToolTipText(turboXasParameters.getEnergyCalibrationFile()); // so can see full by by hovering with mouse

		// move cursor to end of text field, so filename can be seen in box (not just the leading directories in the fullpath...)
		energyCalibrationFileTextbox.setSelection(energyCalibrationFileTextbox.getText().length());

		int selectionIndex = motorCombo.indexOf(turboXasParameters.getMotorToMove());
		motorCombo.select(Math.max(selectionIndex, 0));

		useTrajectoryScanButton.setSelection(turboXasParameters.getUseTrajectoryScan());
		List<String> selectedDetectors = Arrays.asList(turboXasParameters.getDetectors());
		for(Button box : detectorCheckboxes) {
			boolean selected = selectedDetectors.contains(box.getData());
			box.setSelection(selected);
		}

		// Set tooltip on energy calibration polynomial to shows calibration energy range
		TurboXasMotorParameters motorParams = getMotorParameters();
		double minEnergy = motorParams.getEnergyForPosition(turboXasParameters.getEnergyCalibrationMinPosition());
		double maxEnergy = motorParams.getEnergyForPosition(turboXasParameters.getEnergyCalibrationMaxPosition());
		energyCalibrationPolyTextbox.setToolTipText(String.format("Energy range : %.5g ... %.5g ev", minEnergy, maxEnergy));

		createAsciiFileButton.setSelection(turboXasParameters.getWriteAsciiData());
		updatingGuiFromParameters = false;
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

		turboXasParameters.setEnergyCalibrationPolynomial(energyCalibrationPolyTextbox.getText());
		turboXasParameters.setEnergyCalibrationMinPosition(getDoubleFromTextbox(energyCalibrationPolyMinPositionTextbox));
		turboXasParameters.setEnergyCalibrationMaxPosition(getDoubleFromTextbox(energyCalibrationPolyMaxPositionTextbox));
		turboXasParameters.setEnergyCalibrationFile(energyCalibrationFileTextbox.getText());

		turboXasParameters.setUseTrajectoryScan(useTrajectoryScanButton.getSelection());
		turboXasParameters.setDetectors(getSelectedDetectors());
		turboXasParameters.setMotorToMove(motorCombo.getText());

		turboXasParameters.setWriteAsciiData(createAsciiFileButton.getSelection());
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
	 * Save the current TurboXasParameters to preference store.
	 */
	private void saveSettingsToPreferenceStore(){
		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(PREFERENCE_STORE_KEY, turboXasParameters.toXML());
	}

	@Override
	public void dispose() {
		logger.debug("dispose called");
		saveSettingsToPreferenceStore();
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
}