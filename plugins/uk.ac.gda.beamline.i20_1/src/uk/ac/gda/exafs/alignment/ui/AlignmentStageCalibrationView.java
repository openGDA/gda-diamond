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

import gda.device.Scannable;
import gda.device.scannable.AlignmentStage;
import gda.device.scannable.AlignmentStageScannable;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.MotorPositionEditorControl;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.ui.components.NumberEditorControl;

public class AlignmentStageCalibrationView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.alignmentstagecalibration";

	private static final Logger logger = LoggerFactory.getLogger(AlignmentStageCalibrationView.class);

	private FormToolkit toolkit;
	private Form form;

	public AlignmentStageCalibrationView() {}

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		ScrolledForm scrolledform = toolkit.createScrolledForm(parent);
		form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Alignment Stage");
		try {
			createControlsSection();
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}

	@SuppressWarnings("static-access")
	private void createControlsSection() throws Exception {
		final Section section = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		toolkit.paintBordersFor(section);
		section.setText("Calibration");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		sectionComposite.setLayout(new GridLayout());
		section.setClient(sectionComposite);

		Composite composite = createAlignmentStageXY(sectionComposite, ScannableSetup.ALIGNMENT_STAGE_X_POSITION, ScannableSetup.ALIGNMENT_STAGE_Y_POSITION);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Button alignmentStageCalibrationButton = toolkit.createButton(sectionComposite, "Calibrate aligment stage", SWT.None);
		alignmentStageCalibrationButton.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		alignmentStageCalibrationButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				// FIXME Complete implementation
			}
		});

		Composite alignmentStageComposite = toolkit.createComposite(sectionComposite, SWT.None);
		alignmentStageComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		alignmentStageComposite.setLayout(new GridLayout(3, false));

		Scannable scannable = ClientConfig.ScannableSetup.ALIGNMENT_STAGE.getScannable();
		if (scannable instanceof AlignmentStage) {
			AlignmentStage alignmentStage = (AlignmentStage) scannable;

			Label label = toolkit.createLabel(alignmentStageComposite, "X-ray eye", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			composite = createXY(alignmentStageComposite, alignmentStage.getAlignmentStageDevice(
					AlignmentStageScannable.AlignmentStageDevice.eye.name()).getLocation(),
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);
			composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Button moveToXrayEyeButton = toolkit.createButton(alignmentStageComposite, "Move", SWT.None);
			moveToXrayEyeButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));

			label = toolkit.createLabel(alignmentStageComposite, "Slits", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			composite = createXY(alignmentStageComposite, alignmentStage.getAlignmentStageDevice(
					AlignmentStageScannable.AlignmentStageDevice.slits.name()).getLocation(),
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);
			composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Button moveToSlitsButton = toolkit.createButton(alignmentStageComposite, "Move", SWT.None);
			moveToSlitsButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));

			label = toolkit.createLabel(alignmentStageComposite, "Foils", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			composite = createXY(alignmentStageComposite, alignmentStage.getAlignmentStageDevice(
					AlignmentStageScannable.AlignmentStageDevice.foil.name()).getLocation(),
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);
			composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Button moveToFoilsButton = toolkit.createButton(alignmentStageComposite, "Move", SWT.None);
			moveToFoilsButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));

			label = toolkit.createLabel(alignmentStageComposite, "Hole", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			composite = createXY(alignmentStageComposite, alignmentStage.getAlignmentStageDevice(
					AlignmentStageScannable.AlignmentStageDevice.hole.name()).getLocation(),
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);
			composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Button moveToHoleButton = toolkit.createButton(alignmentStageComposite, "Move", SWT.None);
			moveToHoleButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));

			Composite fastShutterComposite = toolkit.createComposite(sectionComposite, SWT.None);
			fastShutterComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
			fastShutterComposite.setLayout(new GridLayout(3, false));

			label = toolkit.createLabel(alignmentStageComposite, "Fast shutter", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			composite = createXY(alignmentStageComposite, alignmentStage.getAlignmentStageDevice(
					AlignmentStageScannable.AlignmentStageDevice.shutter.name()).getLocation(),
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);
			composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Button moveToFastShutterButton = toolkit.createButton(alignmentStageComposite, "Move", SWT.None);
			moveToFastShutterButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));
		}

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}

	private Composite createAlignmentStageXY(Composite parent, ScannableSetup xScannable, ScannableSetup yScannable) throws Exception {
		Composite xyPositionComposite = toolkit.createComposite(parent, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		GridLayout layout = new GridLayout();
		layout.marginHeight = 0;
		layout.marginHeight = 0;
		xyPositionComposite.setLayout(layout);

		Composite xPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(xPositionComposite);
		xPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xPositionComposite.setLayout(new GridLayout(2, false));

		Label xPosLabel = toolkit.createLabel(xPositionComposite, "Alignment stage x", SWT.None);
		xPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		MotorPositionEditorControl xPosition = new MotorPositionEditorControl(xPositionComposite, SWT.None, xScannable.getScannableWrapper(), true);
		xPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		xPosition.setUnit(xScannable.getUnit().getText());
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(new GridLayout(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "Alignment stage y", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		MotorPositionEditorControl yPosition = new MotorPositionEditorControl(yPositionComposite, SWT.None, yScannable.getScannableWrapper(), true);
		yPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		yPosition.setUnit(yScannable.getUnit().getText());
		yPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		return xyPositionComposite;
	}

	private Composite createXY(Composite parent, ObservableModel model, String xPropertyName, String yPropertyName) throws Exception {
		Composite xyPositionComposite = toolkit.createComposite(parent, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		GridLayout layout = new GridLayout(2, true);
		layout.marginHeight = 0;
		layout.marginHeight = 0;
		xyPositionComposite.setLayout(layout);

		Composite xPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(xPositionComposite);
		xPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xPositionComposite.setLayout(new GridLayout(2, false));

		Label xPosLabel = toolkit.createLabel(xPositionComposite, "x", SWT.None);
		xPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl xPosition = new NumberEditorControl(xPositionComposite, SWT.None, model, xPropertyName, false);
		xPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		xPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(new GridLayout(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "y", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl yPosition = new NumberEditorControl(yPositionComposite, SWT.None, model, yPropertyName, false);
		yPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		yPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		yPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		return xyPositionComposite;
	}



	@Override
	public void setFocus() {
		form.setFocus();
	}

}
