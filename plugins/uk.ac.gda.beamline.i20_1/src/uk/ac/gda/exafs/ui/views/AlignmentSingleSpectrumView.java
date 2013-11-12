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

import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;
import gda.device.scannable.AlignmentStageScannable.Location;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.SingleSpectrumUIModel;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentMotorPostion;
import uk.ac.gda.exafs.ui.data.experiment.SampleStageMotorSelectionComposite;
import uk.ac.gda.exafs.ui.data.experiment.SampleStageMotors;
import uk.ac.gda.exafs.ui.sections.EDECalibrationSection;
import uk.ac.gda.exafs.ui.sections.SingleSpectrumParametersSection;

public class AlignmentSingleSpectrumView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.alignmentSingleSpectrumView";

	private static final Logger logger = LoggerFactory.getLogger(AlignmentSingleSpectrumView.class);

	private FormToolkit toolkit;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ScrolledForm scrolledform;

	private Button switchWithSamplePositionButton;

	private Composite sampleStageMotorsComposite;

	private Binding stageSelectionButtonBinding;

	private Composite sampleStateMotorselectionComposite;

	private Form form;

	private Binding sampleStageI0CompositeBinding;

	private Composite sampleI0PositionComposite;

	private Composite alignmentI0PositionComposite;

	private Binding alignmentStageI0CompositeBinding;

	private PropertyChangeListener selectionChangeListener;

	private Binding sampleStageItCompositeBinding;

	private Binding alignmentStageItCompositeBinding;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledform = toolkit.createScrolledForm(parent);
		form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum / E calibration");
		Composite formParent = form.getBody();
		final Composite stageSelectionComposite = toolkit.createComposite(form.getHead());
		stageSelectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		switchWithSamplePositionButton = toolkit.createButton(stageSelectionComposite, "Use alignment stage for sample positions", SWT.CHECK);
		GridData gridData = new GridData(SWT.FILL, SWT.BEGINNING, true, false);
		gridData.horizontalSpan = 2;
		switchWithSamplePositionButton.setLayoutData(gridData);
		sampleStateMotorselectionComposite = toolkit.createComposite(stageSelectionComposite);
		sampleStateMotorselectionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		sampleStateMotorselectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		Label sampleStageMotorsLabel = toolkit.createLabel(sampleStateMotorselectionComposite, "Sample stage motors");
		sampleStageMotorsLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		sampleStageMotorsComposite = new SampleStageMotorSelectionComposite(sampleStateMotorselectionComposite, SWT.BORDER, SingleSpectrumUIModel.INSTANCE.getSampleStageMotors());
		sampleStageMotorsComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		stageSelectionComposite.layout();
		form.setHeadClient(stageSelectionComposite);

		try {
			createSampleI0Position(formParent);
			createSampleItPosition(formParent);
			setupScannables();
			SingleSpectrumParametersSection.INSTANCE.createEdeCalibrationSection(form, toolkit);
			EDECalibrationSection.INSTANCE.createEdeCalibrationSection(form, toolkit);
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}


	private void setupScannables() {
		stageSelectionButtonBinding = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(switchWithSamplePositionButton),
				WidgetProperties.visible().observe(sampleStateMotorselectionComposite),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus status = super.doSet(observableValue, !((boolean) value));
						((GridData) sampleStateMotorselectionComposite.getLayoutData()).exclude = ((boolean) value);
						form.layout();
						return status;
					}
				},
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));
		stageSelectionButtonBinding.updateTargetToModel();

		sampleStageI0CompositeBinding = dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(sampleI0PositionComposite),
				BeanProperties.value(SingleSpectrumUIModel.ALIGNMENT_STAGE_SELECTION).observe(SingleSpectrumUIModel.INSTANCE),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus status = super.doSet(observableValue, !((boolean) value));
						((GridData) sampleI0PositionComposite.getLayoutData()).exclude = ((boolean) value);
						form.layout();
						return status;
					}
				});

		alignmentStageI0CompositeBinding = dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(alignmentI0PositionComposite),
				BeanProperties.value(SingleSpectrumUIModel.ALIGNMENT_STAGE_SELECTION).observe(SingleSpectrumUIModel.INSTANCE),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus status = super.doSet(observableValue, ((boolean) value));
						((GridData) alignmentI0PositionComposite.getLayoutData()).exclude = !((boolean) value);
						form.layout();
						return status;
					}
				});

		sampleStageItCompositeBinding = dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(sampleItPositionComposite),
				BeanProperties.value(SingleSpectrumUIModel.ALIGNMENT_STAGE_SELECTION).observe(SingleSpectrumUIModel.INSTANCE),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus status = super.doSet(observableValue, !((boolean) value));
						((GridData) sampleItPositionComposite.getLayoutData()).exclude = ((boolean) value);
						form.layout();
						return status;
					}
				});

		alignmentStageItCompositeBinding = dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(alignmentItPositionComposite),
				BeanProperties.value(SingleSpectrumUIModel.ALIGNMENT_STAGE_SELECTION).observe(SingleSpectrumUIModel.INSTANCE),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus status = super.doSet(observableValue, ((boolean) value));
						((GridData) alignmentItPositionComposite.getLayoutData()).exclude = !((boolean) value);
						form.layout();
						return status;
					}
				});
		dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(switchWithSamplePositionButton),
				BeanProperties.value(SingleSpectrumUIModel.ALIGNMENT_STAGE_SELECTION).observe(SingleSpectrumUIModel.INSTANCE));

		selectionChangeListener = new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				selectionSampleStageMotorListChange();
			}
		};
		selectionSampleStageMotorListChange();
		SingleSpectrumUIModel.INSTANCE.getSampleStageMotors().addPropertyChangeListener(SampleStageMotors.SELECTED_MOTORS, selectionChangeListener);
	}

	private final List<Composite> sampleStageMotorComposites = new ArrayList<Composite>();

	private Composite sampleItPositionComposite;

	private Composite alignmentItPositionComposite;
	private void selectionSampleStageMotorListChange() {
		for (Composite composite : sampleStageMotorComposites) {
			composite.dispose();
		}
		sampleStageMotorComposites.clear();
		try {
			for(final ExperimentMotorPostion experimentMotorPostion : SingleSpectrumUIModel.INSTANCE.getSampleStageMotors().getSelectedMotors()) {
				Composite composite = createXYPositionComposite(sampleI0PositionComposite, experimentMotorPostion,
						ExperimentMotorPostion.TARGET_I0_POSITION,
						experimentMotorPostion.getScannableSetup().getLabel(), new Listener() {
					@Override
					public void handleEvent(Event event) {
						try {
							experimentMotorPostion.setTargetI0Position((double) experimentMotorPostion.getScannableSetup().getScannable().getPosition());
						} catch (Exception e) {
							UIHelper.showError("Unable to update current motor postion", e.getMessage());
							logger.error("Unable to update current motor postion", e.getMessage());
						}
					}
				});
				sampleStageMotorComposites.add(composite);
				composite = createXYPositionComposite(sampleItPositionComposite, experimentMotorPostion,
						ExperimentMotorPostion.TARGET_IT_POSITION,
						experimentMotorPostion.getScannableSetup().getLabel(), new Listener() {
					@Override
					public void handleEvent(Event event) {
						try {
							experimentMotorPostion.setTargetItPosition((double) experimentMotorPostion.getScannableSetup().getScannable().getPosition());
						} catch (Exception e) {
							UIHelper.showError("Unable to update current motor postion", e.getMessage());
							logger.error("Unable to update current motor postion", e.getMessage());
						}
					}
				});
				sampleStageMotorComposites.add(composite);
			}
			form.layout();
		} catch (Exception e) {
			UIHelper.showError("Unable to update selected motor positions", e.getMessage());
			logger.error("Unable to update selected motor positions", e);
		}
	}

	private Listener createXPositionListener(final Location location, final AlignmentStageDevice alignmentStageDevice) {
		return new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					location.setxPosition(alignmentStageDevice.getLocation().getxPosition());
				} catch (Exception e) {
					UIHelper.showError("Unable to update current motor postion", e.getMessage());
					logger.error("Unable to update current motor postion", e.getMessage());
				}
			}
		};
	}

	private Listener createYPositionListener(final Location location, final AlignmentStageDevice alignmentStageDevice) {
		return new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					location.setyPosition(alignmentStageDevice.getLocation().getyPosition());
				} catch (Exception e) {
					UIHelper.showError("Unable to update current motor postion", e.getMessage());
					logger.error("Unable to update current motor postion", e.getMessage());
				}
			}
		};
	}

	private void createSampleI0Position(Composite body) throws Exception {
		@SuppressWarnings("static-access")
		final Section section = toolkit.createSection(body, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		section.setText("I0 sample position");
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite sampleI0PositionSectionComposite = toolkit.createComposite(section, SWT.NONE);
		sampleI0PositionSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sampleI0PositionSectionComposite);
		section.setClient(sampleI0PositionSectionComposite);
		sampleI0PositionComposite = toolkit.createComposite(sampleI0PositionSectionComposite, SWT.NONE);
		sampleI0PositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		sampleI0PositionComposite.setLayout(new GridLayout());

		alignmentI0PositionComposite = toolkit.createComposite(sampleI0PositionSectionComposite, SWT.NONE);
		alignmentI0PositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		alignmentI0PositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		createXYPositionComposite(
				alignmentI0PositionComposite,
				SingleSpectrumUIModel.INSTANCE.getHoleLocationForAlignment(),
				AlignmentStageScannable.Location.X_POS_PROP_NAME,
				"Hole X position", createXPositionListener(SingleSpectrumUIModel.INSTANCE.getHoleLocationForAlignment(), AlignmentStageDevice.hole)
				);
		createXYPositionComposite(
				alignmentI0PositionComposite,
				SingleSpectrumUIModel.INSTANCE.getHoleLocationForAlignment(),
				AlignmentStageScannable.Location.Y_POS_PROP_NAME,
				"Hole Y position", createYPositionListener(SingleSpectrumUIModel.INSTANCE.getHoleLocationForAlignment(), AlignmentStageDevice.hole));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(defaultSectionSeparator);
		section.setSeparatorControl(defaultSectionSeparator);
	}

	private void createSampleItPosition(Composite body) throws Exception {
		@SuppressWarnings("static-access")
		final Section section = toolkit.createSection(body, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		section.setText("It sample position");
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite sampleI0PositionSectionComposite = toolkit.createComposite(section, SWT.NONE);
		sampleI0PositionSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sampleI0PositionSectionComposite);
		section.setClient(sampleI0PositionSectionComposite);
		sampleItPositionComposite = toolkit.createComposite(sampleI0PositionSectionComposite, SWT.NONE);
		sampleItPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		sampleItPositionComposite.setLayout(new GridLayout());

		// TODO How to move?
		alignmentItPositionComposite = toolkit.createComposite(sampleI0PositionSectionComposite, SWT.NONE);
		alignmentItPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		alignmentItPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		createXYPositionComposite(alignmentItPositionComposite, SingleSpectrumUIModel.INSTANCE.getFoilLocationForAlignment(),
				AlignmentStageScannable.Location.X_POS_PROP_NAME,
				"Foil X position", createXPositionListener(SingleSpectrumUIModel.INSTANCE.getFoilLocationForAlignment(), AlignmentStageDevice.foil));
		createXYPositionComposite(alignmentItPositionComposite, SingleSpectrumUIModel.INSTANCE.getFoilLocationForAlignment(),
				AlignmentStageScannable.Location.Y_POS_PROP_NAME,
				"Foil Y position", createYPositionListener(SingleSpectrumUIModel.INSTANCE.getFoilLocationForAlignment(), AlignmentStageDevice.foil));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(defaultSectionSeparator);
		section.setSeparatorControl(defaultSectionSeparator);
	}

	private Composite createXYPositionComposite(Composite parent, Object object, String propertyName, String label, Listener listener) throws Exception {
		Composite positionAllComposite = toolkit.createComposite(parent, SWT.NONE);
		toolkit.paintBordersFor(positionAllComposite);
		positionAllComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		int columns = (listener != null) ? 2 : 1;
		positionAllComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(columns, false));

		Composite positionComposite = toolkit.createComposite(positionAllComposite, SWT.NONE);
		toolkit.paintBordersFor(positionComposite);
		positionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		positionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		Label xPosLabel = toolkit.createLabel(positionComposite, label, SWT.None);
		GridData gridData = new GridData(SWT.BEGINNING, SWT.CENTER, false, false);
		gridData.widthHint = 130;
		xPosLabel.setLayoutData(gridData);

		final NumberEditorControl positionControl = new NumberEditorControl(positionComposite, SWT.None, object, propertyName, false);
		positionControl.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		positionControl.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		positionControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		if (listener != null) {
			Button readCurrentPositionButton = toolkit.createButton(positionAllComposite, "Read current", SWT.PUSH);
			readCurrentPositionButton.addListener(SWT.Selection, listener);
			readCurrentPositionButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, true, false));
		}
		return positionAllComposite;
	}


	@Override
	public void dispose() {
		dataBindingCtx.removeBinding(stageSelectionButtonBinding);
		stageSelectionButtonBinding.dispose();
		dataBindingCtx.removeBinding(sampleStageI0CompositeBinding);
		sampleStageI0CompositeBinding.dispose();
		dataBindingCtx.removeBinding(alignmentStageI0CompositeBinding);
		alignmentStageI0CompositeBinding.dispose();
		dataBindingCtx.removeBinding(sampleStageItCompositeBinding);
		sampleStageItCompositeBinding.dispose();
		dataBindingCtx.removeBinding(alignmentStageItCompositeBinding);
		alignmentStageItCompositeBinding.dispose();
		SingleSpectrumUIModel.INSTANCE.getSampleStageMotors().removePropertyChangeListener(SampleStageMotors.SELECTED_MOTORS, selectionChangeListener);
		super.dispose();
	}

	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}
}
