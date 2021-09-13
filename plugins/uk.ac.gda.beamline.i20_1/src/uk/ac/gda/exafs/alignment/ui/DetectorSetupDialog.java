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

package uk.ac.gda.exafs.alignment.ui;

import java.text.NumberFormat;
import java.text.ParseException;
import java.util.Arrays;
import java.util.Map;

import org.dawnsci.ede.DataHelper;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.ValidationStatusProvider;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.core.databinding.validation.IValidator;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.dialog.TitleAreaDialogSupport;
import org.eclipse.jface.databinding.dialog.ValidationMessageProvider;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.dialogs.IMessageProvider;
import org.eclipse.jface.dialogs.TitleAreaDialog;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.dialogs.ListSelectionDialog;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.detector.DetectorData;
import gda.device.detector.EdeDetector;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.detector.xstrip.XhDetector;
import gda.device.detector.xstrip.XhDetectorData;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.ede.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;

public class DetectorSetupDialog extends TitleAreaDialog {

	private static final int ADDED_DIALOG_WIDTH = 100;

	private static Logger logger = LoggerFactory.getLogger(DetectorSetupDialog.class);

	@Override
	protected Point getInitialSize() {
		Point point = super.getInitialSize();
		point.x += ADDED_DIALOG_WIDTH;
		return point;
	}

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private Text txtBiasVoltage;
	private Text txtExcludedStrips;

	private Binding bindTxtBiasVoltage;
	private Binding bindExcludedStrips;

	private String biasErrorMessage;
	private String detectorInputMessage;

	private final EdeDetector detector;
	private final DetectorData detectorData;

	private Text txtAccumulationReadoutTime;

	public DetectorSetupDialog(Shell parentShell) throws Exception {
		super(parentShell);
		detector = DetectorModel.INSTANCE.getCurrentDetector();
		detectorData = detector.getDetectorData();
		if (detectorData instanceof XhDetectorData) {
			biasErrorMessage = "Voltage not in range. Enter input between " + ((XhDetectorData) detectorData).getMinBias() + " and " + ((XhDetectorData) detectorData).getMaxBias() + ".";
			detectorInputMessage = "Edit details for Xh detector.";
		} else {
			detectorInputMessage = "Edit details for Ede Frelon detector.";
		}
		if (detector == null) {
			throw new Exception("Current Detector is null.");
		}
	}

