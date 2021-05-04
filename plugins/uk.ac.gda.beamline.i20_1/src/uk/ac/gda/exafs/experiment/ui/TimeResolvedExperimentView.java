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


import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
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
import gda.scan.ede.TimeResolvedExperimentParameters;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.alignment.ui.SampleStageMotorsComposite;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentDataModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;
import uk.ac.gda.exafs.experiment.ui.data.TimeResolvedExperimentModel;
import uk.ac.gda.exafs.ui.composites.ScannableListEditor;

public class TimeResolvedExperimentView extends ViewPart {

	public static final String LINEAR_EXPERIMENT_VIEW_ID = "uk.ac.gda.exafs.ui.views.linearExperimentView";

	private static Logger logger = LoggerFactory.getLogger(TimeResolvedExperimentView.class);

	protected FormToolkit toolkit;
	private DataBindingContext dataBindingCtx;

	protected Button useExternalTriggerCheckbox;

	private Button useFastShutterCheckbox;

	private Button generateAsciiDataCheckbox;

	private Button setupScannableButton;

	private ScannableListEditor scannableListEditor;

	private Text sampleDescText;

	private Text suffixText;

	private SampleStageMotorsComposite sampleMotorsComposite;

	private TimingGroupSectionComposite timingGroupSectionComposite;

	private boolean hideTimeBar = true;

	@Override
	public void createPartControl(final Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		dataBindingCtx = new DataBindingContext();
		final SashForm parentComposite = new SashForm(parent, SWT.VERTICAL);
		parentComposite.SASH_WIDTH = 7;
		try {
			createSections(parentComposite);
			bind();
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);
	}

	protected void createSections(final SashForm parentComposite) {
		createExperimentPropertiesComposite(parentComposite);
		createStartStopScanSection(parentComposite);
		int[] weights = new int[] {8, 1};
		parentComposite.setWeights(weights);
	}

	protected TimeResolvedExperimentModel getModel() {
		return ExperimentModelHolder.INSTANCE.getLinerExperimentModel();
	}

	private void bind() {
		// Select first item in timing group table
		timingGroupSectionComposite.selectTimingGroupTableRow(0);

		dataBindingCtx.bindValue(WidgetProperties.selection().observe(useFastShutterCheckbox),
				BeanProperties.value(ExperimentDataModel.USE_FAST_SHUTTER_PROP_NAME).observe(getModel().getExperimentDataModel()) );

		dataBindingCtx.bindValue(WidgetProperties.selection().observe(generateAsciiDataCheckbox),
				BeanProperties.value(TimeResolvedExperimentModel.GENERATE_ASCII_DATA).observe(getModel()) );
	}

