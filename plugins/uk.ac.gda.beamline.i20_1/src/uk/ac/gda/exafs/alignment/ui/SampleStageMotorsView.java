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
import uk.ac.gda.exafs.experiment.ui.data.ExperimentMotorPostion;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors;
import uk.ac.gda.exafs.ui.data.ScannableMotorMoveObserver;

public class SampleStageMotorsView extends ViewPart {

	public static String ID = "uk.ac.gda.exafs.ui.views.samplestagemotors";

	private static final Logger logger = LoggerFactory.getLogger(SampleStageMotorsView.class);

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
		form.setText("Sample Stage Motors");
		try {
			createFormSampleSection(form);
		} catch (Exception e) {
			UIHelper.showError("Unable to create scannable controls", e.getMessage());
			logger.error("Unable to create scannable controls", e);
		}
		return scrolledform;
	}

	private void createFormSampleSection(Form form) throws Exception {
		final WritableList<Scannable> movingScannables = new WritableList<>(new ArrayList<>(), Scannable.class);
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

		sampleStageMotorsChangeListener = evt -> {
			try {
				clearSampleStageMotorControls(samplePositionComposite);
				addSampleStageMotorEditors(samplePositionComposite, moveObserver, (ExperimentMotorPostion[]) evt.getNewValue());
				samplePositionSection.layout(true);
				samplePositionSection.getParent().layout(true);
			} catch (Exception e) {
				UIHelper.showError("Unable to add Sample stage motor controls", e.getMessage());
				logger.error("Unable to add Sample stage motor controls", e);
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
	}

	@Override
	public void dispose() {
		super.dispose();
		SampleStageMotors.INSTANCE.removePropertyChangeListener(SampleStageMotors.SELECTED_MOTORS_PROP_NAME, sampleStageMotorsChangeListener);
	}

	@Override
	public void setFocus() {}
}
