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

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import org.dawnsci.ede.DataHelper;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.core.databinding.observable.map.IObservableMap;
import org.eclipse.core.databinding.observable.set.IObservableSet;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableMapLabelProvider;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.window.Window;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.ResourceManager;

import gda.device.detector.frelon.FrelonCcdDetectorData;
import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.ede.data.ClientConfig;
import uk.ac.gda.ede.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumCollectionModel;
import uk.ac.gda.exafs.experiment.ui.TimingGroupsSetupPage.TimingGroupWizardModel;
import uk.ac.gda.exafs.experiment.ui.data.CyclicExperimentModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentDataModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors;
import uk.ac.gda.exafs.experiment.ui.data.TimeIntervalDataModel;
import uk.ac.gda.exafs.experiment.ui.data.TimeResolvedExperimentModel;
import uk.ac.gda.exafs.experiment.ui.data.TimingGroupUIModel;
import uk.ac.gda.exafs.ui.composites.XHControlComposite;
import uk.ac.gda.ui.components.NumberEditorControl;

public class TimingGroupSectionComposite extends ResourceComposite {

	private static Logger logger = LoggerFactory.getLogger(TimingGroupSectionComposite.class);

	private static final int GROUP_TABLE_HEIGHT = 120;
	private static final int GROUP_TABLE_WIDTH = 100;

	private final FormToolkit toolkit;

	private TableViewer groupsTableViewer;

	// This parameter is not needed for now
	// private NumberEditorControl spectrumDelayValueText;

	private NumberEditorControl integrationTimeValueText;
	private NumberEditorControl accumulationReadoutTimeValueText;
	private NumberEditorControl realTimePerSpectrumValueText;
	private NumberEditorControl timePerSpectrumValueText;
	private NumberEditorControl noOfAccumulationValueText;
	private NumberEditorControl delayBeforeFristSpectrumValueText;
	private NumberEditorControl noOfSpectrumValueText;
	private NumberEditorControl startTimeValueText;
	private NumberEditorControl endTimeValueText;
	private NumberEditorControl itTimeControl;
	private NumberEditorControl numberOfSpectraPerSecToPlotText;
	protected Button useExternalTriggerCheckbox;
	private ComboViewer itUnitSelectionCombo;
	private ComboViewer groupUnitSelectionCombo;

	boolean showAccumulationReadoutControls, showRealTimePerSpectrum;

	private final TimeResolvedExperimentModel model;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private final List<Binding> groupBindings = new ArrayList<Binding>();

	private Section groupSection;

	private Button i0NoOfAccumulationCheck;

	private NumberEditorControl i0IntegrationTimeValueText;

	private NumberEditorControl i0NoOfAccumulationValueText;

	private NumberEditorControl iRefIntegrationTimeValueText;

	private NumberEditorControl iRefNoOfAccumulationValueText;

	private Section sectionIRefaccumulationSection;

	private Composite i0NoOfaccumulationsComposite;

	private Button endTimeValueFixedFlag;

	private final Image pin;

	private NumberEditorControl itExpDurationControl;

	private Button useTopupCheckerCheckbox;

	public TimingGroupSectionComposite(Composite parent, int style, FormToolkit toolkit, TimeResolvedExperimentModel model) {
		super(parent, style);
		this.toolkit = toolkit;
		this.model = model;
		pin = ResourceManager.getImageDescriptor(XHControlComposite.class,
				"/icons/lock.png").createImage();

		// Set flags for whether to display Frelon specific textboxes for accumulation readout time and real time per spectra.
		if ( DetectorModel.INSTANCE.getCurrentDetector().getDetectorData() instanceof FrelonCcdDetectorData ) {
			showRealTimePerSpectrum = true;
			showAccumulationReadoutControls = true;
		} else {
			showRealTimePerSpectrum = false;
			showAccumulationReadoutControls = false;
		}

		try {
			setupUI();
			bind();
		} catch (Exception e) {
			logger.error("Unable to create controls", e);
		}
	}

