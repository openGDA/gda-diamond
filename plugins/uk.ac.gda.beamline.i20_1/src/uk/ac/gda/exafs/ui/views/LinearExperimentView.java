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

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.map.IObservableMap;
import org.eclipse.core.databinding.observable.set.IObservableSet;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableMapLabelProvider;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnViewerEditor;
import org.eclipse.jface.viewers.ColumnViewerEditorActivationEvent;
import org.eclipse.jface.viewers.ColumnViewerEditorActivationStrategy;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TableViewerEditor;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.ControlListener;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Scale;
import org.eclipse.swt.widgets.Widget;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.beamline.i20_1.utils.TimebarHelper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.detector.CollectionModel;
import uk.ac.gda.exafs.ui.data.detector.CollectionModelRenderer;
import uk.ac.gda.exafs.ui.data.detector.Group;
import uk.ac.gda.exafs.ui.data.detector.LinearExperimentModel;
import uk.ac.gda.exafs.ui.data.detector.MilliScale;
import uk.ac.gda.exafs.ui.data.detector.Spectrum;

import com.swtdesigner.ResourceManager;

import de.jaret.util.date.Interval;
import de.jaret.util.date.JaretDate;
import de.jaret.util.ui.timebars.TimeBarMarker;
import de.jaret.util.ui.timebars.TimeBarMarkerImpl;
import de.jaret.util.ui.timebars.model.ITimeBarChangeListener;
import de.jaret.util.ui.timebars.model.TimeBarRow;
import de.jaret.util.ui.timebars.swt.TimeBarViewer;

public class LinearExperimentView extends ViewPart {
	public static final String ID = "uk.ac.gda.exafs.ui.views.linearExperimentView";

	private static final int TIMEBAR_ZOOM_FACTOR = 100;

	private static final long INITIAL_TIMEBAR_MARKER_IN_MILLI = 10L;

	private static final int GROUP_TABLE_HEIGHT = 100;
	private static final int GROUP_TABLE_WIDTH = 100;

	private IPlottingSystem plottingSystem;
	private TimeBarViewer timeBarViewer;
	private FormToolkit toolkit;
	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private TableViewer groupsTableViewer;
	protected Label integrationTimeLabel;
	protected NumberEditorControl integrationTimeValueText;
	protected NumberEditorControl timePerSpectrumValueText;
	protected Label timePerSpectrumValueLabel;

	protected Label spectrumDelayValueLabel;

	protected NumberEditorControl spectrumDelayValueText;

	protected Label noOfAccumulationValueLabel;

	protected NumberEditorControl noOfAccumulationValueText;

	protected int maxAccumulationforDetector;

	private TimeBarMarkerImpl marker;

	private Action runExperimentAction;

