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

package uk.ac.gda.exafs.ui.views;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.core.databinding.observable.map.IObservableMap;
import org.eclipse.core.databinding.observable.set.IObservableSet;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableMapLabelProvider;
import org.eclipse.jface.databinding.viewers.ViewerProperties;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.swt.SWT;
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

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentTimingDataModel;
import uk.ac.gda.exafs.ui.data.experiment.TimeResolvedExperimentModel;
import uk.ac.gda.exafs.ui.data.experiment.TimingGroupUIModel;
import uk.ac.gda.ui.components.NumberEditorControl;

public class TimingGroupSectionComposite extends Composite {

	private static Logger logger = LoggerFactory.getLogger(TimingGroupSectionComposite.class);

	private static final int GROUP_TABLE_HEIGHT = 120;
	private static final int GROUP_TABLE_WIDTH = 100;

	private final FormToolkit toolkit;

	private TableViewer groupsTableViewer;
	private NumberEditorControl spectrumDelayValueText;
	private NumberEditorControl integrationTimeValueText;
	private NumberEditorControl timePerSpectrumValueText;
	private NumberEditorControl noOfAccumulationValueText;
	private NumberEditorControl delayBeforeFristSpectrumValueText;
	private NumberEditorControl noOfSpectrumValueText;
	private NumberEditorControl startTimeValueText;
	private NumberEditorControl endTimeValueText;
	private NumberEditorControl experimentTimeControl;
	private NumberEditorControl numberOfSpectraPerSecToPlotText;
	protected Button useExternalTriggerCheckbox;
	private ComboViewer expUnitSelectionCombo;
	private ComboViewer groupUnitSelectionCombo;
	private ComboViewer inputLemoSelector;

	private final TimeResolvedExperimentModel model;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private final List<Binding> groupBindings = new ArrayList<Binding>();

	private Section groupSection;

	public TimingGroupSectionComposite(Composite parent, int style, FormToolkit toolkit, TimeResolvedExperimentModel model) {
		super(parent, style);
		this.toolkit = toolkit;
		this.model = model;
		try {
			setupUI();
			bind();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			logger.error("TODO put description of error here", e);
		}
	}

