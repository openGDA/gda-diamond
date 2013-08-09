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

import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.exafs.data.ObservableModel;
import uk.ac.gda.exafs.ui.composites.MotorPositionEditorControl;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.AlignmentStageModel;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class AlignmentStageClaibrationView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.alignmentstagecalibration";
	private FormToolkit toolkit;
	private Form form;

	public AlignmentStageClaibrationView() {}

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
		sectionComposite.setLayout(new GridLayout(3, false));
		section.setClient(sectionComposite);

		Label label = toolkit.createLabel(sectionComposite, "Alignment stage", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Composite composite = createXY(sectionComposite, ScannableSetup.ALIGNMENT_STAGE_X_POSITION, ScannableSetup.ALIGNMENT_STAGE_Y_POSITION);
		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		composite.setLayoutData(gridData);


		Button alignmentStageCalibrationButton = toolkit.createButton(sectionComposite, "Calibrate aligment stage", SWT.None);
		gridData = new GridData(SWT.FILL, SWT.BEGINNING, true, false);
		gridData.horizontalSpan = 3;
		alignmentStageCalibrationButton.setLayoutData(gridData);
		alignmentStageCalibrationButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				// TODO
			}
		});

		label = toolkit.createLabel(sectionComposite, "X-ray eye", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		composite = createXY(sectionComposite, AlignmentStageModel.INSTANCE, AlignmentStageModel.X_X_EYE_PROP_NAME, AlignmentStageModel.Y_X_EYE_PROP_NAME);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Button moveToXrayEyeButton = toolkit.createButton(sectionComposite, "Move", SWT.None);
		moveToXrayEyeButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));

		label = toolkit.createLabel(sectionComposite, "Slits", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		composite = createXY(sectionComposite, AlignmentStageModel.INSTANCE, AlignmentStageModel.X_SLITS_PROP_NAME, AlignmentStageModel.Y_SLITS_PROP_NAME);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Button moveToSlitsButton = toolkit.createButton(sectionComposite, "Move", SWT.None);
		moveToSlitsButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));

		label = toolkit.createLabel(sectionComposite, "Foils", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		composite = createXY(sectionComposite, AlignmentStageModel.INSTANCE, AlignmentStageModel.X_FOILS_PROP_NAME, AlignmentStageModel.Y_FOILS_PROP_NAME);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Button moveToFoilsButton = toolkit.createButton(sectionComposite, "Move", SWT.None);
		moveToFoilsButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));

		label = toolkit.createLabel(sectionComposite, "Hole", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		composite = createXY(sectionComposite, AlignmentStageModel.INSTANCE, AlignmentStageModel.X_HOLE_PROP_NAME, AlignmentStageModel.Y_HOLE_PROP_NAME);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Button moveToHoleButton = toolkit.createButton(sectionComposite, "Move", SWT.None);
		moveToHoleButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));

		label = toolkit.createLabel(sectionComposite, "Fast shutter", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		composite = createXY(sectionComposite, AlignmentStageModel.INSTANCE, AlignmentStageModel.X_SHUTTER_PROP_NAME, AlignmentStageModel.Y_SHUTTER_PROP_NAME);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Button moveToFastShutterButton = toolkit.createButton(sectionComposite, "Move", SWT.None);
		moveToFastShutterButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);


	}

	private Composite createXY(Composite parent, ScannableSetup xScannable, ScannableSetup yScannable) throws Exception {
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

		Label xPosLabel = toolkit.createLabel(xPositionComposite, "X", SWT.None);
		xPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		MotorPositionEditorControl xPosition = new MotorPositionEditorControl(xPositionComposite, SWT.None, xScannable.getScannable(), true);
		xPosition.setUnit(xScannable.getUnit().getText());
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(new GridLayout(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "Y", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		MotorPositionEditorControl yPosition = new MotorPositionEditorControl(yPositionComposite, SWT.None, yScannable.getScannable(), true);
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

		Label xPosLabel = toolkit.createLabel(xPositionComposite, "X", SWT.None);
		xPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl xPosition = new NumberEditorControl(xPositionComposite, SWT.None, model, xPropertyName, true);
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(new GridLayout(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "Y", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl yPosition = new NumberEditorControl(yPositionComposite, SWT.None, model, yPropertyName, true);
		yPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		return xyPositionComposite;
	}



	@Override
	public void setFocus() {
		form.setFocus();
	}

}
