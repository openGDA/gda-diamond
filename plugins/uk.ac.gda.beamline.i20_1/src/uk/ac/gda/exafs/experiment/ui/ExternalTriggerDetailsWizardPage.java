/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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
import java.util.Iterator;
import java.util.List;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.map.IObservableMap;
import org.eclipse.core.databinding.observable.set.IObservableSet;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableMapLabelProvider;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.ComboBoxViewerCellEditor;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerComparator;
import org.eclipse.jface.window.Window;
import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.experiment.trigger.DetectorDataCollection;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;
import uk.ac.gda.exafs.experiment.ui.data.ExternalTriggerSetting;
import uk.ac.gda.ui.components.NumberEditorControl;

public class ExternalTriggerDetailsWizardPage extends WizardPage {

	private static Logger logger = LoggerFactory.getLogger(ExternalTriggerDetailsWizardPage.class);


	private final ExternalTriggerSetting externalTriggerSetting;
	private TableViewer sampleEnvironmentTableViewer;

	private Label xhUsrPortText;
	private NumberEditorControl xhPulseWidthText;
	private NumberEditorControl xhDelayText;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ExternalTriggerDetailsTimebarComposite timebar;

	public ExternalTriggerDetailsWizardPage(ExternalTriggerSetting externalTriggerSetting) {
		super("wizardPage");
		setTitle("TFG Trigger Details");
		setDescription("");
		this.externalTriggerSetting = externalTriggerSetting;
	}

	@Override
	public void createControl(Composite parent) {
		Composite container = new Composite(parent, SWT.NULL);

		setControl(container);
		container.setLayout(new GridLayout(2, false));

		Label sampleEnvLabel = new Label(container, SWT.None);
		sampleEnvLabel.setText("Sample environment");
		GridData gridData = new GridData(SWT.FILL, SWT.BEGINNING, false, false);
		gridData.horizontalSpan = 2;
		sampleEnvLabel.setLayoutData(gridData);

		Composite tableContainer = new Composite(container, SWT.NULL);
		gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
		gridData.heightHint = 120;
		tableContainer.setLayoutData(gridData);
		TableColumnLayout layout = new TableColumnLayout();
		tableContainer.setLayout(layout);

		sampleEnvironmentTableViewer = new TableViewer(tableContainer, SWT.BORDER | SWT.MULTI);
		sampleEnvironmentTableViewer.getTable().setHeaderVisible(true);
		TableViewerColumn viewerNumberColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE, 0);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Name");
		viewerNumberColumn.setEditingSupport(new EditingSupport(sampleEnvironmentTableViewer) {
			@Override
			protected void setValue(Object element, Object value) {
				((TriggerableObject) element).setName((String) value);
			}
			@Override
			protected Object getValue(Object element) {
				return ((TriggerableObject) element).getName();
			}
			@Override
			protected CellEditor getCellEditor(Object element) {
				return new TextCellEditor(sampleEnvironmentTableViewer.getTable());
			}
			@Override
			protected boolean canEdit(Object element) {
				return true;
			}
		});

