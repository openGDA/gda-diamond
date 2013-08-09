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

import java.util.ArrayList;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
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
import uk.ac.gda.exafs.ui.composites.MotorPositionEditorControl;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.ScannableMotorMoveObserver;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.sections.DetectorROIsSesion;

public class FocusingView extends ViewPart {

	public static String ID = "uk.ac.gda.exafs.ui.views.focusingview";

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
		try {
			createFormSampleSection(form);
			createFormBendSection(form);
			createFormCurvatureSection(form);
		} catch (Exception e) {
			UIHelper.showError("Unable to create scannable controls", e.getMessage());
		}
		return scrolledform;
	}

	@SuppressWarnings({ "static-access", "unused" })
	private void createFormBendSection(Form form) throws Exception {
		final WritableList movingScannables = new WritableList(new ArrayList<Scannable>(), Scannable.class);
		final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);
		final Section bendSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
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
		Scannable scannable = ScannableSetup.POLY_BENDER_1.getScannable();
		scannable.addIObserver(moveObserver);
		MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(bendSelectionComposite, SWT.None, scannable, true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label lblBend2Name = toolkit.createLabel(bendSelectionComposite, ScannableSetup.POLY_BENDER_2.getLabel(), SWT.NONE);
		lblBend2Name.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		scannable = ScannableSetup.POLY_BENDER_2.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(bendSelectionComposite, SWT.None, scannable, true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final ToolBar motorSectionTbar = new ToolBar(bendSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(motorSectionTbar, SWT.SEPARATOR);
		final ToolItem stopMotorsBarItem = ScannableMotorMoveObserver.setupStopToolItem(motorSectionTbar, movingScannables);
		bendSection.setTextClient(motorSectionTbar);
		movingScannables.addListChangeListener(ScannableMotorMoveObserver.getStopButtonListener(bendSection, stopMotorsBarItem));
		stopMotorsBarItem.setEnabled(!movingScannables.isEmpty());

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(bendSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		bendSection.setSeparatorControl(defaultSectionSeparator);
	}

	@SuppressWarnings({ "static-access", "unused" })
	private void createFormCurvatureSection(Form form) throws Exception {
		final WritableList movingScannables = new WritableList(new ArrayList<Scannable>(), Scannable.class);
		final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);
		final Section curvatureSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
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
		Scannable scannable = ScannableSetup.POLY_CURVATURE.getScannable();
		scannable.addIObserver(moveObserver);
		MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(curvatureSelectionComposite, SWT.None, scannable, true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label lblEllipticity = toolkit.createLabel(curvatureSelectionComposite, ScannableSetup.POLY_Y_ELLIPTICITY.getLabel(), SWT.NONE);
		lblEllipticity.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		scannable = ScannableSetup.POLY_Y_ELLIPTICITY.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(curvatureSelectionComposite, SWT.None, scannable, true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final ToolBar motorSectionTbar = new ToolBar(curvatureSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(motorSectionTbar, SWT.SEPARATOR);
		final ToolItem stopMotorsBarItem = ScannableMotorMoveObserver.setupStopToolItem(motorSectionTbar, movingScannables);
		curvatureSection.setTextClient(motorSectionTbar);
		movingScannables.addListChangeListener(ScannableMotorMoveObserver.getStopButtonListener(curvatureSection, stopMotorsBarItem));
		stopMotorsBarItem.setEnabled(!movingScannables.isEmpty());

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(curvatureSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		curvatureSection.setSeparatorControl(defaultSectionSeparator);
	}

	@SuppressWarnings({ "static-access", "unused" })
	private void createFormSampleSection(Form form) throws Exception {
		final WritableList movingScannables = new WritableList(new ArrayList<Scannable>(), Scannable.class);
		final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);

		final Section samplePositionSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		toolkit.paintBordersFor(samplePositionSection);
		samplePositionSection.setText("Sample position");
		toolkit.paintBordersFor(samplePositionSection);
		samplePositionSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite samplePositionComposite = toolkit.createComposite(samplePositionSection, SWT.NONE);
		toolkit.paintBordersFor(samplePositionComposite);
		samplePositionComposite.setLayout(new GridLayout(2, false));
		samplePositionSection.setClient(samplePositionComposite);

		Label lblSampleZ = toolkit.createLabel(samplePositionComposite, ScannableSetup.SAMPLE_Z_POSITION.getLabel(), SWT.NONE);
		lblSampleZ.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Scannable scannable = ScannableSetup.SAMPLE_Z_POSITION.getScannable();
		scannable.addIObserver(moveObserver);
		MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(samplePositionComposite, SWT.None, scannable, true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final ToolBar motorSectionTbar = new ToolBar(samplePositionSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(motorSectionTbar, SWT.SEPARATOR);
		final ToolItem stopMotorsBarItem = ScannableMotorMoveObserver.setupStopToolItem(motorSectionTbar, movingScannables);
		samplePositionSection.setTextClient(motorSectionTbar);
		movingScannables.addListChangeListener(ScannableMotorMoveObserver.getStopButtonListener(samplePositionSection, stopMotorsBarItem));
		stopMotorsBarItem.setEnabled(!movingScannables.isEmpty());

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(samplePositionSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		samplePositionSection.setSeparatorControl(defaultSectionSeparator);
	}

	@SuppressWarnings("static-access")
	private void createFormSlitsParametersSection(Form form) {
		final Section slitsParametersSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		slitsParametersSection.setText("Slits scan");
		slitsParametersSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite slitsParametersSelectionComposite = toolkit.createComposite(slitsParametersSection, SWT.NONE);
		toolkit.paintBordersFor(slitsParametersSelectionComposite);
		slitsParametersSelectionComposite.setLayout(new GridLayout(2, false));
		slitsParametersSection.setClient(slitsParametersSelectionComposite);
		try{
			Label lbl = toolkit.createLabel(slitsParametersSelectionComposite, ClientConfig.ScannableSetup.SLIT_3_HORIZONAL_GAP.getLabel(), SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			GridData gridDataForTxt = new GridData(SWT.FILL, GridData.CENTER, true, false);

			NumberEditorControl  txtGap = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScanner.getInstance(), SlitScanner.GAP_PROP_NAME, false);
			txtGap.setUnit(ClientConfig.ScannableSetup.SLIT_3_HORIZONAL_GAP.getUnit().getText());
			txtGap.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			txtGap.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "From", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl spnFromOffset = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScanner.getInstance(), SlitScanner.FROM_OFFSET_PROP_NAME, true);
			spnFromOffset.setUnit(UnitSetup.MILLI_METER.getText());
			spnFromOffset.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			spnFromOffset.setIncrement(1 * (int) Math.pow(10, ClientConfig.DEFAULT_DECIMAL_PLACE));
			spnFromOffset.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "To", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl spnToOffset = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScanner.getInstance(), SlitScanner.TO_OFFSET_PROP_NAME, true);
			spnToOffset.setUnit(UnitSetup.MILLI_METER.getText());
			spnToOffset.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			spnToOffset.setIncrement(1 * (int) Math.pow(10, ClientConfig.DEFAULT_DECIMAL_PLACE));
			spnToOffset.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "Step size", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl txtStep = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScanner.getInstance(), SlitScanner.STEP_PROP_NAME, true);
			txtStep.setUnit(UnitSetup.MILLI_METER.getText());
			txtStep.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			txtStep.setIncrement(1 * (int) Math.pow(10, ClientConfig.DEFAULT_DECIMAL_PLACE));
			txtStep.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "Integration time", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl integrationTime = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScanner.getInstance(), SlitScanner.INTEGRATION_TIME_PROP_NAME, true);
			integrationTime.setUnit(UnitSetup.SEC.getText());
			integrationTime.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			integrationTime.setIncrement(1 * (int) Math.pow(10, ClientConfig.DEFAULT_DECIMAL_PLACE));
			integrationTime.setLayoutData(gridDataForTxt);

			Composite scanButtons = toolkit.createComposite(slitsParametersSelectionComposite);
			GridData gridData = new GridData(GridData.HORIZONTAL_ALIGN_FILL);
			gridData.horizontalSpan = 2;
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
		} catch (Exception e) {
			UIHelper.showError("Unable to setup slit scan parameters", e.getMessage());
		}
	}

	@Override
	public void setFocus() {}

}
