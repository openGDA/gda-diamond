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

import java.util.Iterator;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.map.IObservableMap;
import org.eclipse.core.databinding.observable.set.IObservableSet;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableMapLabelProvider;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;
import uk.ac.gda.exafs.experiment.ui.data.ExternalTriggerSetting;

public class ExternalTriggerDetailsWizardPage extends WizardPage {
	private final ExternalTriggerSetting externalTriggerSetting;
	private TableViewer sampleEnvironmentTableViewer;

	private Label xhUsrPortText;
	private Text xhPulseWidthText;
	private Text xhDelayText;

	private Label photonShutterUsrPortText;
	private Text photonShutterPulseWidthText;
	private Text photonShutterDelayText;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

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
		TableViewerColumn viewerNumberColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE);
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

		viewerNumberColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Delay");
		viewerNumberColumn.setEditingSupport(new EditingSupport(sampleEnvironmentTableViewer) {
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

		viewerNumberColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE);
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

		viewerNumberColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Output port");

		viewerNumberColumn = new TableViewerColumn(sampleEnvironmentTableViewer, SWT.NONE);
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));
		viewerNumberColumn.getColumn().setText("Edge");

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

		Group photonShutterParent = new Group(container, SWT.None);
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		photonShutterParent.setLayoutData(gridData);
		photonShutterParent.setLayout(new GridLayout(6, false));
		photonShutterParent.setText("Photon Shutter");
		Label photonShutterDelayLabel = new Label(photonShutterParent, SWT.None);
		photonShutterDelayLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		photonShutterDelayLabel.setText("Delay: ");
		photonShutterDelayText = new Text(photonShutterParent, SWT.BORDER);
		photonShutterDelayText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label photonShutterPulseWidthLabel = new Label(photonShutterParent, SWT.None);
		photonShutterPulseWidthLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		photonShutterPulseWidthLabel.setText("Pulse width: ");
		photonShutterPulseWidthText = new Text(photonShutterParent, SWT.BORDER);
		photonShutterPulseWidthText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label photonShutterUsrPortLabel = new Label(photonShutterParent, SWT.None);
		photonShutterUsrPortLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		photonShutterUsrPortLabel.setText("Output port: ");
		photonShutterUsrPortText = new Label(photonShutterParent, SWT.None);
		photonShutterUsrPortText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Group xhParent = new Group(container, SWT.None);
		xhParent.setText("IT Collection");
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		xhParent.setLayoutData(gridData);
		xhParent.setLayout(new GridLayout(6, false));

		Label xhDelayLabel = new Label(xhParent, SWT.None);
		xhDelayLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		xhDelayLabel.setText("Delay: ");
		xhDelayText = new Text(xhParent, SWT.BORDER);
		xhDelayText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label xhPulseWidthLabel = new Label(xhParent, SWT.None);
		xhPulseWidthLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		xhPulseWidthLabel.setText("Pulse width: ");
		xhPulseWidthText = new Text(xhParent, SWT.BORDER);
		xhPulseWidthText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label xhUsrPortLabel = new Label(xhParent, SWT.None);
		xhUsrPortLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		xhUsrPortLabel.setText("Output port: ");
		xhUsrPortText = new Label(xhParent, SWT.None);
		xhUsrPortText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		doBinding();
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
		final IObservableMap isRisingEdge = BeanProperties.value(TriggerableObject.class,
				TriggerableObject.TRIGGER_PULSE_RISING_PROP_NAME).observeDetail(knownElements);
		IObservableMap[] labelMaps = {names, delay, pulseTimes, portName, isRisingEdge};

		sampleEnvironmentTableViewer.setLabelProvider(new ObservableMapLabelProvider(labelMaps) {
			@Override
			public String getColumnText(Object element, int columnIndex) {
				TriggerableObject obj = (TriggerableObject) element;
				switch (columnIndex) {
				case 0: return obj.getName();
				case 1: return Double.toString(obj.getTriggerDelay()) + " s";
				case 2: return Double.toString(obj.getTriggerPulseLength())  + " s";
				case 3: return obj.getTriggerOutputPort().getPortName();
				case 4: return obj.isPulseRising() ? "Rising" : "Falling";
				default : return "Unknown";
				}
			}
		});
		sampleEnvironmentTableViewer.setContentProvider(sampleEnvContent);
		sampleEnvironmentTableViewer.setInput(externalTriggerSetting.getSampleEnvironment());

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(photonShutterDelayText),
				BeanProperties.value(TriggerableObject.TRIGGER_DELAY_PROP_NAME).observe(externalTriggerSetting.getTfgTrigger().getPhotonShutter()));

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(photonShutterPulseWidthText),
				BeanProperties.value(TriggerableObject.TRIGGER_PULSE_LENGTH_PROP_NAME).observe(externalTriggerSetting.getTfgTrigger().getPhotonShutter()));

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(photonShutterUsrPortText),
				BeanProperties.value(TriggerableObject.TRIGGER_OUTPUT_PORT_PROP_NAME).observe(externalTriggerSetting.getTfgTrigger().getPhotonShutter()),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return TriggerableObject.TriggerOutputPort.valueOf(((String) value));
					}
				},
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((TriggerableObject.TriggerOutputPort) value).getPortName();
					}
				});

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(xhDelayText),
				BeanProperties.value(TriggerableObject.TRIGGER_DELAY_PROP_NAME).observe(externalTriggerSetting.getTfgTrigger().getDetector()));

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(xhPulseWidthText),
				BeanProperties.value(TriggerableObject.TRIGGER_PULSE_LENGTH_PROP_NAME).observe(externalTriggerSetting.getTfgTrigger().getDetector()));

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(xhUsrPortText),
				BeanProperties.value(TriggerableObject.TRIGGER_OUTPUT_PORT_PROP_NAME).observe(externalTriggerSetting.getTfgTrigger().getDetector()),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return TriggerableObject.TriggerOutputPort.valueOf(((String) value));
					}
				},
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((TriggerableObject.TriggerOutputPort) value).getPortName();
					}
				});
	}

}
