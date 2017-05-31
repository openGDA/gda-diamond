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


import org.apache.commons.lang.StringUtils;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.VerifyEvent;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
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
import gda.jython.IJythonServerStatusObserver;
import gda.jython.InterfaceProvider;
import gda.scan.ScanEvent;
import gda.scan.TurboSlitTimingGroup;
import gda.scan.TurboXasMotorParameters;
import gda.scan.TurboXasParameters;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.data.EdeDataStore;
import uk.ac.gda.exafs.experiment.ui.TurboXasTimingGroupTableView.TimingGroupParamType;

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

	private TurboXasTimingGroupTableView timingGroupTable;
	private TurboXasParameters turboXasParameters; // parameters being viewed in gui

	private boolean updatingGuiFromParameters = false;

	private static String PREFERENCE_STORE_KEY = "turboxas_settings_key";

	@Override
	public void createPartControl(final Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());

		final SashForm parentComposite = new SashForm(parent, SWT.VERTICAL);
		parentComposite.SASH_WIDTH = 3;
		try {
			turboXasParameters = new TurboXasParameters();
			createSections(parentComposite);
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);
	}

	final IJythonServerStatusObserver serverObserver = new IJythonServerStatusObserver() {
		@Override
		public void update(Object theObserved, final Object changeCode) {
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					if (changeCode instanceof ScanEvent) {
						//TODO Update to show progress of scan
					}
				}
			});
		}
	};

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
		addListenersVerifiers();

		createTimingGroupSection(form.getBody());
		createLoadSaveSection(form.getBody());
		loadSettingsFromPreferenceStore();
		form.layout();
	}

	private Text makeLabelAndTextBox(Composite parent, String labelText) {
		Label label = toolkit.createLabel(parent, labelText, SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Text textBox = toolkit.createText(parent, "", SWT.BORDER);
		textBox.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		return textBox;
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
		Button addGroupButton = new Button(mainComposite, SWT.PUSH);
		addGroupButton.setText("Add timing group");
		addGroupButton.setToolTipText("Add new timing group");

		Button removeGroupButton = new Button(mainComposite, SWT.PUSH);
		removeGroupButton.setText("Remove timing group");
		removeGroupButton.setToolTipText("Remove timing group currently highlighted in table");

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

		startEnergyTextbox = makeLabelAndTextBox(mainComposite, "Start energy");
		endEnergyTextbox = makeLabelAndTextBox(mainComposite, "End energy");
		energyStepsizeTextbox = makeLabelAndTextBox(mainComposite, "Energy step size");
		addEmptyLabels(mainComposite, 2);

		Composite energyCalPolyComposite = makeSectionAndComposite(parent, "Energy calibration polynomial", 4);
		energyCalibrationPolyTextbox = makeLabelAndTextBox(energyCalPolyComposite, "Energy calibration polynomial");
		setRowSpan(energyCalibrationPolyTextbox, 3);
		energyCalibrationPolyMinPositionTextbox = makeLabelAndTextBox(energyCalPolyComposite, "Min Position");
		energyCalibrationPolyMaxPositionTextbox = makeLabelAndTextBox(energyCalPolyComposite, "Max Position");
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
		Button startScanButton = toolkit.createButton(parent, "Start scan", SWT.PUSH);
		startScanButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		startScanButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				updateParametersFromGui();
				runScan();
			}
		});
		new SaveLoadButtonsForTurboXasExperiment(mainComposite, toolkit);
	}

	/**
	 * Run a scan using the current TurboXasParameters. <p>
	 * The parameters are serialised to an XML string which is then used to
	 * construct a string of Jython commands to setup and run the scan.
	 */
	private void runScan() {
		TurboXasMotorParameters motorParams = turboXasParameters.getMotorParameters();
		motorParams.setMotorParametersForTimingGroup(0);
		String motorParamString = motorParams.toXML().replace("\n", " ");
		String imports = "from gda.scan import TurboXasParameters, TurboXasMotorParameters;\n";
		String command = "turboXasMotorParams = TurboXasMotorParameters.fromXML(\""+motorParamString+"\");\n"+
				"txasScan = TurboXasScan( turbo_xas_slit, turboXasMotorParams, [scaler_for_zebra] );\n" +
				"turboXasMotorParams.toXML();txasScan.runScan()";
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
}