	@Override
	protected Control createDialogArea(Composite parent) {
		Composite area = (Composite) super.createDialogArea(parent);
		Composite selectionComposite = new Composite(area, SWT.NONE);
		selectionComposite.setLayoutData(new GridData(GridData.FILL_BOTH));
		selectionComposite.setLayout(new GridLayout(2, false));

		Label lblBiasVoltage = new Label(selectionComposite, SWT.NONE);
		lblBiasVoltage.setText(UnitSetup.VOLTAGE.addUnitSuffixForLabel("Voltage"));
		lblBiasVoltage.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));

		txtBiasVoltage = new Text(selectionComposite, SWT.NONE);
		txtBiasVoltage.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));

		Label lblExcludedStrips = new Label(selectionComposite, SWT.NONE);
		lblExcludedStrips.setText("Excluded strips:");
		lblExcludedStrips.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));

		txtExcludedStrips = new Text(selectionComposite, SWT.NONE);
		txtExcludedStrips.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));
		txtExcludedStrips.setEditable(false);

		Listener excludedStripsTxtListener = new Listener() {
			@Override
			public void handleEvent(Event event) {
				if (event.type == SWT.MouseUp | event.type == SWT.KeyUp) {
					showExcludedStripsDialog();
				}
			}
		};

		txtExcludedStrips.addListener(SWT.MouseUp, excludedStripsTxtListener);
		txtExcludedStrips.addListener(SWT.KeyUp, excludedStripsTxtListener);

		if (detector.getDetectorData() instanceof FrelonCcdDetectorData) {
			addAccumulationReadoutTimeControls(selectionComposite);
		}

		createTemperatureTable(selectionComposite);
		bindingValues();
		return selectionComposite;
	}

	private void addAccumulationReadoutTimeControls(Composite parent) {
		Label lblReadoutTime = new Label(parent, SWT.NONE);
		lblReadoutTime.setText(UnitSetup.MILLI_SEC.addUnitSuffixForLabel("Accumulation readout time"));
		lblReadoutTime.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));

		txtAccumulationReadoutTime = new Text(parent, SWT.NONE);
		txtAccumulationReadoutTime.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));
		double timeMs = ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(DetectorModel.INSTANCE.getAccumulationReadoutTime(), ExperimentUnit.MILLI_SEC);
		txtAccumulationReadoutTime.setText(Double.toString(timeMs));
	}

	private void updateAccumulationReadoutTime() {
		if (txtAccumulationReadoutTime == null) {
			return;
		}
		try {
			logger.debug("Update model with accumulation readout time");
			Number newReadoutTime = NumberFormat.getInstance().parse(txtAccumulationReadoutTime.getText());
			double newTime = ExperimentUnit.MILLI_SEC.convertToDefaultUnit(newReadoutTime.doubleValue());
			DetectorModel.INSTANCE.setAccumulationReadoutTime(newTime);
		} catch (ParseException e) {
			logger.error("Problem updating detector accumulation readout time using value {}",	txtAccumulationReadoutTime.getText(), e);
		}
	}

	private void createTemperatureTable(Composite selectionComposite) {
		Label lblTemperature = new Label(selectionComposite, SWT.NONE);
		lblTemperature.setText("Temperature:");
		lblTemperature.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));

		final Composite temperatureSelectionComposite = new Composite(selectionComposite, SWT.NONE);
		temperatureSelectionComposite.setLayoutData(new GridData(GridData.FILL_BOTH));
		final TableColumnLayout layout = new TableColumnLayout();
		temperatureSelectionComposite.setLayout(layout);

		final Table temperatureTable = new Table(temperatureSelectionComposite, SWT.NONE);
		temperatureTable.setLinesVisible (true);
		temperatureTable.setHeaderVisible (true);
		temperatureTable.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));

		Map<String, Double> temperatureValues;
		Cursor cursor = null;
		try {
			// TODO Create generic wait
			cursor = Display.getDefault().getActiveShell().getCursor();
			Cursor waitCursor = Display.getDefault().getSystemCursor(SWT.CURSOR_WAIT);
			Display.getDefault().getActiveShell().setCursor(waitCursor);
			temperatureValues = (DetectorModel.INSTANCE.getCurrentDetector()).getTemperatures();
			if (!temperatureValues.isEmpty()) {
				int weight = 100 / temperatureValues.size();
				String[] values = new String[temperatureValues.size()];
				int i = 0;
				for (Map.Entry<String,Double> entry : temperatureValues.entrySet()) {
					TableColumn column = new TableColumn (temperatureTable, SWT.NONE);
					layout.setColumnData(column, new ColumnWeightData(weight));
					column.setText(entry.getKey());
					values[i++] = Double.toString(entry.getValue());
				}
				TableItem item = new TableItem (temperatureTable, SWT.NONE);
				item.setText(values);
			}
		} catch (DeviceException e) {
			UIHelper.showError("Unable to show temperature readings", e.getMessage());
			logger.error("Unable to show temperature readings", e);
		} finally {
			Display.getDefault().getActiveShell().setCursor(cursor);
		}
	}

	private void bindingValues() {

		TitleAreaDialogSupport.create(this, dataBindingCtx).setValidationMessageProvider(new ValidationMessageProvider() {
			@Override
			public String getMessage(ValidationStatusProvider statusProvider) {
				if (statusProvider == null) {
					return detectorInputMessage;
				}
				return super.getMessage(statusProvider);
			}

			@Override
			public int getMessageType(ValidationStatusProvider statusProvider) {
				int type = super.getMessageType(statusProvider);
				if(getButton(IDialogConstants.OK_ID) != null) {
					getButton(IDialogConstants.OK_ID).setEnabled(type != IMessageProvider.ERROR);
				}
				return type;
			}
		});
		if (detector instanceof XhDetector) {
			bindTxtBiasVoltage = dataBindingCtx.bindValue(
					WidgetProperties.text(SWT.Modify).observe(txtBiasVoltage),
					BeanProperties.value(DetectorModel.BIAS_PROP_NAME).observe(detectorData),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_ON_REQUEST).setBeforeSetValidator(new IValidator() {
						@Override
						public IStatus validate(Object value) {
							if (value instanceof Double) {
								if (((XhDetectorData) detectorData).isVoltageInRange((double) value)) {
									return ValidationStatus.ok();
								}
								return ValidationStatus.error(biasErrorMessage);
							}
							return ValidationStatus.error("Not a valid decimal value");
						}
					}),
					new UpdateValueStrategy().setAfterGetValidator(new IValidator() {
						@Override
						public IStatus validate(Object value) {
							if (((XhDetectorData) detectorData).isVoltageInRange((double) value)) {
								return ValidationStatus.ok();
							}
							return ValidationStatus.error("Voltage not in range");
						}
					}));

			txtBiasVoltage.addModifyListener(new ModifyListener() {
				@Override
				public void modifyText(ModifyEvent e) {
					bindTxtBiasVoltage.validateTargetToModel();
				}
			});
		}

		bindExcludedStrips = dataBindingCtx.bindValue(
				WidgetProperties.text(SWT.Modify).observe(txtExcludedStrips),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.CURRENT_DETECTOR_EXCLUDED_STRIPS_PROP_NAME),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_ON_REQUEST) {
					@Override
					public Object convert(Object value) {
						String excludedStrips = (String) value;
						if (excludedStrips.isEmpty()) {
							return new Integer[]{};
						}
						String[] valuesStringArray = excludedStrips.split(",");
						Integer[] excludedStripsArray = new Integer[valuesStringArray.length];
						for (int i = 0; i < valuesStringArray.length; i++) {
							excludedStripsArray[i] = new Integer(valuesStringArray[i]);
						}
						return excludedStripsArray;
					}
				},
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						Integer[] values = (Integer[]) value;
						return DataHelper.toString(values);
					}
				});
	}

	@Override
	protected void createButtonsForButtonBar(Composite parent) {
		createButton(parent, IDialogConstants.OK_ID,
				IDialogConstants.OK_LABEL, true);
		createButton(parent, IDialogConstants.CANCEL_ID,
				IDialogConstants.CANCEL_LABEL, false);
		if (detector instanceof XhDetector) {
			bindTxtBiasVoltage.validateModelToTarget();
		}
	}

	private void showExcludedStripsDialog() {
		ListSelectionDialog dialog =
				new ListSelectionDialog(
						Display.getDefault().getActiveShell(),
						DetectorModel.INSTANCE.getStrips(),
						new ArrayContentProvider(),
						new LabelProvider(),
						"Select excluded strips");
		if (!txtExcludedStrips.getText().isEmpty()) {
			String[] array = txtExcludedStrips.getText().split("\\s*,\\s*");
			Integer[] intArray = new Integer[array.length];
			for (int i = 0; i < array.length; i++) {
				intArray[i] = new Integer(array[i]);
			}
			dialog.setInitialElementSelections(Arrays.asList(intArray));
		}
		if (dialog.open() == Window.OK) {
			Object[] selection = dialog.getResult();
			txtExcludedStrips.setText(DataHelper.toString(selection));
		}
	}

	@Override
	public void create() {
		super.create();
		this.setTitle("Detector Setup");
		this.setMessage(detectorInputMessage);
	}

	@Override
	protected void okPressed() {
		bindExcludedStrips.updateTargetToModel();
		if (detector instanceof XhDetector) {
			bindTxtBiasVoltage.updateTargetToModel();
		}
		updateAccumulationReadoutTime();
		disposeBinding();
		super.okPressed();
	}

	@Override
	protected void cancelPressed() {
		disposeBinding();
		super.cancelPressed();
	}

	private void disposeBinding() {
		dataBindingCtx.dispose();
	}
}
