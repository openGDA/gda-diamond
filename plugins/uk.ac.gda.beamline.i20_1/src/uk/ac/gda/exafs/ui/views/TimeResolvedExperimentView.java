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
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.action.MenuManager;
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
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.ControlListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.Scale;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.beamline.i20_1.utils.TimebarHelper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.SingleSpectrumUIModel;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.CollectionModelRenderer;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentMarkerRenderer;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentTimingDataModel;
import uk.ac.gda.exafs.ui.data.experiment.SpectrumModel;
import uk.ac.gda.exafs.ui.data.experiment.TimeResolvedExperimentModel;
import uk.ac.gda.exafs.ui.data.experiment.TimingGroupModel;
import uk.ac.gda.exafs.ui.data.experiment.TimingGroupsScaleRenderer;
import de.jaret.util.date.Interval;
import de.jaret.util.date.JaretDate;
import de.jaret.util.ui.timebars.TimeBarMarker;
import de.jaret.util.ui.timebars.TimeBarMarkerImpl;
import de.jaret.util.ui.timebars.model.ITimeBarChangeListener;
import de.jaret.util.ui.timebars.model.TimeBarRow;
import de.jaret.util.ui.timebars.swt.TimeBarViewer;

public class TimeResolvedExperimentView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.linearExperimentView";

	private static final int TIMEBAR_ZOOM_FACTOR = 10;

	private static Logger logger = LoggerFactory.getLogger(TimeResolvedExperimentView.class);

	private static final long INITIAL_TIMEBAR_MARKER_IN_MILLI = 10L;

	private static final int GROUP_TABLE_HEIGHT = 120;
	private static final int GROUP_TABLE_WIDTH = 100;

	//	private IPlottingSystem plottingSystem;
	private TimeBarViewer timeBarViewer;
	private FormToolkit toolkit;
	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private TableViewer groupsTableViewer;

	private NumberEditorControl spectrumDelayValueText;
	private NumberEditorControl integrationTimeValueText;
	private NumberEditorControl timePerSpectrumValueText;
	private NumberEditorControl noOfAccumulationValueText;
	private NumberEditorControl delayBeforeFristSpectrumValueText;
	private NumberEditorControl noOfSpectrumValueText;
	private NumberEditorControl startTimeValueText;
	private NumberEditorControl endTimeValueText;

	private TimeBarMarkerImpl marker;

	protected Button useExternalTriggerCheckbox;

	private NumberEditorControl experimentTimeControl;

	private ComboViewer expUnitSelectionCombo;

	private Scale scale;

	private ComboViewer groupUnitSelectionCombo;

	private SampleStageMotorsComposite sampleMotorsComposite;

	@Override
	public void createPartControl(final Composite parent) {
		if (toolkit == null) {
			toolkit = new FormToolkit(parent.getDisplay());
		}
		final SashForm parentComposite = new SashForm(parent, SWT.VERTICAL);
		parentComposite.SASH_WIDTH = 7;

		// TODO Until it is clear how to do, temporary removed the time resolved plot to determine groups

		// SashForm topPartComposite = new SashForm(parentComposite, SWT.HORIZONTAL);
		// topPartComposite.SASH_WIDTH = 7;

		try {
			createExperimentPropertiesComposite(parentComposite);
			// createPlotComposite(topPartComposite);
			createTimeBarComposite(parentComposite);
			bind();
			parentComposite.setWeights(new int[] {3, 1});
			// topPartComposite.setWeights(new int[] {3, 1});
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}

	private void bind() {
		dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(groupsTableViewer),
				ViewersObservables.observeSingleSelection(timeBarViewer),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						if (value != null) {
							timeBarViewer.scrollIntervalToVisible((Interval) value);
						}
						return super.doSet(observableValue, value);
					}
				},
				new UpdateValueStrategy() {
					@Override
					public IStatus validateBeforeSet(Object value) {
						TimingGroupModel object = null;
						if (value instanceof TimingGroupModel) {
							object =  (TimingGroupModel) value;
						} else if (value instanceof SpectrumModel) {
							object = ((SpectrumModel) value).getParent();
						}
						IStructuredSelection structuredSelection = (IStructuredSelection) groupsTableViewer.getSelection();
						if(!structuredSelection.isEmpty()) {
							if (value == null) {
								return Status.CANCEL_STATUS;
							}
							TimingGroupModel viewerObject = (TimingGroupModel) structuredSelection.getFirstElement();
							if (viewerObject.equals(object)) {
								return Status.CANCEL_STATUS;
							}
						}
						return Status.OK_STATUS;
					}

					@Override
					public Object convert(Object value) {
						if (value instanceof TimingGroupModel) {
							return super.convert(value);
						}
						else if (value instanceof SpectrumModel) {
							return super.convert(((SpectrumModel) value).getParent());
						}
						return null;
					}
				});

		dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(expUnitSelectionCombo),
				BeanProperties.value(TimeResolvedExperimentModel.UNIT_PROP_NAME).observe(TimeResolvedExperimentModel.INSTANCE));
		dataBindingCtx.bindValue(
				BeanProperties.value(NumberEditorControl.UNIT_PROP_NAME).observe(experimentTimeControl),
				BeanProperties.value(TimeResolvedExperimentModel.UNIT_PROP_NAME).observe(TimeResolvedExperimentModel.INSTANCE),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((ExperimentTimingDataModel.ExperimentUnit) value).getUnitText();
					}
				});
	}

	private void createExperimentPropertiesComposite(Composite parent) throws Exception {
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
		form.layout();
	}

	private static class ModelToTargetConverter implements IConverter {
		private final TimingGroupModel group;
		public ModelToTargetConverter(TimingGroupModel group) {
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
		private final TimingGroupModel group;
		public TargetToModelConverter(TimingGroupModel group) {
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



	@SuppressWarnings({ "static-access" })
	private void createExperimentDetailsSection(Composite parent) throws Exception {
		// Start stop buttons

		Composite acquisitionButtonsComposite = new Composite(parent, SWT.NONE);
		GridData gridData = new GridData(SWT.FILL, SWT.BEGINNING, true, false);
		gridData.horizontalSpan = 2;
		acquisitionButtonsComposite.setLayoutData(gridData);
		acquisitionButtonsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		toolkit.paintBordersFor(acquisitionButtonsComposite);

		Button startAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Start", SWT.PUSH);
		startAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		startAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					TimeResolvedExperimentModel.INSTANCE.doCollection();
				} catch (Exception e) {
					UIHelper.showError("Unable to scan", e.getMessage());
				}
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startAcquicitionButton),
				BeanProperties.value(TimeResolvedExperimentModel.SCANNING_PROP_NAME).observe(TimeResolvedExperimentModel.INSTANCE),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return (!(boolean) value);
					}
				});

		Button stopAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Stop", SWT.PUSH);
		stopAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(stopAcquicitionButton),
				BeanProperties.value(TimeResolvedExperimentModel.SCANNING_PROP_NAME).observe(TimeResolvedExperimentModel.INSTANCE));
		stopAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				TimeResolvedExperimentModel.INSTANCE.doStop();
			}
		});

		//Sample stage motors

		sampleMotorsComposite = new SampleStageMotorsComposite(parent, SWT.None, toolkit, true);

		// IRef

		final Section irefSection = toolkit.createSection(parent, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		irefSection.setText("Use IRef position");
		irefSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sectionComposite = toolkit.createComposite(irefSection, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		sectionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		irefSection.setClient(sectionComposite);

		final Button useIRefCheckButton = toolkit.createButton(sectionComposite, "Use Iref", SWT.CHECK);
		useIRefCheckButton.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Composite xyPositionComposite = toolkit.createComposite(sectionComposite, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		xyPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xyPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));

		Composite xPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(xPositionComposite);
		xPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		Label xPosLabel = toolkit.createLabel(xPositionComposite, "x", SWT.None);
		xPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final NumberEditorControl xPosition = new NumberEditorControl(xPositionComposite, SWT.None, SingleSpectrumUIModel.INSTANCE, SingleSpectrumUIModel.IREF_X_POSITION_PROP_NAME, false);
		xPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		xPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "y", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final NumberEditorControl yPosition = new NumberEditorControl(yPositionComposite, SWT.None, SingleSpectrumUIModel.INSTANCE, SingleSpectrumUIModel.IREF_Y_POSITION_PROP_NAME, false);
		yPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		yPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		yPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		useIRefCheckButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				xPosition.setEditable(useIRefCheckButton.getSelection());
				yPosition.setEditable(useIRefCheckButton.getSelection());
			}
		});

		xPosition.setEditable(useIRefCheckButton.getSelection());
		yPosition.setEditable(useIRefCheckButton.getSelection());

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(irefSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		irefSection.setSeparatorControl(defaultSectionSeparator);
	}

	private void createGroupSection(Composite parent) throws Exception {
		@SuppressWarnings("static-access")
		Section section = toolkit.createSection(parent, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		section.setText("Timing groups");
		GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
		section.setLayoutData(gridData);
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		section.setClient(sectionComposite);

		Composite expTimeComposite = new Composite(sectionComposite, SWT.NONE);
		expTimeComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		expTimeComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(3, false));

		Label lbl = toolkit.createLabel(expTimeComposite, "Total experiment", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		experimentTimeControl = new NumberEditorControl(expTimeComposite, SWT.None, TimeResolvedExperimentModel.INSTANCE, TimeResolvedExperimentModel.EXPERIMENT_DURATION_PROP_NAME, false);
		experimentTimeControl.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		experimentTimeControl.setLayoutData(gridData);

		gridData = new GridData(SWT.END, SWT.CENTER, false, false);
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

		final IObservableMap names = BeanProperties.value(TimingGroupModel.class,
				ExperimentTimingDataModel.NAME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap startTimes = BeanProperties.value(TimingGroupModel.class,
				ExperimentTimingDataModel.START_TIME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap endTimes = BeanProperties.value(TimingGroupModel.class,
				ExperimentTimingDataModel.END_TIME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap timePerSpectrum = BeanProperties.value(TimingGroupModel.class,
				TimingGroupModel.TIME_PER_SPECTRUM_PROP_NAME).observeDetail(knownElements);
		final IObservableMap noOfSpectrum = BeanProperties.value(TimingGroupModel.class,
				TimingGroupModel.NO_OF_SPECTRUM_PROP_NAME).observeDetail(knownElements);
		IObservableMap[] labelMaps = {names, startTimes, endTimes, timePerSpectrum, noOfSpectrum};

		groupsTableViewer.setContentProvider(contentProvider);
		groupsTableViewer.setLabelProvider(new ObservableMapLabelProvider(labelMaps) {
			@Override
			public String getColumnText(Object element, int columnIndex) {
				switch (columnIndex) {
				case 0: return (String) names.get(element);
				case 1: return DataHelper.roundDoubletoStringWithOptionalDigits(TimeResolvedExperimentModel.INSTANCE.getUnit().getWorkingUnit().convertFromMilli((double) startTimes.get(element))) + " " + TimeResolvedExperimentModel.INSTANCE.getUnit().getWorkingUnit().getUnitText();
				case 2: return DataHelper.roundDoubletoStringWithOptionalDigits(TimeResolvedExperimentModel.INSTANCE.getUnit().getWorkingUnit().convertFromMilli((double) endTimes.get(element))) + " " + TimeResolvedExperimentModel.INSTANCE.getUnit().getWorkingUnit().getUnitText();
				case 3: return DataHelper.roundDoubletoStringWithOptionalDigits(TimeResolvedExperimentModel.INSTANCE.getUnit().getWorkingUnit().convertFromMilli((double) timePerSpectrum.get(element))) + " " + TimeResolvedExperimentModel.INSTANCE.getUnit().getWorkingUnit().getUnitText();
				case 4: return Integer.toString((int) noOfSpectrum.get(element));
				default : return "Unkown column";
				}
			}
		});
		groupsTableViewer.setInput(TimeResolvedExperimentModel.INSTANCE.getGroupList());
		TimeResolvedExperimentModel.INSTANCE.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(TimeResolvedExperimentModel.UNIT_PROP_NAME)) {
					groupsTableViewer.refresh();
					timeBarViewer.redraw();
				}
			}
		});
		Composite buttonComposit = new Composite(regionsComposit, SWT.NONE);
		buttonComposit.setLayout(new GridLayout());
		buttonComposit.setLayoutData(new GridData(GridData.VERTICAL_ALIGN_FILL));
		final Button butAdd = new Button(buttonComposit, SWT.FLAT);
		butAdd.setText("Add");
		butAdd.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		butAdd.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				TimeResolvedExperimentModel.INSTANCE.addGroup();
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
					TimeResolvedExperimentModel.INSTANCE.removeGroup((TimingGroupModel) structuredSelection.getFirstElement());
				}
			}
		});

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);

		final Section groupSection = toolkit.createSection(parent, SWT.None);
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

		useExternalTriggerCheckbox = toolkit.createButton(groupSectionComposite, "Use exernal trigger", SWT.CHECK);
		GridData useExternalTriggerGridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		useExternalTriggerGridData.horizontalSpan = 2;
		useExternalTriggerCheckbox.setLayoutData(useExternalTriggerGridData);

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
				} else {
					groupSection.setVisible(false);
				}
				groupSectionComposite.layout(true, true);
				groupSection.layout(true, true);
				groupSection.getParent().layout(true, true);
			}
		});
		TimeResolvedExperimentModel.INSTANCE.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(TimeResolvedExperimentModel.UNIT_PROP_NAME)) {
					IStructuredSelection structuredSelection = (IStructuredSelection) groupsTableViewer.getSelection();
					if (!structuredSelection.isEmpty()) {
						showGroupDetails(groupSection, structuredSelection);
					}
				}
			}
		});
	}

	// TODO Until it is clear how to do, temporary removed the time resolved plot to determine groups

	//	private void createPlotComposite(Composite parent) {
	//		try {
	//			if (plottingSystem == null) {
	//				plottingSystem = PlottingFactory.createPlottingSystem();
	//			}
	//		} catch (Exception e) {
	//			UIHelper.showError("Unable to create plotting system", e.getMessage());
	//			logger.error("Unable to create plotting system", e);
	//			return;
	//		}
	//		Composite composite = new Composite(parent, SWT.None);
	//		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
	//		composite.setLayout(new FillLayout());
	//		plottingSystem.createPlotPart(composite,
	//				getTitle(),
	//				// unique id for plot.
	//				getViewSite().getActionBars(),
	//				PlotType.XY,
	//				this);
	//	}

	@SuppressWarnings({ "static-access" })
	private void createTimeBarComposite(Composite parent) {
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(new GridLayout(2, false));
		timeBarViewer = new TimeBarViewer(composite, SWT.H_SCROLL | SWT.V_SCROLL);
		timeBarViewer.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		timeBarViewer.setTimeScalePosition(TimeBarViewer.TIMESCALE_POSITION_TOP);

		timeBarViewer.setDrawRowGrid(true);
		timeBarViewer.setAutoScaleRows(2);
		timeBarViewer.setAutoscrollEnabled(true);
		timeBarViewer.setMilliAccuracy(true);
		timeBarViewer.setDrawOverlapping(true);

		timeBarViewer.registerTimeBarRenderer(TimingGroupModel.class, new CollectionModelRenderer());
		timeBarViewer.registerTimeBarRenderer(SpectrumModel.class, new CollectionModelRenderer());
		timeBarViewer.setTimeScaleRenderer(new TimingGroupsScaleRenderer());
		timeBarViewer.setModel(TimeResolvedExperimentModel.INSTANCE.getTimeBarModel());
		resetToDisplayWholeExperimentTime();
		timeBarViewer.setAdjustMinMaxDatesByModel(true);
		timeBarViewer.setLineDraggingAllowed(false);
		marker = new TimeBarMarkerImpl(true, TimebarHelper.getTime().advanceMillis(INITIAL_TIMEBAR_MARKER_IN_MILLI));

		TimeResolvedExperimentModel.INSTANCE.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(TimeResolvedExperimentModel.SCANNING_PROP_NAME)) {
					if ((boolean) evt.getNewValue()) {
						marker.setDate(TimebarHelper.getTime());
						timeBarViewer.addMarker(marker);
					} else {
						timeBarViewer.remMarker(marker);
					}
				} else if (evt.getPropertyName().equals(TimeResolvedExperimentModel.CURRENT_SCANNING_SPECTRUM_PROP_NAME)) {
					SpectrumModel spectrum = (SpectrumModel) evt.getNewValue();
					marker.setDate(spectrum.getEnd().copy());
				}
			}
		});

		timeBarViewer.addTimeBarChangeListener(new ITimeBarChangeListener() {

			@Override
			public void markerDragStopped(TimeBarMarker arg0) {
				if (arg0.getDate().getMillis() == 0) {
					timeBarViewer.setStartDate(TimebarHelper.getTime());
					marker.setDate(TimebarHelper.getTime().advanceMillis(INITIAL_TIMEBAR_MARKER_IN_MILLI));
				}
			}

			@Override
			public void markerDragStarted(TimeBarMarker arg0) {}

			@Override
			public void intervalIntermediateChange(TimeBarRow arg0, Interval arg1, JaretDate arg2, JaretDate arg3) {}

			@Override
			public void intervalChanged(TimeBarRow arg0, Interval arg1, JaretDate arg2, JaretDate arg3) {}

			@Override
			public void intervalChangeStarted(TimeBarRow arg0, Interval arg1) {}

			@Override
			public void intervalChangeCancelled(TimeBarRow arg0, Interval arg1) {}
		});
		MenuManager menuManager = new MenuManager();
		Menu menu = menuManager.createContextMenu(timeBarViewer);
		// Set the MenuManager
		timeBarViewer.setMenu(menu);
		getSite().registerContextMenu(menuManager, timeBarViewer);
		getSite().setSelectionProvider(timeBarViewer);

		// Controls
		Composite controls = new Composite(composite, SWT.None);
		controls.setLayoutData(new GridData(SWT.END, SWT.FILL, false, true));
		controls.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		scale = new Scale(controls, SWT.VERTICAL);

		timeBarViewer.addControlListener(new ControlListener() {
			@Override
			public void controlResized(ControlEvent e) {
				updateScaleSelection();
			}
			@Override
			public void controlMoved(ControlEvent e) {}
		});

		timeBarViewer.setMarkerRenderer(new ExperimentMarkerRenderer());

		// TODO Adjust accordingly
		scale.setMinimum(10);
		scale.setSelection(10);
		scale.setMaximum(1000);

		scale.setIncrement(100);
		scale.setPageIncrement(500);

		scale.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		scale.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				int selection = scale.getSelection();
				timeBarViewer.setPixelPerSecond((double) selection / 1000);
				if (selection == scale.getMinimum()) {
					resetToDisplayWholeExperimentTime();
				} else {
					IStructuredSelection structuredSelection = (IStructuredSelection) timeBarViewer.getSelection();
					if (structuredSelection.getFirstElement() != null) {
						timeBarViewer.scrollIntervalToVisible((Interval) structuredSelection.getFirstElement());
					}
				}
			}
		});

		TimeResolvedExperimentModel.INSTANCE.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(TimeResolvedExperimentModel.EXPERIMENT_DURATION_PROP_NAME)) {
					resetToDisplayWholeExperimentTime();
					updateScaleSelection();
					updateTopupMarkers((double) evt.getNewValue());
				}
			}
		});

		updateTopupMarkers(TimeResolvedExperimentModel.INSTANCE.getDuration());
	}

	private void updateTopupMarkers(double duration) {
		if (timeBarViewer.getMarkers() != null) {
			timeBarViewer.getMarkers().clear();
		}
		for (TimeBarMarker marker : TimeResolvedExperimentModel.getTopupTimes()) {
			if (TimeResolvedExperimentModel.INSTANCE.getUnit().convertToMilli(duration) >= marker.getDate().getMillisInDay()) {
				timeBarViewer.addMarker(marker);
			}
		}
	}

	private void resetToDisplayWholeExperimentTime() {
		timeBarViewer.scrollIntervalToVisible((Interval) TimeResolvedExperimentModel.INSTANCE.getGroupList().get(0));
		double width = timeBarViewer.getClientArea().width - timeBarViewer.getYAxisWidth();
		if (width > 0) {
			double pixelPerSecond = width / TimeResolvedExperimentModel.INSTANCE.getDurationInSec();
			if (pixelPerSecond > 0) {
				timeBarViewer.setPixelPerSecond(pixelPerSecond);
			}
		}
	}

	@Override
	public void setFocus() {
		timeBarViewer.setFocus();
	}

	private final List<Binding> groupBindings = new ArrayList<Binding>();

	private void showGroupDetails(final Section groupSection, IStructuredSelection structuredSelection) {
		TimingGroupModel group = (TimingGroupModel) structuredSelection.getFirstElement();
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
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(group)));

			startTimeValueText.setModel(group, ExperimentTimingDataModel.START_TIME_PROP_NAME);
			startTimeValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			startTimeValueText.setEditable(false);
			startTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(startTimeValueText),
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			endTimeValueText.setModel(group, ExperimentTimingDataModel.END_TIME_PROP_NAME);
			endTimeValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			endTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(endTimeValueText),
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			timePerSpectrumValueText.setModel(group, TimingGroupModel.TIME_PER_SPECTRUM_PROP_NAME);
			timePerSpectrumValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			timePerSpectrumValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(timePerSpectrumValueText),
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));


			noOfSpectrumValueText.setModel(group, TimingGroupModel.NO_OF_SPECTRUM_PROP_NAME);

			integrationTimeValueText.setModel(group, TimingGroupModel.INTEGRATION_TIME_PROP_NAME);
			integrationTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			integrationTimeValueText.setUnit(ClientConfig.UnitSetup.MILLI_SEC.getText());

			noOfAccumulationValueText.setModel(group, TimingGroupModel.NO_OF_ACCUMULATION_PROP_NAME);
			noOfAccumulationValueText.setEditable(false);

			delayBeforeFristSpectrumValueText.setModel(group, ExperimentTimingDataModel.DELAY_PROP_NAME);
			delayBeforeFristSpectrumValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			delayBeforeFristSpectrumValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			delayBeforeFristSpectrumValueText.setUnit(group.getUnit().getWorkingUnit().getUnitText());
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(delayBeforeFristSpectrumValueText),
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));

			spectrumDelayValueText.setModel(group, TimingGroupModel.DELAY_BETWEEN_SPECTRUM_PROP_NAME);
			spectrumDelayValueText.setConverters(modelToTargetConverter, targetToModelConverter);
			spectrumDelayValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			groupBindings.add(dataBindingCtx.bindValue(
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(spectrumDelayValueText),
					BeanProperties.value(TimingGroupModel.UNIT_PROP_NAME).observe(group),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					unitConverter));
		} catch (Exception e) {
			// TODO Handle this!
			e.printStackTrace();
		}
	}

	private void updateScaleSelection() {
		double width = timeBarViewer.getClientArea().width - timeBarViewer.getYAxisWidth();
		if (width > 0) {
			double pixelPerSecond = width / TimeResolvedExperimentModel.INSTANCE.getDurationInSec();
			scale.setMaximum((int)(TIMEBAR_ZOOM_FACTOR * pixelPerSecond * 1000));
			scale.setMinimum((int) (pixelPerSecond * 1000));
			scale.setSelection(scale.getMinimum());
			if (pixelPerSecond > 0) {
				timeBarViewer.setPixelPerSecond((double) scale.getSelection() / 1000);
			}
		}
	}

	@Override
	public void dispose() {
		sampleMotorsComposite.dispose();
		super.dispose();
	}
}