		TableViewerColumn viewerDelayColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE, 1);
		layout.setColumnData(viewerDelayColumn.getColumn(), new ColumnWeightData(1));
		viewerDelayColumn.getColumn().setText("Delay after Topup");
		viewerDelayColumn.getColumn().addSelectionListener( new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.debug("Change sort order");
				sampleEnvironmentTableViewer.getTable().setSortDirection(comparator.getSortDirection());
				sampleEnvironmentTableViewer.getTable().setSortColumn(viewerDelayColumn.getColumn());
				sampleEnvironmentTableViewer.refresh();
				comparator.setSortDirection( -1*comparator.getSortDirection() );
			}
		});

		viewerDelayColumn.setEditingSupport(new EditingSupport(sampleEnvironmentTableViewer) {
			@Override
			protected void setValue(Object element, Object value) {
				((TriggerableObject) element).setTriggerDelay(Double.parseDouble((String) value));
			}
			@Override
			protected Object getValue(Object element) {
				return Double.toString(((TriggerableObject) element).getTriggerDelay());
			}
			@Override
			protected CellEditor getCellEditor(Object element) {
				return new TextCellEditor(sampleEnvironmentTableViewer.getTable());
			}
			@Override
			protected boolean canEdit(Object element) {
				return true;
			}
		});

		viewerNumberColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE, 2);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Pulse width");
		viewerNumberColumn.setEditingSupport(new EditingSupport(sampleEnvironmentTableViewer) {
			@Override
			protected void setValue(Object element, Object value) {
				((TriggerableObject) element).setTriggerPulseLength(Double.parseDouble((String) value));
			}
			@Override
			protected Object getValue(Object element) {
				return Double.toString(((TriggerableObject) element).getTriggerPulseLength());
			}
			@Override
			protected CellEditor getCellEditor(Object element) {
				return new TextCellEditor(sampleEnvironmentTableViewer.getTable());
			}
			@Override
			protected boolean canEdit(Object element) {
				return true;
			}
		});

		viewerNumberColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE, 3);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Output port");
		viewerNumberColumn.setEditingSupport(new EditingSupport(sampleEnvironmentTableViewer) {
			@Override
			protected void setValue(Object element, Object value) {
				((TriggerableObject) element).setTriggerOutputPort((TriggerOutputPort)value);
			}
			@Override
			protected Object getValue(Object element) {
				return ((TriggerableObject) element).getTriggerOutputPort();
			}
			@Override
			protected CellEditor getCellEditor(Object element) {
				final ComboBoxViewerCellEditor ce = new ComboBoxViewerCellEditor(sampleEnvironmentTableViewer.getTable());
				ce.setLabelProvider(new LabelProvider());
				ce.setContentProvider(new ArrayContentProvider());
				List<TriggerOutputPort> availablePorts = new ArrayList<TriggerOutputPort>();
				TriggerOutputPort[] values = TriggerableObject.TriggerOutputPort.values();
				for (int i=2; i<values.length; i++) {
					availablePorts.add(values[i]);
				}
				ce.setInput(availablePorts);
				return ce;
			}
			@Override
			protected boolean canEdit(Object element) {
				return true;
			}
		});

		// Add another column to show timing of trigger relative to spectra start time.
		viewerNumberColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE, 4);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Time relative to spectra");

		Composite tableContainerAddRemove = new Composite(container, SWT.NULL);
		gridData = new GridData(SWT.END, SWT.FILL, false, true);
		tableContainerAddRemove.setLayoutData(gridData);
		tableContainerAddRemove.setLayout(new GridLayout(1, false));
		Button addButton = new Button(tableContainerAddRemove, SWT.None);
		addButton.setText("Add");
		addButton.setLayoutData(new GridData(SWT.FILL, SWT.FILL, false, false));
		addButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					externalTriggerSetting.getSampleEnvironment().add(externalTriggerSetting.getTfgTrigger().createNewSampleEnvEntry());
				} catch (Exception e) {
					UIHelper.showError("Error", e.getMessage());
				}
			}
		});

		Button removeButton = new Button(tableContainerAddRemove, SWT.None);
		removeButton.setText("Remove");
		removeButton.setLayoutData(new GridData(SWT.FILL, SWT.FILL, false, false));
		removeButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				StructuredSelection selection = (StructuredSelection) sampleEnvironmentTableViewer.getSelection();
				if (!selection.isEmpty()) {
					Iterator<?> iterator = selection.iterator();
					while (iterator.hasNext()) {
						externalTriggerSetting.getSampleEnvironment().remove(iterator.next());
					}
				}
			}
		});

		Button copyButton = new Button(tableContainerAddRemove, SWT.None);
		copyButton.setText("Copy...");
		copyButton.setLayoutData(new GridData(SWT.FILL, SWT.FILL, false, false));
		copyButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				StructuredSelection selection = (StructuredSelection) sampleEnvironmentTableViewer.getSelection();
				if (!selection.isEmpty()) {

					InputDialog numberInput = new InputDialog(parent.getShell(), "Copy trigger parameters", "Enter start time to place copied triggers : ", "0.0", new DoubleValidator() );
					if(numberInput.open() == Window.OK) {

						List<TriggerableObject> newTriggers = new ArrayList<>();
						Iterator<?> iterator = selection.iterator();
						while (iterator.hasNext()) {
							TriggerableObject tObject = (TriggerableObject)iterator.next();
							logger.info("Copy triggers : length = {}, delay = {}, port = {}", tObject.getTriggerPulseLength(), tObject.getTriggerDelay(), tObject.getTriggerOutputPort().getUsrPortNumber());

							// Create new object, a copy of the original
							TriggerableObject newTrigger = externalTriggerSetting.getTfgTrigger().createNewSampleEnvEntry(tObject.getTriggerDelay(), tObject.getTriggerPulseLength(), tObject.getTriggerOutputPort());
							newTrigger.setName( tObject.getName() );
							newTriggers.add(newTrigger);
						}
						double origTriggerOverallStartTime = newTriggers.stream().mapToDouble(TriggerableObject::getTriggerDelay).min().getAsDouble();
						double userTriggerStartTime = Double.parseDouble(numberInput.getValue());

						// Adjust time of each trigger to required start time
						newTriggers.forEach((newTrigger) -> {
							double newTime = newTrigger.getTriggerDelay() - origTriggerOverallStartTime	+ userTriggerStartTime;
							newTrigger.setTriggerDelay(newTime);
							externalTriggerSetting.getSampleEnvironment().add(newTrigger);
						});
					}
				}
			}
		});

		try {

			Group xhParent = new Group(container, SWT.None);
			xhParent.setText(externalTriggerSetting.getTfgTrigger().getDetectorDataCollection().getName());
			gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
			gridData.horizontalSpan = 2;
			xhParent.setLayoutData(gridData);
			xhParent.setLayout(new GridLayout(6, false));

			Label xhDelayLabel = new Label(xhParent, SWT.None);
			xhDelayLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			xhDelayLabel.setText("Delay after Topup: ");
			xhDelayText = new NumberEditorControl(xhParent, SWT.None, externalTriggerSetting.getTfgTrigger().getDetectorDataCollection(), TriggerableObject.TRIGGER_DELAY_PROP_NAME, false);
			xhDelayText.setUnit(TFGTrigger.DEFAULT_DELAY_UNIT.getUnitText());
			xhDelayText.setDigits(6);
			gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
			gridData.widthHint = 140;
			xhDelayText.setLayoutData(gridData);

			Label xhPulseWidthLabel = new Label(xhParent, SWT.None);
			xhPulseWidthLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			xhPulseWidthLabel.setText("Pulse width: ");
			xhPulseWidthText = new NumberEditorControl(xhParent, SWT.None, externalTriggerSetting.getTfgTrigger().getDetectorDataCollection(), TriggerableObject.TRIGGER_PULSE_LENGTH_PROP_NAME, false);
			xhPulseWidthText.setUnit(TFGTrigger.DEFAULT_DELAY_UNIT.getUnitText());
			xhPulseWidthText.setDigits(6);
			gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
			gridData.widthHint = 140;
			xhPulseWidthText.setLayoutData(gridData);

			Label xhUsrPortLabel = new Label(xhParent, SWT.None);
			xhUsrPortLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			xhUsrPortLabel.setText("Output port: ");
			xhUsrPortText = new Label(xhParent, SWT.None);
			xhUsrPortText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));

			timebar = new ExternalTriggerDetailsTimebarComposite(externalTriggerSetting, container, SWT.None);
			gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
			gridData.horizontalSpan = 2;
			gridData.heightHint = 200;
			timebar.setLayoutData(gridData);
			doBinding();

		} catch (Exception ex) {
			logger.error("Unable to bind data", ex);
		}
	}


	private void doBinding() {
		ObservableListContentProvider sampleEnvContent = new ObservableListContentProvider();
		IObservableSet knownElements = sampleEnvContent.getKnownElements();

		final IObservableMap names = BeanProperties.value(TriggerableObject.class,
				TriggerableObject.NAME_PROP_NAME).observeDetail(knownElements);
		final IObservableMap delay = BeanProperties.value(TriggerableObject.class,
				TriggerableObject.TRIGGER_DELAY_PROP_NAME).observeDetail(knownElements);
		final IObservableMap pulseTimes = BeanProperties.value(TriggerableObject.class,
				TriggerableObject.TRIGGER_PULSE_LENGTH_PROP_NAME).observeDetail(knownElements);
		final IObservableMap portName = BeanProperties.value(TriggerableObject.class,
				TriggerableObject.TRIGGER_OUTPUT_PORT_PROP_NAME).observeDetail(knownElements);
		IObservableMap[] labelMaps = {names, delay, pulseTimes, portName};

		sampleEnvironmentTableViewer.setLabelProvider(new ObservableMapLabelProvider(labelMaps) {
			@Override
			public String getColumnText(Object element, int columnIndex) {
				TriggerableObject obj = (TriggerableObject) element;
				switch (columnIndex) {
				case 0: return obj.getName();
				case 1: return Double.toString(obj.getTriggerDelay()) + " " + TFGTrigger.DEFAULT_DELAY_UNIT.getUnitText();
				case 2: return Double.toString(obj.getTriggerPulseLength())  + " " + TFGTrigger.DEFAULT_DELAY_UNIT.getUnitText();
				case 3: return obj.getTriggerOutputPort().getPortName();
				case 4: return getRelativeTimeStringForTrigger(obj);
				default : return "Unknown";
				}
			}
		});
		sampleEnvironmentTableViewer.setContentProvider(sampleEnvContent);
		sampleEnvironmentTableViewer.setInput(externalTriggerSetting.getSampleEnvironment());
		sampleEnvironmentTableViewer.setComparator(comparator);

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(xhUsrPortText),
				BeanProperties.value(TriggerableObject.TRIGGER_OUTPUT_PORT_PROP_NAME).observe(externalTriggerSetting.getTfgTrigger().getDetectorDataCollection()),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return TriggerableObject.TriggerOutputPort.valueOf(((String) value));
					}
				},
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((TriggerOutputPort) value).getPortName();
					}
				});
	}

	/**
	 * Return String showing time of trigger relative to start of spectra accumulation.
	 * @since 30/9/2015
	 * @author Iain Hall
	 */
	private String getRelativeTimeStringForTrigger( TriggerableObject trigger ) {
		DetectorDataCollection collection = externalTriggerSetting.getTfgTrigger().getDetectorDataCollection();

		int numFrames = collection.getNumberOfFrames();
		double timePerFrame = collection.getTotalDuration()/numFrames;
		double timeRelativeToCollectionStart = trigger.getTriggerDelay() - collection.getTriggerDelay();

		int frameNumber = (int)Math.floor( timeRelativeToCollectionStart/timePerFrame );

		if ( frameNumber < 0 ) {
			return "Before data collection";
		} else if ( frameNumber > numFrames-1 ) {
			return "After data collection";
		}

		double timeRelativeToFrameStart = timeRelativeToCollectionStart-frameNumber*timePerFrame;

		String timeStr = String.format("%5g",  timeRelativeToFrameStart );

		String str = "Spectra " + (frameNumber+1) + " + " + timeStr + " s";
		return str;
	}

	/**
	 * Validator used to check floating point number input (collection time dialog box)
	 */
	private class DoubleValidator implements IInputValidator {
		/**
		 * Validates a string to make sure it's an integer > 0. Returns null for no error, or string with error message
		 *
		 * @param newText
		 * @return String
		 */
		@Override
		public String isValid(String newText) {
			Double value = null;
			try {
				value = Double.valueOf(newText);
			} catch (NumberFormatException nfe) {
				// swallow, value==null
			}
			if (value == null || value < 0) {
				return "Text should be a number > 0";
			}
			return null;
		}
	}

	private class TimeOrderComparator extends ViewerComparator {
		private int sortDirection = 1;

		public int getSortDirection() {
			return sortDirection;
		}

		public void setSortDirection(int dir) {
			sortDirection = dir;
		}
		@Override
		public int compare(Viewer viewer, Object e1, Object e2) {
			TriggerableObject t1 = (TriggerableObject) e1;
			TriggerableObject t2 = (TriggerableObject) e2;
			int compInt = Double.compare(t1.getTotalDelay(), t2.getTotalDelay());
			if (compInt == 0) {
				return 0;
			}
			compInt *= sortDirection;
			return compInt;

		}
	}
	private TimeOrderComparator comparator = new TimeOrderComparator();
}
