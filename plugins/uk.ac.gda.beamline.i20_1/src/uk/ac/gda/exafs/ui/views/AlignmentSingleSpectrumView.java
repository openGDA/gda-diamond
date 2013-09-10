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
import gda.device.scannable.AlignmentStage;
import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
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

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.composites.ScannableWrapper;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.sections.EDECalibrationSection;
import uk.ac.gda.exafs.ui.sections.SingleSpectrumAcquisitionParametersSection;

public class AlignmentSingleSpectrumView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.alignmentSingleSpectrumView";

	private FormToolkit toolkit;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ScrolledForm scrolledform;

	// Using index 0 for x and 1 for y
	private final Binding[] i0Binding = new Binding[2];
	private final Binding[] itBinding = new Binding[2];

	private Button switchWithSamplePositionButton;

	private Scannable alignmentStageScannable;
	private ScannableWrapper sampleXScannable;
	private ScannableWrapper sampleYScannable;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledform = toolkit.createScrolledForm(parent);
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum / E calibration");
		Composite formParent = form.getBody();
		switchWithSamplePositionButton = toolkit.createButton(form.getHead(), "Use alignment stage for sample positions", SWT.CHECK);
		form.setHeadClient(switchWithSamplePositionButton);
		try {
			setupScannables();
			createSamplePosition("I0 sample position", formParent, i0Binding, AlignmentStageDevice.hole.name(), SingleSpectrumModel.I0_X_POSITION_PROP_NAME, SingleSpectrumModel.I0_Y_POSITION_PROP_NAME);
			createSamplePosition("It sample position", formParent, itBinding, AlignmentStageDevice.foil.name(), SingleSpectrumModel.IT_X_POSITION_PROP_NAME, SingleSpectrumModel.IT_Y_POSITION_PROP_NAME);
			SingleSpectrumAcquisitionParametersSection.INSTANCE.createEdeCalibrationSection(form, toolkit);
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
		}
		EDECalibrationSection.INSTANCE.createEdeCalibrationSection(form, toolkit);
	}

	private void setupScannables() throws Exception {
		alignmentStageScannable = ScannableSetup.ALIGNMENT_STAGE.getScannable();
		sampleXScannable = new ScannableWrapper(ScannableSetup.SAMPLE_X_POSITION.getScannable());
		sampleYScannable = new ScannableWrapper(ScannableSetup.SAMPLE_Y_POSITION.getScannable());
	}

	private void createSamplePosition(String title, Composite body, final Binding[] binding, final String alignmentStageDeviceName, final String xPostionPropName, final String yPostionPropName) throws Exception {
		@SuppressWarnings("static-access")
		final Section section = toolkit.createSection(body, Section.DESCRIPTION | Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
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

		final Button customPositionButton = toolkit.createButton(sampleCustomPositionComposite, "Custom position", SWT.CHECK);
		customPositionButton.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Button customReadPositionButton = toolkit.createButton(sampleCustomPositionComposite, "Read current", SWT.PUSH);
		customReadPositionButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(WidgetProperties.enabled().observe(customReadPositionButton), WidgetProperties.selection().observe(customPositionButton));

		customPositionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				updateBinding(section, binding, customPositionButton, xPosition, yPosition, alignmentStageDeviceName, xPostionPropName, yPostionPropName);
			}
		});
		switchWithSamplePositionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				updateBinding(section, binding, customPositionButton, xPosition, yPosition, alignmentStageDeviceName, xPostionPropName, yPostionPropName);
			}
		});

		updateBinding(section, binding, customPositionButton, xPosition, yPosition, alignmentStageDeviceName, xPostionPropName, yPostionPropName);

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}

	private void updateBinding(Section section, Binding[] binding, Button customPositionButton, NumberEditorControl xPosition, NumberEditorControl yPosition, String alignmentStageDeviceName, String propXName, String propYName) {
		xPosition.setEditable(customPositionButton.getSelection());
		yPosition.setEditable(customPositionButton.getSelection());
		if (binding[0] != null) {
			dataBindingCtx.removeBinding(binding[0]);
			binding[0].dispose();
			binding[0] = null;
		}
		if (binding[1] != null) {
			dataBindingCtx.removeBinding(binding[1]);
			binding[1].dispose();
			binding[1] = null;
		}
		if (!customPositionButton.getSelection()) {
			if (switchWithSamplePositionButton.getSelection()) {
				if (alignmentStageScannable instanceof AlignmentStage) {
					final AlignmentStage alignmentStage = (AlignmentStage) alignmentStageScannable;
					AlignmentStageScannable.Location location = alignmentStage.getAlignmentStageDevice(alignmentStageDeviceName).getLocation();
					if (binding[0] == null) {
						binding[0] = dataBindingCtx.bindValue(
								BeanProperties.value(AlignmentStageScannable.Location.X_POS_PROP_NAME).observe(location),
								BeanProperties.value(propXName).observe(SingleSpectrumModel.INSTANCE),
								new UpdateValueStrategy(),
								new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));
						binding[0].updateTargetToModel();
					}
					if (binding[1] == null) {
						binding[1] = dataBindingCtx.bindValue(
								BeanProperties.value(AlignmentStageScannable.Location.Y_POS_PROP_NAME).observe(location),
								BeanProperties.value(propYName).observe(SingleSpectrumModel.INSTANCE),
								new UpdateValueStrategy(),
								new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));
						binding[1].updateTargetToModel();
					}
					section.setDescription("Using alignment stage " + alignmentStageDeviceName + " as sample x and y position");
				}
			} else {
				if (binding[0] == null) {
					binding[0] = dataBindingCtx.bindValue(
							BeanProperties.value(ScannableWrapper.POSITION_PROP_NAME).observe(sampleXScannable),
							BeanProperties.value(propXName).observe(SingleSpectrumModel.INSTANCE),
							new UpdateValueStrategy(),
							new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));
					binding[0].updateTargetToModel();
				}
				if (binding[1] == null) {
					binding[1] = dataBindingCtx.bindValue(
							BeanProperties.value(ScannableWrapper.POSITION_PROP_NAME).observe(sampleYScannable),
							BeanProperties.value(propYName).observe(SingleSpectrumModel.INSTANCE),
							new UpdateValueStrategy(),
							new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));
					binding[1].updateTargetToModel();
				}
				section.setDescription("Using sample stage position");
			}
		} else {
			section.setDescription("Using custom position");
		}
	}


	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}
}
