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

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;

import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Scannable;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.MotorPositionEditorControl;
import uk.ac.gda.exafs.data.ScannableSetup;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentMotorPostion;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors;
import uk.ac.gda.exafs.ui.data.ScannableMotorMoveObserver;

public class FocusingView extends ViewPart {

	public static String ID = "uk.ac.gda.exafs.ui.views.focusingview";

	private static final Logger logger = LoggerFactory.getLogger(FocusingView.class);

	private FormToolkit toolkit;

	private PropertyChangeListener sampleStageMotorsChangeListener;

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
		//SlitsScanSection slitsScanSection = new SlitsScanSection(form.getBody(), SWT.None);
		//slitsScanSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		DetectorROIsSection detectorROIsSection = new DetectorROIsSection(form.getBody(), SWT.None);
		detectorROIsSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		try {
			createFormSampleSection(form);
			//createFormBendSection(form);
			//createFormCurvatureSection(form);
		} catch (Exception e) {
			UIHelper.showError("Unable to create scannable controls", e.getMessage());
			logger.error("Unable to create scannable controls", e);
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
		MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(bendSelectionComposite, SWT.None, ScannableSetup.POLY_BENDER_1.getScannableWrapper(), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label lblBend2Name = toolkit.createLabel(bendSelectionComposite, ScannableSetup.POLY_BENDER_2.getLabel(), SWT.NONE);
		lblBend2Name.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		scannable = ScannableSetup.POLY_BENDER_2.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(bendSelectionComposite, SWT.None, ScannableSetup.POLY_BENDER_2.getScannableWrapper(), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		ScannableMotorMoveObserver.setupStopToolbarButton(bendSection, movingScannables);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(bendSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		bendSection.setSeparatorControl(defaultSectionSeparator);
	}

	private void createFormCurvatureSection(Form form) throws Exception {
		final WritableList movingScannables = new WritableList(new ArrayList<Scannable>(), Scannable.class);
		final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);
		final Section curvatureSection = toolkit.createSection(form.getBody(), ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
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
		MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(curvatureSelectionComposite, SWT.None, ScannableSetup.POLY_CURVATURE.getScannableWrapper(), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label lblEllipticity = toolkit.createLabel(curvatureSelectionComposite, ScannableSetup.POLY_Y_ELLIPTICITY.getLabel(), SWT.NONE);
		lblEllipticity.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		scannable = ScannableSetup.POLY_Y_ELLIPTICITY.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(curvatureSelectionComposite, SWT.None, ScannableSetup.POLY_Y_ELLIPTICITY.getScannableWrapper(), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label lblTwist = toolkit.createLabel(curvatureSelectionComposite, ScannableSetup.POLY_TWIST.getLabel(), SWT.NONE);
		lblTwist.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		scannable = ScannableSetup.POLY_TWIST.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(curvatureSelectionComposite, SWT.None, ScannableSetup.POLY_TWIST.getScannableWrapper(), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		ScannableMotorMoveObserver.setupStopToolbarButton(curvatureSection, movingScannables);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(curvatureSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		curvatureSection.setSeparatorControl(defaultSectionSeparator);
	}

	private void createFormSampleSection(Form form) throws Exception {
		final WritableList movingScannables = new WritableList(new ArrayList<Scannable>(), Scannable.class);
		final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);

		final Section samplePositionSection = toolkit.createSection(form.getBody(), ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		toolkit.paintBordersFor(samplePositionSection);
		samplePositionSection.setText("Sample position");
		toolkit.paintBordersFor(samplePositionSection);
		samplePositionSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));

		ScannableMotorMoveObserver.setupStopToolbarButton(samplePositionSection, movingScannables);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(samplePositionSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		samplePositionSection.setSeparatorControl(defaultSectionSeparator);

		final Composite samplePositionComposite = toolkit.createComposite(samplePositionSection, SWT.NONE);
		toolkit.paintBordersFor(samplePositionComposite);
		samplePositionComposite.setLayout(new GridLayout(2, false));
		samplePositionSection.setClient(samplePositionComposite);

		sampleStageMotorsChangeListener = new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				try {
					clearSampleStageMotorControls(samplePositionComposite);
					addSampleStageMotorEditors(samplePositionComposite, moveObserver, (ExperimentMotorPostion[]) evt.getNewValue());
					samplePositionSection.layout(true);
					samplePositionSection.getParent().layout(true);
				} catch (Exception e) {
					UIHelper.showError("Unable to add Sample stage motor controls", e.getMessage());
					logger.error("Unable to add Sample stage motor controls", e);
				}
			}
		};
		addSampleStageMotorEditors(samplePositionComposite, moveObserver, (SampleStageMotors.INSTANCE.getSelectedMotors()));
		SampleStageMotors.INSTANCE.addPropertyChangeListener(SampleStageMotors.SELECTED_MOTORS_PROP_NAME, sampleStageMotorsChangeListener);
	}

	public void clearSampleStageMotorControls(final Composite samplePositionComposite) {
		for (Control childWidget :samplePositionComposite.getChildren()) {
			childWidget.dispose();
		}
	}

	private void addSampleStageMotorEditors(Composite parent, ScannableMotorMoveObserver moveObserver, ExperimentMotorPostion[] motors) throws Exception {
		GridData labelGridData = new GridData(GridData.BEGINNING, GridData.CENTER, false, false);
		labelGridData.widthHint = 120;
		GridData controlGridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		for (ExperimentMotorPostion motor : motors) {
			Label label = toolkit.createLabel(parent, motor.getScannableSetup().getLabel(), SWT.NONE);
			label.setLayoutData(labelGridData);
			Scannable scannable = motor.getScannableSetup().getScannable();
			scannable.addIObserver(moveObserver);
			MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(parent, SWT.None,  motor.getScannableSetup().getScannableWrapper(), true);
			motorPositionEditorControl.setLayoutData(controlGridData);
		}
		//TODO take the following out and ensure the for loop above covered Sample_Z motor
		//		Label lblSampleZ = toolkit.createLabel(parent, ScannableSetup.SAMPLE_Z_POSITION.getLabel(), SWT.NONE);
		//		lblSampleZ.setLayoutData(labelGridData);
		//		Scannable scannable = ScannableSetup.SAMPLE_Z_POSITION.getScannable();
		//		scannable.addIObserver(moveObserver);
		//		MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(parent, SWT.None,  ScannableSetup.SAMPLE_Z_POSITION.getScannableWrapper(), true);
		//		motorPositionEditorControl.setLayoutData(controlGridData);
	}

	@Override
	public void dispose() {
		super.dispose();
		SampleStageMotors.INSTANCE.removePropertyChangeListener(SampleStageMotors.SELECTED_MOTORS_PROP_NAME, sampleStageMotorsChangeListener);
	}

	@Override
	public void setFocus() {}
}
