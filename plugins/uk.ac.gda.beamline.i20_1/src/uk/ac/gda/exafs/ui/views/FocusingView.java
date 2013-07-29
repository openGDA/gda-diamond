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

import gda.device.Scannable;
import gda.jython.Jython;
import gda.jython.JythonServerStatus;
import gda.observable.IObserver;

import java.util.ArrayList;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.databinding.validation.IValidator;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.fieldassist.ControlDecorationSupport;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorConfig;
import uk.ac.gda.exafs.data.DetectorUnavailableException;
import uk.ac.gda.exafs.data.SlitScanner;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.UIHelper.UIMotorControl;
import uk.ac.gda.exafs.ui.sections.DetectorROIsSesion;

public class FocusingView extends ViewPart {

	private static final int SLIT_PARAM_LABELS_WIDTH = 130;


	public static String ID = "uk.ac.gda.exafs.ui.views.focusingview";


	private static final int SPINNER_INCREMENT = (int) Math.pow(10, ClientConfig.DEFAULT_DECIMAL_PLACE);

	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private FormToolkit toolkit;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		createFocusingForm(parent);
	}

	private ScrolledForm createFocusingForm(Composite parent) {
		ScrolledForm scrolledform = toolkit.createScrolledForm(parent);
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Slits scan / Focusing");
		createFormSlitsParametersSection(form);
		DetectorROIsSesion.INSTANCE.createFormRoisSection(form, toolkit);
		createFormSampleZSection(form);
		createFormBendSection(form);
		createFormCurvatureSection(form);
		return scrolledform;
	}

	private final WritableList movingScannables = new WritableList(new ArrayList<Scannable>(), Scannable.class);
	private final MoveObserver moveObserver = new MoveObserver(movingScannables);
	private static class MoveObserver implements IObserver {
		private final WritableList movingScannables;
		public MoveObserver(WritableList movingScannables) {
			this.movingScannables = movingScannables;
		}

		@Override
		public void update(Object source, Object arg) {
			if (arg instanceof JythonServerStatus) {
				JythonServerStatus status = (JythonServerStatus) arg;
				if (status.scanStatus == Jython.RUNNING | status.scanStatus == Jython.PAUSED) {
					movingScannables.add(source);
				}
				else if (status.scanStatus == Jython.IDLE) {
					movingScannables.remove(source);
				}
			}
		}
	}

	@SuppressWarnings("static-access")
	private void createFormBendSection(Form form) {
		final Section bendSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(bendSection);
		bendSection.setText("Polychromator Benders");
		toolkit.paintBordersFor(bendSection);
		bendSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite bendSelectionComposite = toolkit.createComposite(bendSection, SWT.NONE);
		toolkit.paintBordersFor(bendSelectionComposite);
		bendSelectionComposite.setLayout(new GridLayout(2, false));
		bendSection.setClient(bendSelectionComposite);

		Label lblBend1Name = toolkit.createLabel(bendSelectionComposite, ScannableSetup.POLY_BENDER_1.getLabel(), SWT.NONE);
		lblBend1Name.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, bendSelectionComposite, ScannableSetup.POLY_BENDER_1, UIMotorControl.ROTATION, moveObserver);

		Label lblBend2Name = toolkit.createLabel(bendSelectionComposite, ScannableSetup.POLY_BENDER_2.getLabel(), SWT.NONE);
		lblBend2Name.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, bendSelectionComposite, ScannableSetup.POLY_BENDER_2, UIMotorControl.ROTATION, moveObserver);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(bendSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		bendSection.setSeparatorControl(defaultSectionSeparator);
	}

	@SuppressWarnings("static-access")
	private void createFormCurvatureSection(Form form) {
		final Section curvatureSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(curvatureSection);
		curvatureSection.setText("Curvature/Ellipticity");
		toolkit.paintBordersFor(curvatureSection);
		curvatureSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite curvatureSelectionComposite = toolkit.createComposite(curvatureSection, SWT.NONE);
		toolkit.paintBordersFor(curvatureSelectionComposite);
		curvatureSelectionComposite.setLayout(new GridLayout(2, false));
		curvatureSection.setClient(curvatureSelectionComposite);

		Label lblCurvature = toolkit.createLabel(curvatureSelectionComposite, ScannableSetup.POLY_CURVATURE.getLabel(), SWT.NONE);
		lblCurvature.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, curvatureSelectionComposite, ScannableSetup.POLY_CURVATURE, UIMotorControl.ROTATION, moveObserver);

		Label lblEllipticity = toolkit.createLabel(curvatureSelectionComposite, ScannableSetup.POLY_Y_ELLIPTICITY.getLabel(), SWT.NONE);
		lblEllipticity.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, curvatureSelectionComposite, ScannableSetup.POLY_Y_ELLIPTICITY, UIMotorControl.ROTATION, moveObserver);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(curvatureSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		curvatureSection.setSeparatorControl(defaultSectionSeparator);
	}

	@SuppressWarnings("static-access")
	private void createFormSampleZSection(Form form) {
		final Section sampleZSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(sampleZSection);
		sampleZSection.setText("Sample position");
		toolkit.paintBordersFor(sampleZSection);
		sampleZSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite sampleZSelectionComposite = toolkit.createComposite(sampleZSection, SWT.NONE);
		toolkit.paintBordersFor(sampleZSelectionComposite);
		sampleZSelectionComposite.setLayout(new GridLayout(2, false));
		sampleZSection.setClient(sampleZSelectionComposite);

		Label lblSampleZ = toolkit.createLabel(sampleZSelectionComposite, ScannableSetup.SAMPLE_Z_POSITION.getLabel(), SWT.NONE);
		lblSampleZ.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, sampleZSelectionComposite, ScannableSetup.SAMPLE_Z_POSITION, UIMotorControl.POSITION, moveObserver);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(sampleZSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		sampleZSection.setSeparatorControl(defaultSectionSeparator);
	}

	@SuppressWarnings("static-access")
	private void createFormSlitsParametersSection(Form form) {
		final Section slitsParametersSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(slitsParametersSection);
		slitsParametersSection.setText("Slits scan");
		toolkit.paintBordersFor(slitsParametersSection);
		slitsParametersSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite slitsParametersSelectionComposite = toolkit.createComposite(slitsParametersSection, SWT.NONE);
		toolkit.paintBordersFor(slitsParametersSelectionComposite);
		slitsParametersSelectionComposite.setLayout(new GridLayout(3, false));
		slitsParametersSection.setClient(slitsParametersSelectionComposite);

		Label lbl = toolkit.createLabel(slitsParametersSelectionComposite, ClientConfig.ScannableSetup.SLIT_3_HORIZONAL_GAP.getLabel(), SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		final Text txtGap = toolkit.createText(slitsParametersSelectionComposite, "", SWT.None);
		GridData gridDataForTxt = new GridData(GridData.BEGINNING, GridData.CENTER, false, false);
		gridDataForTxt.widthHint = SLIT_PARAM_LABELS_WIDTH;
		txtGap.setLayoutData(gridDataForTxt);

		Binding bindValue = dataBindingCtx.bindValue(
				WidgetProperties.text(SWT.Modify).observe(txtGap),
				BeanProperties.value(SlitScanner.GAP_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy().setBeforeSetValidator(new IValidator() {
					@Override
					public IStatus validate(Object value) {
						if (value instanceof Double) {
							if (SlitScanner.isGapInRange((double) value)) {
								return ValidationStatus.ok();
							}
							return ValidationStatus.error("Gap too large");
						}
						return ValidationStatus.error("Not a valid decimal value");
					}
				}),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ClientConfig.roundDoubletoString((double) value);
					}
				});
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, ClientConfig.ScannableSetup.SLIT_3_HORIZONAL_GAP.getUnit().getText(), SWT.NONE);
		lbl.setAlignment(SWT.LEFT);
		lbl.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, "From", SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		// TODO Load from saved value
		final Spinner spnFromOffset = new Spinner(slitsParametersSelectionComposite, SWT.BORDER);
		spnFromOffset.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		spnFromOffset.setIncrement(SPINNER_INCREMENT);
		spnFromOffset.setMaximum((int) SlitScanner.MAX_OFFSET * SPINNER_INCREMENT);
		spnFromOffset.setMinimum((int) SlitScanner.MIN_OFFSET * SPINNER_INCREMENT);
		spnFromOffset.setLayoutData(gridDataForTxt);
		toolkit.paintBordersFor(spnFromOffset);

		bindValue = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(spnFromOffset),
				BeanProperties.value(SlitScanner.FROM_OFFSET_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE) {
					@Override
					public Object convert(Object value) {
						return ((int) value) / SPINNER_INCREMENT;
					}
				}, null);
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, UnitSetup.MILLI_METER.getText(), SWT.NONE);
		lbl.setAlignment(SWT.LEFT);
		lbl.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, "To", SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		final Spinner spnToOffset = new Spinner(slitsParametersSelectionComposite, SWT.BORDER);
		spnToOffset.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		spnToOffset.setIncrement(SPINNER_INCREMENT);
		spnToOffset.setMaximum((int) SlitScanner.MAX_OFFSET * SPINNER_INCREMENT);
		spnToOffset.setMinimum((int) SlitScanner.MIN_OFFSET * SPINNER_INCREMENT);
		spnToOffset.setLayoutData(gridDataForTxt);
		toolkit.paintBordersFor(spnToOffset);

		bindValue = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(spnToOffset),
				BeanProperties.value(SlitScanner.TO_OFFSET_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE){
					@Override
					public Object convert(Object value) {
						return ((Integer) value) / SPINNER_INCREMENT;
					}
				},
				null);
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);
		lbl = toolkit.createLabel(slitsParametersSelectionComposite, UnitSetup.MILLI_METER.getText(), SWT.NONE);
		lbl.setAlignment(SWT.LEFT);
		lbl.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, "Step size", SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		final Text txtStep = toolkit.createText(slitsParametersSelectionComposite, "", SWT.None);
		txtStep.setLayoutData(gridDataForTxt);

		bindValue = dataBindingCtx.bindValue(
				WidgetProperties.text(SWT.Modify).observe(txtStep),
				BeanProperties.value(SlitScanner.STEP_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE).setBeforeSetValidator(new IValidator() {
					@Override
					public IStatus validate(Object value) {
						if (value instanceof Double) {
							return ValidationStatus.ok();
						}
						return ValidationStatus.error("Not a value decimal value");
					}
				}),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ClientConfig.roundDoubletoString((double) value);
					}
				});
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, UnitSetup.MILLI_METER.getText(), SWT.NONE);
		lbl.setAlignment(SWT.LEFT);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, true, false));

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, "Integration time ", SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		final Spinner integrationTime = new Spinner(slitsParametersSelectionComposite, SWT.BORDER);
		integrationTime.setLayoutData(gridDataForTxt);
		integrationTime.setMaximum(SlitScanner.MAX_INTEGRATION_TIME);
		integrationTime.setMinimum(SlitScanner.MIN_INTEGRATION_TIME);
		toolkit.paintBordersFor(integrationTime);

		bindValue = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(integrationTime),
				BeanProperties.value(SlitScanner.INTEGRATION_TIME_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE),
				null);
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);
		lbl = toolkit.createLabel(slitsParametersSelectionComposite, UnitSetup.MILLI_SEC.getText(), SWT.NONE);
		lbl.setAlignment(SWT.LEFT);
		lbl.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		Composite scanButtons = toolkit.createComposite(slitsParametersSelectionComposite);
		GridData gridData = new GridData(GridData.HORIZONTAL_ALIGN_FILL);
		gridData.horizontalSpan = 3;
		scanButtons.setLayoutData(gridData);
		scanButtons.setLayout(new GridLayout(2, true));

		Button startPauseButton = toolkit.createButton(scanButtons, "Start Scan", SWT.FLAT);
		startPauseButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startPauseButton),
				BeanProperties.value(SlitScanner.STATE_PROP_NAME).observe(SlitScanner.getInstance()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((int) value == Jython.IDLE);
					}
				});

		startPauseButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					SlitScanner.getInstance().doScan();
				} catch (DetectorUnavailableException e) {
					UIHelper.showError("Unable to scan", e.getMessage());
				}
			}
		});

		Button stopButton = new Button(scanButtons, SWT.FLAT);
		stopButton.setText("Stop");
		stopButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(stopButton),
				BeanProperties.value(SlitScanner.STATE_PROP_NAME).observe(SlitScanner.getInstance()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((int) value != Jython.IDLE);
					}
				});

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(slitsParametersSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		slitsParametersSection.setSeparatorControl(defaultSectionSeparator);

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(slitsParametersSection),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME));
	}

	@Override
	public void setFocus() {}

}