	private void bind() {
		dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(itUnitSelectionCombo),
				BeanProperties.value(TimeResolvedExperimentModel.UNIT_PROP_NAME).observe(model));
		dataBindingCtx.bindValue(
				BeanProperties.value(NumberEditorControl.UNIT_PROP_NAME).observe(itTimeControl),
				BeanProperties.value(TimeResolvedExperimentModel.UNIT_PROP_NAME).observe(model),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((ExperimentUnit) value).getUnitText();
					}
				});

		dataBindingCtx.bindValue(
				BeanProperties.value(NumberEditorControl.UNIT_PROP_NAME).observe(itExpDurationControl),
				BeanProperties.value(TimeResolvedExperimentModel.UNIT_PROP_NAME).observe(model),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((ExperimentUnit) value).getUnitText();
					}
				});

		dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(i0NoOfAccumulationCheck),
				BeanProperties.value(ExperimentDataModel.USE_NO_OF_ACCUMULATIONS_FOR_I0_PROP_NAME).observe(model.getExperimentDataModel()));

		dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(i0NoOfaccumulationsComposite),
				BeanProperties.value(ExperimentDataModel.USE_NO_OF_ACCUMULATIONS_FOR_I0_PROP_NAME).observe(model.getExperimentDataModel()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy());

		dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(sectionIRefaccumulationSection),
				BeanProperties.value(SampleStageMotors.USE_IREF_PROP_NAME).observe(SampleStageMotors.INSTANCE),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus result = super.doSet(observableValue, value);
						boolean useIRef = (boolean) value;
						((GridData) sectionIRefaccumulationSection.getLayoutData()).exclude = !useIRef;
						((GridData) sectionIRefaccumulationSection.getLayoutData()).exclude = !((boolean) value);
						((GridLayout) sectionIRefaccumulationSection.getParent().getLayout()).numColumns = useIRef ? 2 : 1;
						UIHelper.revalidateLayout(sectionIRefaccumulationSection.getParent());
						return result;
					}
				});
	}

	private void setupUI() throws Exception {
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		createI0IRefComposites();

		Section section = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		section.setText("It acquisition settings and Timing groups");
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		section.setClient(sectionComposite);

		createExperimentDetails(sectionComposite);
		createGroupTable(sectionComposite);

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);

		createGroupDetails();

		groupsTableViewer.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				IStructuredSelection structuredSelection = (IStructuredSelection) event.getSelection();
				if (!structuredSelection.isEmpty()) {
					showGroupDetails(groupSection, structuredSelection);
					groupSection.setVisible(true);
					((GridData) groupSection.getLayoutData()).exclude = false;
				} else {
					groupSection.setVisible(false);
					((GridData) groupSection.getLayoutData()).exclude = true;

					// TODO select row in table
					int index = model.getIndexOfSelectedRow();
					selectTimingGroupTableRow( index );
				}
				UIHelper.revalidateLayout(groupSection);
			}
		});
		model.addPropertyChangeListener(unitChangeListener);

		// Update timing group values if accumulation readout time changes.
		DetectorModel.INSTANCE.addPropertyChangeListener(event -> {
			if (event.getPropertyName().equals(TimingGroupUIModel.ACCUMULATION_READOUT_TIME_PROP_NAME)) {
				updateTimingGroupDetails();
			}
		});
	}

	/** Update timing group details widgets with latest values in model.
	 *
	 */
	private void updateTimingGroupDetails() {
		IStructuredSelection structuredSelection = (IStructuredSelection) groupsTableViewer.getSelection();
		if (!structuredSelection.isEmpty()) {
			showGroupDetails(groupSection, structuredSelection);
		}
	}

	public void selectTimingGroupTableRow( int index ) {
		Object element = groupsTableViewer.getElementAt( index );
		if ( element != null ) {
			groupsTableViewer.setSelection(new StructuredSelection( element ),true);
		}
	}


	private void createExperimentDetails(Composite sectionComposite) throws Exception {
		Composite expTimeComposite = new Composite(sectionComposite, SWT.NONE);
		expTimeComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		expTimeComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(7, false));

		Label lbl = toolkit.createLabel(expTimeComposite, "It total time", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);

		itExpDurationControl = new NumberEditorControl(expTimeComposite, SWT.None, model, TimeResolvedExperimentModel.TOTAL_IT_COLLECTION_DURATION_PROP_NAME, false);
		itExpDurationControl.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		itExpDurationControl.setEditable(false);
		itExpDurationControl.setLayoutData(gridData);

		lbl = toolkit.createLabel(expTimeComposite, "Collection time", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		itTimeControl = new NumberEditorControl(expTimeComposite, SWT.None, model, TimeResolvedExperimentModel.IT_COLLECTION_DURATION_PROP_NAME, false);
		itTimeControl.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		itTimeControl.setEditable(false);
		itTimeControl.setLayoutData(gridData);

		gridData = new GridData(SWT.FILL, SWT.CENTER, false, false);
		itUnitSelectionCombo = new ComboViewer(expTimeComposite);
		itUnitSelectionCombo.getControl().setLayoutData(gridData);
		itUnitSelectionCombo.setContentProvider(new ArrayContentProvider());
		itUnitSelectionCombo.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((ExperimentUnit) element).getUnitText();
			}
		});
		itUnitSelectionCombo.setInput(ExperimentUnit.values());

		lbl = toolkit.createLabel(expTimeComposite, "Plot every", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		numberOfSpectraPerSecToPlotText = new NumberEditorControl(expTimeComposite, SWT.None, model, TimeResolvedExperimentModel.NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH_PROP_NAME, false);
		numberOfSpectraPerSecToPlotText.setUnit(UnitSetup.SEC.getText());
		numberOfSpectraPerSecToPlotText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		// TODO Refactor this
		if (model instanceof CyclicExperimentModel) {
			Composite repeatingGroupsComposite = new Composite(sectionComposite, SWT.NONE);
			gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
			gridData.horizontalSpan = 2;
			repeatingGroupsComposite.setLayoutData(gridData);
			repeatingGroupsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

			lbl = toolkit.createLabel(repeatingGroupsComposite, "Number of cycles", SWT.NONE);
			lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			NumberEditorControl repeatingGroupsControl = new NumberEditorControl(repeatingGroupsComposite, SWT.None, model, CyclicExperimentModel.NO_OF_REPEATED_GROUPS_PROP_NAME, false);
			repeatingGroupsControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
			repeatingGroupsControl.setRange(2, Integer.MAX_VALUE);
		}
	}

	private void createGroupDetails() throws Exception {
		GridData gridData;
		// Group details Section
		groupSection = toolkit.createSection(this, SWT.None);
		gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
		groupSection.setLayoutData(gridData);
		final Composite groupSectionComposite = toolkit.createComposite(groupSection, SWT.NONE);
		groupSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		groupSection.setClient(groupSectionComposite);

		// Group parameters Section
		final Composite groupDetailsSectionComposite = toolkit.createComposite(groupSectionComposite, SWT.NONE);
		groupDetailsSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		groupDetailsSectionComposite.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));

		createAccumulationTime(groupDetailsSectionComposite);
		if (showAccumulationReadoutControls) {
			createAccumulationReadoutTime(groupDetailsSectionComposite);
		}
		numberOfAccumulations(groupDetailsSectionComposite);
		createGroupTimeUnits(groupDetailsSectionComposite);
		createTimePerSpectrum(groupDetailsSectionComposite);
		if ( showRealTimePerSpectrum ) {
			// Show corrected (i.e. real) time per spectra the detector can provide.
			createRealTimePerSpectrum(groupDetailsSectionComposite);
		}

		// Group delay and trigger section
		final Composite groupTriggerSectionComposite = toolkit.createComposite(groupSectionComposite, SWT.NONE);
		groupTriggerSectionComposite.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));
		groupTriggerSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		delayBeforeStartOfGroup(groupTriggerSectionComposite);
		createStartTime(groupTriggerSectionComposite);
		createNumberOfSpectra(groupTriggerSectionComposite);
		createEndTime(groupTriggerSectionComposite);

		Composite externalTriggerComposite = toolkit.createComposite(groupTriggerSectionComposite);
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		externalTriggerComposite.setLayoutData(gridData);
		externalTriggerComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		useTopupChecker(externalTriggerComposite);
		useExternalTrigger(externalTriggerComposite);

		Composite sectionSeparator = toolkit.createCompositeSeparator(groupSection);
		toolkit.paintBordersFor(sectionSeparator);
		groupSection.setSeparatorControl(sectionSeparator);
	}

	private void createGroupTimeUnits(Composite parent) {
		Label label = toolkit.createLabel(parent, "Time unit", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		groupUnitSelectionCombo = new ComboViewer(parent);
		groupUnitSelectionCombo.getControl().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		groupUnitSelectionCombo.setContentProvider(new ArrayContentProvider());
		groupUnitSelectionCombo.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((ExperimentUnit) element).getUnitText();
			}
		});
		groupUnitSelectionCombo.setInput(ExperimentUnit.values());
	}

	private void createStartTime(Composite parent) throws Exception {
		Label label = toolkit.createLabel(parent, "Start time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		startTimeValueText = new NumberEditorControl(parent, SWT.None, false);
		startTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void createEndTime(Composite parent) throws Exception {
		Label label = toolkit.createLabel(parent, "End time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		endTimeValueText = new NumberEditorControl(parent, SWT.None, false);
		endTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void createTimePerSpectrum(Composite parent) throws Exception {
		Label label = toolkit.createLabel(parent, "Time per spectrum", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		timePerSpectrumValueText = new NumberEditorControl(parent, SWT.None, false);
		timePerSpectrumValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void createRealTimePerSpectrum(Composite parent) throws Exception {
		Label label = toolkit.createLabel(parent, "Real time per spectrum", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		realTimePerSpectrumValueText = new NumberEditorControl(parent, SWT.None, false);
		realTimePerSpectrumValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		realTimePerSpectrumValueText.setToolTipText("The actual time per spectrum Detector can deliver for your given accumulation parameters");
	}

	private void createNumberOfSpectra(Composite parent) throws Exception {
		Label label = toolkit.createLabel(parent, "No. of spectra", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		noOfSpectrumValueText = new NumberEditorControl(parent, SWT.None, false);
		noOfSpectrumValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void createAccumulationTime(Composite parent) throws Exception {
		Label label = toolkit.createLabel(parent, "Accumulation time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		integrationTimeValueText = new NumberEditorControl(parent, SWT.None, false);
		integrationTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void createAccumulationReadoutTime(Composite parent) throws Exception {
		Label label = toolkit.createLabel(parent, "Accumulation readout time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		accumulationReadoutTimeValueText = new NumberEditorControl(parent, SWT.None, false);
		accumulationReadoutTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void numberOfAccumulations(Composite parent) throws Exception {
		Label label = toolkit.createLabel(parent, "No. of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		noOfAccumulationValueText = new NumberEditorControl(parent, SWT.None, false);
		noOfAccumulationValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void delayBeforeStartOfGroup(Composite parent) throws Exception {
		Label label = toolkit.createLabel(parent, "Delay before start of group", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		delayBeforeFristSpectrumValueText = new NumberEditorControl(parent, SWT.None, false);
		delayBeforeFristSpectrumValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void useExternalTrigger(Composite parent) {
		useExternalTriggerCheckbox = toolkit.createButton(parent, "Use external trigger", SWT.CHECK);
		useExternalTriggerCheckbox.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false));
		useExternalTriggerCheckbox.setEnabled(true);
	}

	private void useTopupChecker(Composite parent) {
		useTopupCheckerCheckbox = toolkit.createButton(parent, "Use topup checker", SWT.CHECK);
		useTopupCheckerCheckbox.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false));
		useTopupCheckerCheckbox.setEnabled(true);
	}

	private void createGroupTable(Composite sectionComposite) {
		GridData gridData;
		// Timing groups
		Composite timmingGroupsComposite = new Composite(sectionComposite, SWT.NONE);
		gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
		gridData.heightHint = GROUP_TABLE_HEIGHT;
		gridData.widthHint = GROUP_TABLE_WIDTH;
		timmingGroupsComposite.setLayoutData(gridData);
		timmingGroupsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		Composite groupsTableComposit = new Composite(timmingGroupsComposite, SWT.NONE);
		gridData = new GridData(SWT.FILL, SWT.FILL, true, true);

		groupsTableComposit.setLayoutData(gridData);
		TableColumnLayout layout = new TableColumnLayout();
		groupsTableComposit.setLayout(layout);
		groupsTableViewer = new TableViewer(groupsTableComposit,  SWT.BORDER | SWT.FLAT);
		groupsTableViewer.getTable().setLayoutData(new GridData());
		groupsTableViewer.getTable().setHeaderVisible(true);

		TableViewerColumn viewerNumberColumn = new TableViewerColumn(groupsTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Name");

		viewerNumberColumn = new TableViewerColumn(groupsTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Start time");

		viewerNumberColumn = new TableViewerColumn(groupsTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("End time");

		viewerNumberColumn = new TableViewerColumn(groupsTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Time per Spectrum");

		viewerNumberColumn = new TableViewerColumn(groupsTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("No. of Spectra");

		ObservableListContentProvider contentProvider =
				new ObservableListContentProvider();
		// Create the label provider including monitoring
		// of the changes of the labels
		IObservableSet knownElements = contentProvider.getKnownElements();

		final IObservableMap names = BeanProperties.value(TimingGroupUIModel.class,
				TimeIntervalDataModel.NAME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap startTimes = BeanProperties.value(TimingGroupUIModel.class,
				TimeIntervalDataModel.START_TIME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap endTimes = BeanProperties.value(TimingGroupUIModel.class,
				TimeIntervalDataModel.END_TIME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap timePerSpectrum = BeanProperties.value(TimingGroupUIModel.class,
				TimingGroupUIModel.TIME_PER_SPECTRUM_PROP_NAME).observeDetail(knownElements);
		final IObservableMap noOfSpectrum = BeanProperties.value(TimingGroupUIModel.class,
				TimingGroupUIModel.NO_OF_SPECTRUM_PROP_NAME).observeDetail(knownElements);
		IObservableMap[] labelMaps = {names, startTimes, endTimes, timePerSpectrum, noOfSpectrum};

		groupsTableViewer.setContentProvider(contentProvider);
		groupsTableViewer.setLabelProvider(new ObservableMapLabelProvider(labelMaps) {
			@Override
			public String getColumnText(Object element, int columnIndex) {
				switch (columnIndex) {
				case 0: return (String) names.get(element);
				case 1: return DataHelper.roundDoubletoStringWithOptionalDigits(model.getUnit().getWorkingUnit().convertFromDefaultUnit((double) startTimes.get(element))) + " " + model.getUnit().getWorkingUnit().getUnitText();
				case 2: return DataHelper.roundDoubletoStringWithOptionalDigits(model.getUnit().getWorkingUnit().convertFromDefaultUnit((double) endTimes.get(element))) + " " + model.getUnit().getWorkingUnit().getUnitText();
				case 3: return DataHelper.roundDoubletoStringWithOptionalDigits(model.getUnit().getWorkingUnit().convertFromDefaultUnit((double) timePerSpectrum.get(element))) + " " + model.getUnit().getWorkingUnit().getUnitText();
				case 4: return Integer.toString((int) noOfSpectrum.get(element));
				default : return "Unkown column";
				}
			}
		});
		groupsTableViewer.setInput(model.getGroupList());
		// TODO Select item at top of table
		//groupsTableViewer.setSelection(new StructuredSelection(groupsTableViewer.getElementAt(0)),true);

		Composite buttonComposit = new Composite(timmingGroupsComposite, SWT.NONE);
		buttonComposit.setLayout(new GridLayout());
		buttonComposit.setLayoutData(new GridData(GridData.VERTICAL_ALIGN_FILL));
		final Button butAdd = new Button(buttonComposit, SWT.FLAT);
		butAdd.setText("Setup");
		butAdd.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		butAdd.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				// model.addGroup();
				WizardDialog wizardDialog = new WizardDialog(TimingGroupSectionComposite.this.getShell(),
						new TimingGroupsSetupWizard());
				if (wizardDialog.open() == Window.OK) {
					TimingGroupWizardModel groupModel = ((TimingGroupsSetupPage) wizardDialog.getCurrentPage()).getTimingGroupWizardModel();
					if (groupModel.getItTime() > 0) {
						model.setupExperiment(groupModel.getUnit(), groupModel.getItTime(), groupModel.getNoOfGroups());
						selectTimingGroupTableRow( 0 );
					}
				}
			}
		});
		final Button butExternalTrigger = new Button(buttonComposit, SWT.FLAT);
		butExternalTrigger.setText("TFG");
		butExternalTrigger.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		butExternalTrigger.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				model.updateCollectionDuration(); // Make sure total number of spectra in data collection is consistent with group settings
				WizardDialog wizardDialog = new WizardDialog(TimingGroupSectionComposite.this.getShell(),
						new ExternalTriggerDetailsWizard(model.getExternalTriggerSetting()));
				wizardDialog.setPageSize(1024, 768);
				wizardDialog.open();
			}
		});
	}

	private void createI0IRefComposites() throws Exception {
		// I0 and IRef accumulation times
		Composite composite = toolkit.createComposite(this);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));

		// I0
		Section i0AcquisitionSection = toolkit.createSection(composite, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		i0AcquisitionSection.setText("I0 acquisition settings");
		i0AcquisitionSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		final Composite i0AcquisitionSectionComposite = toolkit.createComposite(i0AcquisitionSection, SWT.NONE);
		i0AcquisitionSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		i0AcquisitionSection.setClient(i0AcquisitionSectionComposite);

		i0NoOfAccumulationCheck = toolkit.createButton(i0AcquisitionSectionComposite, "Set I0 number of accumulations", SWT.CHECK);
		GridData gridData = new GridData(SWT.LEFT, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		i0NoOfAccumulationCheck.setLayoutData(gridData);

		Label label = toolkit.createLabel(i0AcquisitionSectionComposite, "Accumulation time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		i0IntegrationTimeValueText = new NumberEditorControl(i0AcquisitionSectionComposite, SWT.None, model.getExperimentDataModel(), ExperimentDataModel.I0_INTEGRATION_TIME_PROP_NAME, false);
		i0IntegrationTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		i0IntegrationTimeValueText.setUnit(model.getUnit().getWorkingUnit().getUnitText());
		i0IntegrationTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);

		i0NoOfaccumulationsComposite = toolkit.createComposite(i0AcquisitionSectionComposite);
		i0NoOfaccumulationsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		i0NoOfaccumulationsComposite.setLayoutData(gridData);

		label = toolkit.createLabel(i0NoOfaccumulationsComposite, "No. of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		i0NoOfAccumulationValueText = new NumberEditorControl(i0NoOfaccumulationsComposite, SWT.None, model.getExperimentDataModel(), ExperimentDataModel.I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME, false);
		i0NoOfAccumulationValueText.setRange(1, SingleSpectrumCollectionModel.MAX_NO_OF_ACCUMULATIONS);
		i0NoOfAccumulationValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite sectionSeparator = toolkit.createCompositeSeparator(i0AcquisitionSection);
		toolkit.paintBordersFor(sectionSeparator);
		i0AcquisitionSection.setSeparatorControl(sectionSeparator);

		// IRef
		sectionIRefaccumulationSection = toolkit.createSection(composite, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		sectionIRefaccumulationSection.setText("IRef acquisition settings");
		sectionIRefaccumulationSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		final Composite iRefDetailsComposite = toolkit.createComposite(sectionIRefaccumulationSection, SWT.NONE);
		iRefDetailsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		sectionIRefaccumulationSection.setClient(iRefDetailsComposite);

		label = toolkit.createLabel(iRefDetailsComposite, "Accumulation time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		iRefIntegrationTimeValueText = new NumberEditorControl(iRefDetailsComposite, SWT.None, model.getExperimentDataModel(), ExperimentDataModel.IREF_INTEGRATION_TIME_PROP_NAME, false);
		iRefIntegrationTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		iRefIntegrationTimeValueText.setUnit(model.getUnit().getWorkingUnit().getUnitText());

		label = toolkit.createLabel(iRefDetailsComposite, "No. of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		iRefNoOfAccumulationValueText = new NumberEditorControl(iRefDetailsComposite, SWT.None, model.getExperimentDataModel(), ExperimentDataModel.IREF_NO_OF_ACCUMULATION_PROP_NAME, false);
		iRefNoOfAccumulationValueText.setRange(1, SingleSpectrumCollectionModel.MAX_NO_OF_ACCUMULATIONS);
		iRefNoOfAccumulationValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		sectionSeparator = toolkit.createCompositeSeparator(sectionIRefaccumulationSection);
		toolkit.paintBordersFor(sectionSeparator);
		sectionIRefaccumulationSection.setSeparatorControl(sectionSeparator);
	}

	private final PropertyChangeListener unitChangeListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals(TimeResolvedExperimentModel.UNIT_PROP_NAME)) {
				updateTimingGroupDetails();
			}
		}
	};

	public TableViewer getGroupsTableViewer() {
		return groupsTableViewer;
	}

	// This is for label
	private static class ModelToTargetConverter implements IConverter {
		private final TimingGroupUIModel group;
		public ModelToTargetConverter(TimingGroupUIModel group) {
			this.group = group;
		}
		@Override
		public Object convert(Object fromObject) {
			return group.getUnit().convertFromDefaultUnit((double) fromObject);
		}
		@Override
		public Object getFromType() {
			return double.class;
		}
		@Override
		public Object getToType() {
			return double.class;
		}
	}

	// This is for editor
	private static class TargetToModelConverter implements IConverter {
		private final TimingGroupUIModel group;
		public TargetToModelConverter(TimingGroupUIModel group) {
			this.group = group;
		}
		@Override
		public Object convert(Object fromObject) {
			return Double.toString(group.getUnit().convertToDefaultUnit(Double.parseDouble((String) fromObject)));
		}
		@Override
		public Object getFromType() {
			return String.class;
		}
		@Override
		public Object getToType() {
			return String.class;
		}
	}

	private void showGroupDetails(final Section groupSection, IStructuredSelection structuredSelection) {
		TimingGroupUIModel group = (TimingGroupUIModel) structuredSelection.getFirstElement();
		groupSection.setText(group.getName());
		ModelToTargetConverter modelToTargetConverter = new ModelToTargetConverter(group);
		TargetToModelConverter targetToModelConverter = new TargetToModelConverter(group);
		UpdateValueStrategy unitConverter = new UpdateValueStrategy() {

			@Override
			public Object convert(Object value) {
				return ((ExperimentUnit) value).getUnitText();
			}

		};
		try {
			for(Binding binding : groupBindings) {
				if (binding != null && !binding.isDisposed()) {
					dataBindingCtx.removeBinding(binding);
					binding.dispose();
				}
			}
			groupBindings.clear();
			groupBindings.add(dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(groupUnitSelectionCombo),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group)));

			startTimeValueText.setModel(group, TimeIntervalDataModel.START_TIME_PROP_NAME);
			startTimeValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			startTimeValueText.setEditable(false);
			startTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(startTimeValueText),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

//			groupBindings.add(dataBindingCtx.bindValue(
//					WidgetProperties.selection().observe(endTimeValueFixedFlag),
//					BeanProperties.value(TimingGroupUIModel.END_TIME_IS_LOCKED).observe(group)));

			endTimeValueText.setModel(group, TimeIntervalDataModel.END_TIME_PROP_NAME);
			endTimeValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			//			endTimeValueText.setEditable(false);
			endTimeValueText.setValidators(null, group.getEndTimeValidator());
			endTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(endTimeValueText),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			timePerSpectrumValueText.setModel(group, TimingGroupUIModel.TIME_PER_SPECTRUM_PROP_NAME);
			timePerSpectrumValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			timePerSpectrumValueText.setValidators(null, group.getTimePerSpectrumValidator());
			timePerSpectrumValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(timePerSpectrumValueText),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			if ( showRealTimePerSpectrum ) {
				realTimePerSpectrumValueText.setModel(group, TimingGroupUIModel.REAL_TIME_PER_SPECTRUM_PROP_NAME);
				realTimePerSpectrumValueText.setConverters(modelToTargetConverter, targetToModelConverter);
				realTimePerSpectrumValueText.setEditable(false);
				realTimePerSpectrumValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
				groupBindings.add(dataBindingCtx.bindValue(
						BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(realTimePerSpectrumValueText),
						BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
						new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
						unitConverter));
			}

			noOfSpectrumValueText.setModel(group, TimingGroupUIModel.NO_OF_SPECTRUM_PROP_NAME);
			noOfSpectrumValueText.setValidators(null, group.getNoOfSpectrumValidator());

			integrationTimeValueText.setModel(group, TimingGroupUIModel.INTEGRATION_TIME_PROP_NAME);
			integrationTimeValueText.setConverters(new IConverter() {
				private final ExperimentUnit unitForTextbox = DetectorModel.INSTANCE.getUnitForAccumulationTime();

				@Override
				public Object getFromType() {
					return double.class;
				}
				@Override
				public Object getToType() {
					return double.class;
				}
				@Override
				public Object convert(Object fromObject) {
					return unitForTextbox.convertFromDefaultUnit((double) fromObject);
				}
			}, new IConverter() {
				private final ExperimentUnit unitForTextbox = DetectorModel.INSTANCE.getUnitForAccumulationTime();

				@Override
				public Object getFromType() {
					return String.class;
				}
				@Override
				public Object getToType() {
					return String.class;
				}
				@Override
				public Object convert(Object fromObject) {
					return Double.toString(unitForTextbox.convertToDefaultUnit(Double.parseDouble((String) fromObject)));
				}
			});
			integrationTimeValueText.setUnit(DetectorModel.INSTANCE.getUnitForAccumulationTime().getUnitText());
			integrationTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);

			if ( showAccumulationReadoutControls ) {
				accumulationReadoutTimeValueText.setModel(group, TimingGroupUIModel.ACCUMULATION_READOUT_TIME_PROP_NAME);
				accumulationReadoutTimeValueText.setEditable(false);
				accumulationReadoutTimeValueText.setConverters(new IConverter() {
					@Override
					public Object getFromType() {
						return double.class;
					}
					@Override
					public Object getToType() {
						return double.class;
					}
					@Override
					public Object convert(Object fromObject) {
						return ExperimentUnit.MILLI_SEC.convertFromDefaultUnit((double) fromObject);
					}
				}, new IConverter() {
					@Override
					public Object getFromType() {
						return String.class;
					}
					@Override
					public Object getToType() {
						return String.class;
					}
					@Override
					public Object convert(Object fromObject) {
						return Double.toString(ExperimentUnit.MILLI_SEC.convertToDefaultUnit(Double.parseDouble((String) fromObject)));
					}
				});
				accumulationReadoutTimeValueText.setUnit(ClientConfig.UnitSetup.MILLI_SEC.getText());
				accumulationReadoutTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			}

			noOfAccumulationValueText.setModel(group, TimingGroupUIModel.NO_OF_ACCUMULATION_PROP_NAME);
			noOfAccumulationValueText.setEditable(false);
			noOfAccumulationValueText.setConverters(new IConverter() {

				@Override
				public Object getToType() {
					return int.class;
				}

				@Override
				public Object getFromType() {
					return int.class;
				}

				@Override
				public Object convert(Object fromObject) {
					int noOfAccu = ((Integer) fromObject).intValue();
					if (noOfAccu == TimingGroupUIModel.INVALID_NO_OF_ACCUMULATION) {
						UIHelper.showWarning("Detector error", "Unable to get number of accumulations with current parameters");
					}
					return fromObject;
				}
			}, null);

			delayBeforeFristSpectrumValueText.setModel(group, TimeIntervalDataModel.DELAY_PROP_NAME);
			delayBeforeFristSpectrumValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			delayBeforeFristSpectrumValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			delayBeforeFristSpectrumValueText.setUnit(group.getUnit().getWorkingUnit().getUnitText());
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(delayBeforeFristSpectrumValueText),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			groupBindings.add(dataBindingCtx.bindValue(WidgetProperties.enabled().observe(useExternalTriggerCheckbox),
					BeanProperties.value(TimingGroupUIModel.EXTERNAL_TRIGGER_AVAILABLE_PROP_NAME).observe(group)));

			groupBindings.add(dataBindingCtx.bindValue(WidgetProperties.selection().observe(useExternalTriggerCheckbox),
					BeanProperties.value(TimingGroupUIModel.USE_EXTERNAL_TRIGGER_PROP_NAME).observe(group)));

			groupBindings.add(dataBindingCtx.bindValue(WidgetProperties.selection().observe(useTopupCheckerCheckbox),
					BeanProperties.value(TimingGroupUIModel.USE_TOPUP_CHECKER_PROP_NAME).observe(group)));

			// Only allow 'use topupchecker' to be switched on/off for *first* timing group
			if ( group.getName().endsWith("0") ) {
				useTopupCheckerCheckbox.setEnabled( true );
			} else {
				useTopupCheckerCheckbox.setEnabled( false );
			}

		} catch (Exception e) {
			logger.error("Unable to setup group detail controls", e);
		}
	}

	@Override
	protected void disposeResource() {
		model.removePropertyChangeListener(unitChangeListener);
		pin.dispose();
	}


	public void setUserControlsEnabled(boolean enabled) {
		NumberEditorControl[] controlsToEnableDisableDuringScan = {startTimeValueText, endTimeValueText,timePerSpectrumValueText,
				noOfSpectrumValueText, integrationTimeValueText, accumulationReadoutTimeValueText, delayBeforeFristSpectrumValueText};

		if (groupUnitSelectionCombo!=null) {
			groupUnitSelectionCombo.getControl().setEnabled(enabled);
		}

		for(NumberEditorControl control : controlsToEnableDisableDuringScan) {
			if (control!=null) {
				control.setEditable(enabled);
			}
		}
	}

}