	private void bind() {
		dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(expUnitSelectionCombo),
				BeanProperties.value(TimeResolvedExperimentModel.UNIT_PROP_NAME).observe(model));
		dataBindingCtx.bindValue(
				BeanProperties.value(NumberEditorControl.UNIT_PROP_NAME).observe(experimentTimeControl),
				BeanProperties.value(TimeResolvedExperimentModel.UNIT_PROP_NAME).observe(model),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((ExperimentTimingDataModel.ExperimentUnit) value).getUnitText();
					}
				});
	}

	private void setupUI() throws Exception {
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		Section section = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		section.setText("Timing groups");
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		section.setClient(sectionComposite);

		Composite expTimeComposite = new Composite(sectionComposite, SWT.NONE);
		expTimeComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		expTimeComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(5, false));

		Label lbl = toolkit.createLabel(expTimeComposite, "Total experiment", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		experimentTimeControl = new NumberEditorControl(expTimeComposite, SWT.None, model, TimeResolvedExperimentModel.EXPERIMENT_DURATION_PROP_NAME, false);
		experimentTimeControl.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		experimentTimeControl.setLayoutData(gridData);

		gridData = new GridData(SWT.FILL, SWT.CENTER, false, false);
		expUnitSelectionCombo = new ComboViewer(expTimeComposite);
		expUnitSelectionCombo.getControl().setLayoutData(gridData);
		expUnitSelectionCombo.setContentProvider(new ArrayContentProvider());
		expUnitSelectionCombo.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((ExperimentTimingDataModel.ExperimentUnit) element).getUnitText();
			}
		});
		expUnitSelectionCombo.setInput(ExperimentTimingDataModel.ExperimentUnit.values());

		lbl = toolkit.createLabel(expTimeComposite, "Time interal to plot", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		numberOfSpectraPerSecToPlotText = new NumberEditorControl(expTimeComposite, SWT.None, model, TimeResolvedExperimentModel.NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH_PROP_NAME, false);
		numberOfSpectraPerSecToPlotText.setUnit(UnitSetup.SEC.getText());
		numberOfSpectraPerSecToPlotText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite regionsComposit = new Composite(sectionComposite, SWT.NONE);
		gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
		gridData.heightHint = GROUP_TABLE_HEIGHT;
		gridData.widthHint = GROUP_TABLE_WIDTH;
		regionsComposit.setLayoutData(gridData);
		regionsComposit.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		Composite groupsTableComposit = new Composite(regionsComposit, SWT.NONE);
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
				ExperimentTimingDataModel.NAME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap startTimes = BeanProperties.value(TimingGroupUIModel.class,
				ExperimentTimingDataModel.START_TIME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap endTimes = BeanProperties.value(TimingGroupUIModel.class,
				ExperimentTimingDataModel.END_TIME_PROP_NAME).observeDetail(knownElements);
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
				case 1: return DataHelper.roundDoubletoStringWithOptionalDigits(model.getUnit().getWorkingUnit().convertFromMilli((double) startTimes.get(element))) + " " + model.getUnit().getWorkingUnit().getUnitText();
				case 2: return DataHelper.roundDoubletoStringWithOptionalDigits(model.getUnit().getWorkingUnit().convertFromMilli((double) endTimes.get(element))) + " " + model.getUnit().getWorkingUnit().getUnitText();
				case 3: return DataHelper.roundDoubletoStringWithOptionalDigits(model.getUnit().getWorkingUnit().convertFromMilli((double) timePerSpectrum.get(element))) + " " + model.getUnit().getWorkingUnit().getUnitText();
				case 4: return Integer.toString((int) noOfSpectrum.get(element));
				default : return "Unkown column";
				}
			}
		});
		groupsTableViewer.setInput(model.getGroupList());

		Composite buttonComposit = new Composite(regionsComposit, SWT.NONE);
		buttonComposit.setLayout(new GridLayout());
		buttonComposit.setLayoutData(new GridData(GridData.VERTICAL_ALIGN_FILL));
		final Button butAdd = new Button(buttonComposit, SWT.FLAT);
		butAdd.setText("Add");
		butAdd.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		butAdd.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				model.addGroup();
			}
		});

		final Button butRemove = new Button(buttonComposit, SWT.FLAT);
		butRemove.setText("Remove");
		butRemove.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		butRemove.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				IStructuredSelection structuredSelection = (IStructuredSelection) groupsTableViewer.getSelection();
				if (structuredSelection.getFirstElement() != null) {
					model.removeGroup((TimingGroupUIModel) structuredSelection.getFirstElement());
				}
			}
		});

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);

		groupSection = toolkit.createSection(this, SWT.None);
		gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
		groupSection.setLayoutData(gridData);
		final Composite groupSectionComposite = toolkit.createComposite(groupSection, SWT.NONE);
		groupSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		groupSection.setClient(groupSectionComposite);

		Label label = toolkit.createLabel(groupSectionComposite, "Time unit", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		groupUnitSelectionCombo = new ComboViewer(groupSectionComposite);
		groupUnitSelectionCombo.getControl().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		groupUnitSelectionCombo.setContentProvider(new ArrayContentProvider());
		groupUnitSelectionCombo.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((ExperimentTimingDataModel.ExperimentUnit) element).getUnitText();
			}
		});
		groupUnitSelectionCombo.setInput(ExperimentTimingDataModel.ExperimentUnit.values());

		label = toolkit.createLabel(groupSectionComposite, "Start time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		startTimeValueText = new NumberEditorControl(groupSectionComposite, SWT.None, false);
		startTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		label = toolkit.createLabel(groupSectionComposite, "End time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		endTimeValueText = new NumberEditorControl(groupSectionComposite, SWT.None, false);
		endTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		label = toolkit.createLabel(groupSectionComposite, "Time per spectrum", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		timePerSpectrumValueText = new NumberEditorControl(groupSectionComposite, SWT.None, false);
		timePerSpectrumValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		label = toolkit.createLabel(groupSectionComposite, "No. of spectra", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		noOfSpectrumValueText = new NumberEditorControl(groupSectionComposite, SWT.None, false);
		noOfSpectrumValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		label = toolkit.createLabel(groupSectionComposite, "Accumulation time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		integrationTimeValueText = new NumberEditorControl(groupSectionComposite, SWT.None, false);
		integrationTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		label = toolkit.createLabel(groupSectionComposite, "No. of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		noOfAccumulationValueText = new NumberEditorControl(groupSectionComposite, SWT.None, false);
		noOfAccumulationValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		label = toolkit.createLabel(groupSectionComposite, "Delay before start of group", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		delayBeforeFristSpectrumValueText = new NumberEditorControl(groupSectionComposite, SWT.None, false);
		delayBeforeFristSpectrumValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		label = toolkit.createLabel(groupSectionComposite, "Delay between spectrum", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		spectrumDelayValueText = new NumberEditorControl(groupSectionComposite, SWT.None, false);
		spectrumDelayValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite externalTriggerComposite = toolkit.createComposite(groupSectionComposite);
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		externalTriggerComposite.setLayoutData(gridData);
		externalTriggerComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(3, false));

		useExternalTriggerCheckbox = toolkit.createButton(externalTriggerComposite, "Use exernal trigger", SWT.CHECK);
		useExternalTriggerCheckbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		label = toolkit.createLabel(externalTriggerComposite, "Trigger input Lemo number");
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		inputLemoSelector = new ComboViewer(externalTriggerComposite);
		inputLemoSelector.getCombo().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		inputLemoSelector.setLabelProvider(new LabelProvider());
		inputLemoSelector.setContentProvider(new ArrayContentProvider());
		inputLemoSelector.setInput(TimingGroup.INPUT_TRIGGER_LEMO_NUMBERS);

		sectionSeparator = toolkit.createCompositeSeparator(groupSection);
		toolkit.paintBordersFor(sectionSeparator);
		groupSection.setSeparatorControl(sectionSeparator);

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
				}
				UIHelper.revalidateLayout(groupSection);
			}
		});
		model.addPropertyChangeListener(unitChangeListener);
	}

	private final PropertyChangeListener unitChangeListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals(TimeResolvedExperimentModel.UNIT_PROP_NAME)) {
				IStructuredSelection structuredSelection = (IStructuredSelection) groupsTableViewer.getSelection();
				if (!structuredSelection.isEmpty()) {
					showGroupDetails(groupSection, structuredSelection);
				}
			}
		}
	};

	public TableViewer getGroupsTableViewer() {
		return groupsTableViewer;
	}


	private static class ModelToTargetConverter implements IConverter {
		private final TimingGroupUIModel group;
		public ModelToTargetConverter(TimingGroupUIModel group) {
			this.group = group;
		}
		@Override
		public Object convert(Object fromObject) {
			return group.getUnit().convertFromMilli((double) fromObject);
		}
		@Override
		public Object getFromType() {
			return double.class;
		}
		@Override
		public Object getToType() {
			return String.class;
		}
	}

	private static class TargetToModelConverter implements IConverter {
		private final TimingGroupUIModel group;
		public TargetToModelConverter(TimingGroupUIModel group) {
			this.group = group;
		}
		@Override
		public Object convert(Object fromObject) {
			return group.getUnit().convertToMilli(Double.parseDouble((String) fromObject));
		}
		@Override
		public Object getFromType() {
			return String.class;
		}
		@Override
		public Object getToType() {
			return double.class;
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
				return ((ExperimentTimingDataModel.ExperimentUnit) value).getUnitText();
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

			startTimeValueText.setModel(group, ExperimentTimingDataModel.START_TIME_PROP_NAME);
			startTimeValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			startTimeValueText.setEditable(false);
			startTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(startTimeValueText),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			endTimeValueText.setModel(group, ExperimentTimingDataModel.END_TIME_PROP_NAME);
			endTimeValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			endTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(endTimeValueText),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			timePerSpectrumValueText.setModel(group, TimingGroupUIModel.TIME_PER_SPECTRUM_PROP_NAME);
			timePerSpectrumValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			timePerSpectrumValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(timePerSpectrumValueText),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));


			noOfSpectrumValueText.setModel(group, TimingGroupUIModel.NO_OF_SPECTRUM_PROP_NAME);

			integrationTimeValueText.setModel(group, TimingGroupUIModel.INTEGRATION_TIME_PROP_NAME);
			integrationTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			integrationTimeValueText.setUnit(ClientConfig.UnitSetup.MILLI_SEC.getText());

			noOfAccumulationValueText.setModel(group, TimingGroupUIModel.NO_OF_ACCUMULATION_PROP_NAME);
			noOfAccumulationValueText.setEditable(false);

			delayBeforeFristSpectrumValueText.setModel(group, ExperimentTimingDataModel.DELAY_PROP_NAME);
			delayBeforeFristSpectrumValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			delayBeforeFristSpectrumValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			delayBeforeFristSpectrumValueText.setUnit(group.getUnit().getWorkingUnit().getUnitText());
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(delayBeforeFristSpectrumValueText),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			spectrumDelayValueText.setModel(group, TimingGroupUIModel.DELAY_BETWEEN_SPECTRUM_PROP_NAME);
			spectrumDelayValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			spectrumDelayValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(spectrumDelayValueText),
					BeanProperties.value(TimingGroupUIModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			groupBindings.add(dataBindingCtx.bindValue(WidgetProperties.enabled().observe(useExternalTriggerCheckbox),
					BeanProperties.value(TimingGroupUIModel.EXTERNAL_TRIGGER_AVAILABLE_PROP_NAME).observe(group)));

			groupBindings.add(dataBindingCtx.bindValue(WidgetProperties.selection().observe(useExternalTriggerCheckbox),
					BeanProperties.value(TimingGroupUIModel.USE_EXTERNAL_TRIGGER_PROP_NAME).observe(group)));

			groupBindings.add(dataBindingCtx.bindValue(WidgetProperties.enabled().observe(inputLemoSelector.getCombo()),
					BeanProperties.value(TimingGroupUIModel.USE_EXTERNAL_TRIGGER_PROP_NAME).observe(group)));

			groupBindings.add(dataBindingCtx.bindValue(ViewerProperties.singleSelection().observe(inputLemoSelector),
					BeanProperties.value(TimingGroupUIModel.EXTERNAL_TRIGGER_INPUT_LEMO_NUMBER_PROP_NAME).observe(group)));
		} catch (Exception e) {
			// TODO Handle this!
			e.printStackTrace();
		}
	}

	@Override
	public void dispose() {
		model.removePropertyChangeListener(unitChangeListener);
		super.dispose();
	}

}
