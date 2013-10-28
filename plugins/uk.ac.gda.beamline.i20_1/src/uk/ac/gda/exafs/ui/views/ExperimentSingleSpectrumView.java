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
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.sections.SingleSpectrumParametersSection;

public class ExperimentSingleSpectrumView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.experimentSingleSpectrumView";
	private FormToolkit toolkit;
	private ScrolledForm scrolledform;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledform = toolkit.createScrolledForm(parent);
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum");
		Composite formParent = form.getBody();
		try {
			createSamplePosition("I0 sample position", formParent, SingleSpectrumModel.I0_X_POSITION_PROP_NAME, SingleSpectrumModel.I0_Y_POSITION_PROP_NAME);
			createSamplePosition("It sample position", formParent, SingleSpectrumModel.IT_X_POSITION_PROP_NAME, SingleSpectrumModel.IT_Y_POSITION_PROP_NAME);
			SingleSpectrumParametersSection.INSTANCE.createEdeCalibrationSection(form, toolkit);
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
		}
	}

	private void createSamplePosition(String title, Composite body, final String xPostionPropName, final String yPostionPropName) throws Exception {
		@SuppressWarnings("static-access")
		final Section section = toolkit.createSection(body, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		section.setText(title);
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite samplePositionSectionComposite = toolkit.createComposite(section, SWT.NONE);
		samplePositionSectionComposite.setLayout(new GridLayout());
		toolkit.paintBordersFor(samplePositionSectionComposite);
		section.setClient(samplePositionSectionComposite);

		Composite xyPositionComposite = toolkit.createComposite(samplePositionSectionComposite, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		xyPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xyPositionComposite.setLayout(new GridLayout(2, true));

		Composite xPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(xPositionComposite);
		xPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xPositionComposite.setLayout(new GridLayout(2, false));

		Label xPosLabel = toolkit.createLabel(xPositionComposite, "X position", SWT.None);
		xPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final NumberEditorControl xPosition = new NumberEditorControl(xPositionComposite, SWT.None, SingleSpectrumModel.INSTANCE, xPostionPropName, false);
		xPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		xPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(new GridLayout(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "Y position", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final NumberEditorControl yPosition = new NumberEditorControl(yPositionComposite, SWT.None, SingleSpectrumModel.INSTANCE, yPostionPropName, false);
		yPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		yPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		yPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite sampleCustomPositionComposite = toolkit.createComposite(samplePositionSectionComposite, SWT.NONE);
		toolkit.paintBordersFor(sampleCustomPositionComposite);
		sampleCustomPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		sampleCustomPositionComposite.setLayout(new GridLayout(2, false));

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}

	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}

}