	protected void createExperimentPropertiesComposite(Composite parent) {
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1,false));
		ScrolledForm scrolledform = toolkit.createScrolledForm(composite);
		scrolledform.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Form form = scrolledform.getForm();
		// Moved to single column
		form.getBody().setLayout(new GridLayout(1, true));
		toolkit.decorateFormHeading(form);
		scrolledform.setText("Time-resolved studies");
		createExperimentDetailsSection(form.getBody());
		createGroupSection(form.getBody());
		createCalibrationSection(form.getBody());
		form.layout();
	}

	private SingleSpectrumCollectionWidgets singleSpectrumWidgets;
	private void createCalibrationSection(Composite parent) {
		singleSpectrumWidgets = new SingleSpectrumCollectionWidgets();
		singleSpectrumWidgets.setToolkit(toolkit);
		singleSpectrumWidgets.createEnergyCalibrationSection(parent);
	}

	protected void createStartStopScanSection(Composite parent) {
		final Section startStopScanSection = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR);
		startStopScanSection.setText("Scan run controls and settings");
		startStopScanSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite startStopSectionComposite = toolkit.createComposite(startStopScanSection, SWT.NONE);

		startStopSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		startStopScanSection.setClient(startStopSectionComposite);

		addStartStopButtons(startStopSectionComposite);
		addLoadSaveButtons(startStopSectionComposite);
	}

	/**
	 * Add buttons to start and stop a scan.
	 * @param parent
	 */
	private void addStartStopButtons(final Composite parent) {
		Button startScanButton = toolkit.createButton(parent, "Start scan", SWT.PUSH);
		startScanButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		startScanButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					getModel().doCollection(suffixText.getText(), sampleDescText.getText());
				} catch (Exception e) {
					UIHelper.showError("Unable to scan", e.getMessage());
				}
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startScanButton),
				BeanProperties.value(TimeResolvedExperimentModel.SCANNING_PROP_NAME).observe(getModel()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return (!(boolean) value);
					}
				});

		Button stopScanButton = toolkit.createButton(parent, "Stop scan", SWT.PUSH);
		stopScanButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(stopScanButton),
				BeanProperties.value(TimeResolvedExperimentModel.SCANNING_PROP_NAME).observe(getModel()));
		stopScanButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				getModel().doStop();
			}
		});
	}

	/**
	 * Linear experiment specific implementation of SaveLoadButtons class
	 * ('get' and 'set' parameters from/to gui)
	 */
	private class SaveLoadButtonsForLinearExperiment extends SaveLoadButtonsComposite {

		public SaveLoadButtonsForLinearExperiment(Composite parent, FormToolkit toolkit) {
			super(parent, toolkit);
		}

		@Override
		protected void saveParametersToFile(String filename) throws DeviceException {
			TimeResolvedExperimentParameters params = getModel().getParametersBeanFromCurrentSettings();
			params.saveToFile(filename);
		}

		@Override
		protected void loadParametersFromFile(String filename) throws Exception {
			if (!beanIsCorrectType(filename, TimeResolvedExperimentParameters.class)) {
				return;
			}
			TimeResolvedExperimentParameters params = TimeResolvedExperimentParameters.loadFromFile(filename);
			SingleSpectrumCollectionWidgets.updateCalibrationDetails(params);
			getModel().setupFromParametersBean(params);
		}
	}

	/**
	 * Add buttons to :
	 * <li>Save current scan settings in gui to an xml file</li>
	 * <li>Load settings from xml and update the gui</li>
	 * @param parent parent composite
	 * @since 7/4/2017
	 */
	private void addLoadSaveButtons(final Composite parent) {
		SaveLoadButtonsForLinearExperiment saveLoadButtonsComposite = new SaveLoadButtonsForLinearExperiment(parent, toolkit);
	}

	private void createExperimentDetailsSection(Composite parent) {
		SampleDetailsSection sampleDetailComp = new SampleDetailsSection(parent, toolkit);
		sampleDetailComp.bindWidgetsToModel(getModel().getExperimentDataModel());

		suffixText = sampleDetailComp.getSuffixTextbox();
		sampleDescText = sampleDetailComp.getSampleDescriptionTextbox();

		Composite checkboxComposite = toolkit.createComposite(sampleDetailComp.getMainComposite(), SWT.NONE);
		checkboxComposite.setLayout(new GridLayout(2, false));
		checkboxComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		generateAsciiDataCheckbox = toolkit.createButton(checkboxComposite, "Generate Ascii files", SWT.CHECK);
		generateAsciiDataCheckbox.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false));

		useFastShutterCheckbox = toolkit.createButton(checkboxComposite, "Use fast shutter", SWT.CHECK);
		useFastShutterCheckbox.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false));

		setupScannableButton = toolkit.createButton(sampleDetailComp.getMainComposite(), "Setup scannables/PVs to monitor", SWT.PUSH);
		setupScannableButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		scannableListEditor = new ScannableListEditor(parent.getShell());

		setupScannableButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				scannableListEditor.setScannableInfoFromMap(getModel().getExperimentDataModel().getScannablesToMonitor());
				scannableListEditor.open();
				if (scannableListEditor.getReturnCode() == Window.OK) {
					getModel().getExperimentDataModel().setScannablesToMonitor(scannableListEditor.getScannableMapFromList());
				}
			}
		});

		//Sample stage motors
		sampleMotorsComposite = new SampleStageMotorsComposite(parent, SWT.None, toolkit, true);
	}

	final IJythonServerStatusObserver serverObserver = new IJythonServerStatusObserver() {
		@Override
		public void update(Object theObserved, final Object changeCode) {
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					if (changeCode instanceof ScanEvent) {
						updateStartStopButtons((ScanEvent)changeCode);
					}
				}
			});
		}
	};

	private void updateStartStopButtons(ScanEvent changeCode) {
		switch (changeCode.getLatestStatus()) {
		case COMPLETED_AFTER_FAILURE:
		case COMPLETED_AFTER_STOP:
		case COMPLETED_EARLY:
		case NOTSTARTED:
		case FINISHING_EARLY:
		case TIDYING_UP_AFTER_FAILURE:
		case TIDYING_UP_AFTER_STOP:
		case COMPLETED_OKAY:
			getModel().setScanning(false);
			timingGroupSectionComposite.setUserControlsEnabled(true);
			break;
		case PAUSED:
		case RUNNING:
			getModel().setScanning(true);
			timingGroupSectionComposite.setUserControlsEnabled(false);
			break;
		default:
			getModel().setScanning(false);
			timingGroupSectionComposite.setUserControlsEnabled(true);
			break;
		}
	}

	private void createGroupSection(Composite parent) {
		timingGroupSectionComposite = new TimingGroupSectionComposite(parent, SWT.None, toolkit, getModel());
		timingGroupSectionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		toolkit.paintBordersFor(timingGroupSectionComposite);
		MenuManager menuManager = new MenuManager();
		Menu menu = menuManager.createContextMenu(timingGroupSectionComposite.getGroupsTableViewer().getTable());
		// Set the MenuManager
		timingGroupSectionComposite.getGroupsTableViewer().getTable().setMenu(menu);
		getSite().registerContextMenu(menuManager, timingGroupSectionComposite.getGroupsTableViewer());
		getSite().setSelectionProvider(timingGroupSectionComposite.getGroupsTableViewer());
	}

	@Override
	public void setFocus() {
	}

	@Override
	public void dispose() {
		sampleMotorsComposite.dispose();
		dataBindingCtx.dispose();
		singleSpectrumWidgets.dispose();
		super.dispose();
	}
}