	@Override
	public void createPartControl(final Composite parent) {
		if (toolkit == null) {
			toolkit = new FormToolkit(parent.getDisplay());
		}
		final SashForm all = new SashForm(parent, SWT.VERTICAL);
		all.SASH_WIDTH = 7;

		SashForm top = new SashForm(all, SWT.HORIZONTAL);
		top.SASH_WIDTH = 7;

		try {
			createPropertyComposite(top);
			createPlotComposite(top);
			createTimeBarComposite(all);
			bind();
			all.setWeights(new int[] {3, 2});
			top.setWeights(new int[] {3, 1});
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
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
					public Object convert(Object value) {
						if (value instanceof Group) {
							return super.convert(value);
						} else if (value instanceof Spectrum) {
							return super.convert(((Spectrum) value).getParent());
						}
						return null;
					}
				});
	}

	private void createPropertyComposite(Composite parent) throws Exception {
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1,false));
		ScrolledForm scrolledform = toolkit.createScrolledForm(composite);
		scrolledform.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new GridLayout(2, true));
		toolkit.decorateFormHeading(form);
		scrolledform.setText("Linear experiment");
		runExperimentAction = new Action() {
			@Override
			public void run() {
				LinearExperimentModel.INSTANCE.doCollection();
			}
		};
		runExperimentAction.setImageDescriptor(ResourceManager.getImageDescriptor(LinearExperimentView.class,
				"/icons/control_play_blue.png"));
		form.getToolBarManager().add(runExperimentAction);	// NEW LINE
		form.getToolBarManager().update(true);	// NEW LINE
		createExperimentDetailsSection(form.getBody());
		createGroupSection(form.getBody());

		dataBindingCtx.bindValue(
				BeanProperties.value(IAction.ENABLED).observe(runExperimentAction),
				BeanProperties.value(LinearExperimentModel.SCANNING_PROP_NAME).observe(LinearExperimentModel.INSTANCE),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return !((boolean) value);
					}
				});
	}

	private void createGroupSection(Composite parent) {
		@SuppressWarnings("static-access")
		Section section = toolkit.createSection(parent, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		section.setText("Timing groups");
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		section.setClient(sectionComposite);

		Composite regionsComposit = new Composite(sectionComposite, SWT.NONE);
		GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
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

		ColumnViewerEditorActivationStrategy actSupport = new ColumnViewerEditorActivationStrategy(groupsTableViewer) {
			@Override
			protected boolean isEditorActivationEvent(ColumnViewerEditorActivationEvent event) {
				return event.eventType == ColumnViewerEditorActivationEvent.TRAVERSAL
						|| event.eventType == ColumnViewerEditorActivationEvent.MOUSE_DOUBLE_CLICK_SELECTION
						|| (event.eventType == ColumnViewerEditorActivationEvent.KEY_PRESSED && event.keyCode == SWT.CR)
						|| event.eventType == ColumnViewerEditorActivationEvent.PROGRAMMATIC;
			}
		};

		TableViewerEditor.create(groupsTableViewer, actSupport, ColumnViewerEditor.TABBING_HORIZONTAL
				| ColumnViewerEditor.TABBING_MOVE_TO_ROW_NEIGHBOR
				| ColumnViewerEditor.TABBING_VERTICAL | ColumnViewerEditor.KEYBOARD_ACTIVATION);


		TableViewerColumn viewerNumberColumn = new TableViewerColumn(groupsTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Name");
		viewerNumberColumn.setEditingSupport(new GroupEditorSupport(groupsTableViewer) {
			@Override
			protected Object getValue(Object element) {
				return ((Group) element).getName();
			}

			@Override
			protected void setValue(Object element, Object value) {
				if (!((String) value).isEmpty()) {
					((Group) element).setName((String) value);
				}
			}
		});

		viewerNumberColumn = new TableViewerColumn(groupsTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(2));
		viewerNumberColumn.getColumn().setText("Start time");
		viewerNumberColumn.setEditingSupport(new GroupEditorSupport(groupsTableViewer) {
			@Override
			protected Object getValue(Object element) {
				return Double.toString(((Group) element).getStartTime());
			}
			@Override
			protected void setValue(Object element, Object value) {
				if (!((String) value).isEmpty()) {
					try {
						LinearExperimentModel.INSTANCE.setGroupStartTime((Group) element, Double.parseDouble((String) value));
					} catch(Exception e) {
						UIHelper.showWarning("Unable to set start time", e.getMessage());
					}
				}
			}
		});

		viewerNumberColumn = new TableViewerColumn(groupsTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(2));
		viewerNumberColumn.getColumn().setText("End Time");
		viewerNumberColumn.setEditingSupport(new GroupEditorSupport(groupsTableViewer) {
			@Override
			protected Object getValue(Object element) {
				return Double.toString(((Group) element).getEndTime());
			}

			@Override
			protected void setValue(Object element, Object value) {
				if (!((String) value).isEmpty()) {
					try {
						LinearExperimentModel.INSTANCE.setGroupEndTime((Group) element, Double.parseDouble((String) value));
					} catch(Exception e) {
						UIHelper.showWarning("Unable to set end time", e.getMessage());
					}
				}
			}
		});

		viewerNumberColumn = new TableViewerColumn(groupsTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Spectrums");

		ObservableListContentProvider contentProvider =
				new ObservableListContentProvider();
		// Create the label provider including monitoring
		// of the changes of the labels
		IObservableSet knownElements = contentProvider.getKnownElements();

		final IObservableMap names = BeanProperties.value(Group.class,
				CollectionModel.NAME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap startTimes = BeanProperties.value(Group.class,
				CollectionModel.START_TIME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap endTimes = BeanProperties.value(Group.class,
				CollectionModel.END_TIME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap noOfSpectrum = BeanProperties.value(Group.class,
				Group.NO_OF_SPECTRUMS_PROP_NAME).observeDetail(knownElements);
		IObservableMap[] labelMaps = {names, startTimes, endTimes, noOfSpectrum};

		groupsTableViewer.setContentProvider(contentProvider);
		groupsTableViewer.setLabelProvider(new ObservableMapLabelProvider(labelMaps) {
			@Override
			public String getColumnText(Object element, int columnIndex) {
				switch (columnIndex) {
				case 0: return (String) names.get(element);
				case 1: return DataHelper.roundDoubletoString((double) startTimes.get(element)) + " " + UnitSetup.MILLI_SEC.getText();
				case 2: return DataHelper.roundDoubletoString((double) endTimes.get(element)) + " " + UnitSetup.MILLI_SEC.getText();
				case 3: return Integer.toString((int) noOfSpectrum.get(element));
				default : return "Unkown column";
				}
			}
		});
		groupsTableViewer.setInput(LinearExperimentModel.INSTANCE.getGroupList());
		Composite buttonComposit = new Composite(regionsComposit, SWT.NONE);
		buttonComposit.setLayout(new GridLayout());
		buttonComposit.setLayoutData(new GridData(GridData.VERTICAL_ALIGN_FILL));
		final Button butAdd = new Button(buttonComposit, SWT.FLAT);
		butAdd.setText("Add");
		butAdd.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		butAdd.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				LinearExperimentModel.INSTANCE.addGroup();
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
					LinearExperimentModel.INSTANCE.removeGroup((Group) structuredSelection.getFirstElement());
				}
			}
		});

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);

		final Section groupSection = toolkit.createSection(parent, SWT.None);
		groupSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		final Composite groupSectionComposite = toolkit.createComposite(groupSection, SWT.NONE);
		groupSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		groupSection.setClient(groupSectionComposite);

		sectionSeparator = toolkit.createCompositeSeparator(groupSection);
		toolkit.paintBordersFor(sectionSeparator);
		groupSection.setSeparatorControl(sectionSeparator);
		groupsTableViewer.addSelectionChangedListener(new ISelectionChangedListener() {

			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				IStructuredSelection structuredSelection = (IStructuredSelection) event.getSelection();
				disposeIfNeeded(integrationTimeLabel);
				disposeIfNeeded(integrationTimeValueText);

				disposeIfNeeded(timePerSpectrumValueLabel);
				disposeIfNeeded(timePerSpectrumValueText);

				disposeIfNeeded(spectrumDelayValueLabel);
				disposeIfNeeded(spectrumDelayValueText);

				disposeIfNeeded(noOfAccumulationValueLabel);
				disposeIfNeeded(noOfAccumulationValueText);


				if (!structuredSelection.isEmpty()) {
					Group group = (Group) structuredSelection.getFirstElement();
					groupSection.setText(group.getName());
					try {

						timePerSpectrumValueLabel = toolkit.createLabel(groupSectionComposite, "Time per spectrum", SWT.None);
						timePerSpectrumValueLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
						timePerSpectrumValueText = new NumberEditorControl(groupSectionComposite, SWT.None, group, Group.TIME_PER_SPECTRUM_PROP_NAME, false);
						timePerSpectrumValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
						timePerSpectrumValueText.setUnit(UnitSetup.MILLI_SEC.getText());
						timePerSpectrumValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

						spectrumDelayValueLabel = toolkit.createLabel(groupSectionComposite, "Delay between spectrum", SWT.None);
						spectrumDelayValueLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
						spectrumDelayValueText = new NumberEditorControl(groupSectionComposite, SWT.None, group, Group.DELAY_BETWEEN_SPECTRUM_PROP_NAME, false);
						spectrumDelayValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
						spectrumDelayValueText.setUnit(UnitSetup.MILLI_SEC.getText());
						spectrumDelayValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

						integrationTimeLabel = toolkit.createLabel(groupSectionComposite, "Integration time", SWT.None);
						integrationTimeLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
						integrationTimeValueText = new NumberEditorControl(groupSectionComposite, SWT.None, group, Group.INTEGRATION_TIME_PROP_NAME, false);
						integrationTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
						integrationTimeValueText.setUnit(UnitSetup.MILLI_SEC.getText());
						integrationTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

						noOfAccumulationValueLabel = toolkit.createLabel(groupSectionComposite, "Detector read back accumulations", SWT.None);
						noOfAccumulationValueLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
						noOfAccumulationValueText = new NumberEditorControl(groupSectionComposite, SWT.None, group, Group.NO_OF_ACCUMULATION_PROP_NAME, false);
						// noOfAccumulationValueText.setEditable(false);
						noOfAccumulationValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
					} catch (Exception e) {
						UIHelper.showError("Unable to create controls", e.getMessage());
					}
					groupSection.setVisible(true);
				} else {
					groupSection.setVisible(false);
				}
				groupSectionComposite.layout(true, true);
				groupSection.layout(true, true);
				groupSection.getParent().layout(true, true);
			}

			private void disposeIfNeeded(Widget integrationTimeLabel) {
				if (integrationTimeLabel != null && !integrationTimeLabel.isDisposed()) {
					integrationTimeLabel.dispose();
				}
			}
		});
	}

	private static abstract class GroupEditorSupport extends EditingSupport {
		protected final TableViewer viewer;
		public GroupEditorSupport(TableViewer viewer) {
			super(viewer);
			this.viewer = viewer;
		}
		@Override
		protected CellEditor getCellEditor(Object element) {
			return new TextCellEditor(viewer.getTable());
		}
		@Override
		protected boolean canEdit(Object element) {
			return true;
		}
	}

	private void createExperimentDetailsSection(Composite parent) throws Exception {
		@SuppressWarnings("static-access")
		Section section = toolkit.createSection(parent, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		section.setText("Sample position and experiment");
		GridData data = new GridData(SWT.FILL, SWT.FILL, true, true);
		data.verticalSpan = 2;
		section.setLayoutData(data);
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		section.setClient(sectionComposite);

		Label lbl = toolkit.createLabel(sectionComposite, "I0 position", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		createSamplePositionComposite(sectionComposite, SingleSpectrumModel.I0_X_POSITION_PROP_NAME, SingleSpectrumModel.I0_Y_POSITION_PROP_NAME);

		lbl = toolkit.createLabel(sectionComposite, "It position", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		createSamplePositionComposite(sectionComposite, SingleSpectrumModel.IT_X_POSITION_PROP_NAME, SingleSpectrumModel.IT_Y_POSITION_PROP_NAME);

		// Iref

		final Button useIRefCheckButton = toolkit.createButton(sectionComposite, "Use Iref", SWT.CHECK);
		GridData gridData = new GridData(SWT.BEGINNING, SWT.CENTER, false, false);
		useIRefCheckButton.setLayoutData(gridData);

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

		final NumberEditorControl xPosition = new NumberEditorControl(xPositionComposite, SWT.None, SingleSpectrumModel.INSTANCE, SingleSpectrumModel.IREF_X_POSITION_PROP_NAME, false);
		xPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		xPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "y", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final NumberEditorControl yPosition = new NumberEditorControl(yPositionComposite, SWT.None, SingleSpectrumModel.INSTANCE, SingleSpectrumModel.IREF_Y_POSITION_PROP_NAME, false);
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

		lbl = toolkit.createLabel(sectionComposite, "Total experiment time", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		GridData gridDataForTxt = new GridData(SWT.FILL, SWT.CENTER, true, false);
		NumberEditorControl numberEditorControl = new NumberEditorControl(sectionComposite, SWT.None, LinearExperimentModel.INSTANCE, LinearExperimentModel.DURATION_IN_SEC_PROP_NAME, false);
		numberEditorControl.setUnit(ClientConfig.UnitSetup.SEC.getText());
		numberEditorControl.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		numberEditorControl.setLayoutData(gridDataForTxt);

		lbl = toolkit.createLabel(sectionComposite, "Delay between groups", SWT.NONE);
		lbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		gridDataForTxt = new GridData(SWT.FILL, SWT.CENTER, true, false);
		numberEditorControl = new NumberEditorControl(sectionComposite, SWT.None, LinearExperimentModel.INSTANCE, LinearExperimentModel.DELAY_BETWEEN_GROUPS_PROP_NAME, false);
		numberEditorControl.setUnit(ClientConfig.UnitSetup.MILLI_SEC.getText());
		numberEditorControl.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		numberEditorControl.setLayoutData(gridDataForTxt);

		final Button useExernalTriggerCheckButton = toolkit.createButton(sectionComposite, "Use exernal trigger", SWT.CHECK);
		gridData = new GridData(SWT.BEGINNING, SWT.CENTER, false, false);
		gridData.horizontalSpan = 2;
		useExernalTriggerCheckButton.setLayoutData(gridData);
		useExernalTriggerCheckButton.addListener(SWT.Selection, new Listener() {

			@Override
			public void handleEvent(Event event) {
				runExperimentAction.setEnabled(!useExernalTriggerCheckButton.getSelection());
			}
		});

		Composite roisSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(roisSectionSeparator);
		section.setSeparatorControl(roisSectionSeparator);
	}

	public void createSamplePositionComposite(Composite parent, String xPropName, String yPropName) throws Exception {
		Composite xyPositionComposite = toolkit.createComposite(parent, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		xyPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xyPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));

		Composite xPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(xPositionComposite);
		xPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		Label xPosLabel = toolkit.createLabel(xPositionComposite, "x", SWT.None);
		xPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final NumberEditorControl xPosition = new NumberEditorControl(xPositionComposite, SWT.None, SingleSpectrumModel.INSTANCE, xPropName, false);
		xPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		xPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "y", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final NumberEditorControl yPosition = new NumberEditorControl(yPositionComposite, SWT.None, SingleSpectrumModel.INSTANCE, yPropName, false);
		yPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		yPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		yPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void createPlotComposite(Composite parent) {
		try {
			if (plottingSystem == null) {
				plottingSystem = PlottingFactory.createPlottingSystem();
			}
		} catch (Exception e) {
			UIHelper.showError("Unable to create plotting system", e.getMessage());
			return;
		}
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(new FillLayout());
		plottingSystem.createPlotPart(composite,
				getTitle(),
				// unique id for plot.
				getViewSite().getActionBars(),
				PlotType.XY,
				this);
	}

	@SuppressWarnings({ "static-access" })
	private void createTimeBarComposite(Composite parent) {
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(new GridLayout(2, false));
		timeBarViewer = new TimeBarViewer(composite, SWT.H_SCROLL | SWT.V_SCROLL);
		timeBarViewer.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		timeBarViewer.setTimeScalePosition(TimeBarViewer.TIMESCALE_POSITION_TOP);

		timeBarViewer.setAdjustMinMaxDatesByModel(true);
		timeBarViewer.setDrawRowGrid(true);
		timeBarViewer.setAutoScaleRows(2);
		timeBarViewer.setAutoscrollEnabled(true);
		timeBarViewer.setMilliAccuracy(true);
		timeBarViewer.setDrawOverlapping(true);

		// TODO Adjust accordingly
		timeBarViewer.setInitialDisplayRange(TimebarHelper.getTime(), (int) LinearExperimentModel.INSTANCE.getDurationInSec());
		timeBarViewer.registerTimeBarRenderer(Group.class, new CollectionModelRenderer());
		timeBarViewer.registerTimeBarRenderer(Spectrum.class, new CollectionModelRenderer());
		timeBarViewer.setTimeScaleRenderer(new MilliScale());
		timeBarViewer.setModel(LinearExperimentModel.INSTANCE.getTimeBarModel());
		timeBarViewer.setLineDraggingAllowed(false);
		marker = new TimeBarMarkerImpl(true, TimebarHelper.getTime().advanceMillis(INITIAL_TIMEBAR_MARKER_IN_MILLI));

		LinearExperimentModel.INSTANCE.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(LinearExperimentModel.SCANNING_PROP_NAME)) {
					if ((boolean) evt.getNewValue()) {
						marker.setDate(TimebarHelper.getTime());
						timeBarViewer.addMarker(marker);
					} else {
						timeBarViewer.remMarker(marker);
					}
				} else if (evt.getPropertyName().equals(LinearExperimentModel.CURRENT_SCANNING_SPECTRUM_PROP_NAME)) {
					Spectrum spectrum = (Spectrum) evt.getNewValue();
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

		// Controls
		Composite controls = new Composite(composite, SWT.None);
		controls.setLayoutData(new GridData(SWT.END, SWT.FILL, false, true));
		controls.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		final Scale scale = new Scale(controls, SWT.VERTICAL);

		timeBarViewer.addControlListener(new ControlListener() {

			@Override
			public void controlResized(ControlEvent e) {
				double width = timeBarViewer.getClientArea().width - timeBarViewer.getYAxisWidth();
				if (width > 0) {
					scale.setMinimum((int) (width / LinearExperimentModel.INSTANCE.getDurationInSec()));
					scale.setSelection((int) (width / LinearExperimentModel.INSTANCE.getDurationInSec()));
					scale.setMaximum(TIMEBAR_ZOOM_FACTOR * (int) (width / LinearExperimentModel.INSTANCE.getDurationInSec()));
					timeBarViewer.setPixelPerSecond(scale.getSelection());
				}
			}
			@Override
			public void controlMoved(ControlEvent e) {
				// TODO Auto-generated method stub
			}
		});

		scale.setMinimum(10);
		scale.setSelection(10);
		scale.setMaximum(1000);

		scale.setIncrement(100);
		scale.setPageIncrement(500);

		scale.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		scale.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				timeBarViewer.setPixelPerSecond(scale.getSelection());
				IStructuredSelection structuredSelection = (IStructuredSelection) timeBarViewer.getSelection();
				if (structuredSelection.getFirstElement() != null) {
					timeBarViewer.scrollIntervalToVisible((Interval) structuredSelection.getFirstElement());
				}

			}
		});
	}

	@Override
	public void setFocus() {
		timeBarViewer.setFocus();
	}

}
