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

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;
import gda.device.scannable.AlignmentStageScannable.Location;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.calibration.ui.EDECalibrationSection;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.SingleSpectrumCollectionModel;
import uk.ac.gda.exafs.experiment.ui.SingleSpectrumCollectionView;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;
import uk.ac.gda.ui.components.NumberEditorControl;

public class SingleSpectrumAlignmentView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.alignmentSingleSpectrumView";

	private static final Logger logger = LoggerFactory.getLogger(SingleSpectrumAlignmentView.class);

	private FormToolkit toolkit;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ScrolledForm scrolledform;

	private Button switchWithSamplePositionButton;

	private Form form;

	private Composite alignmentStageSectionsParent;
	private Composite sampleStageSectionsParent;

	private Binding alignmentStageCompositeBinding;
	private Binding sampleStageCompositeBinding;

	private Binding switchWithSamplePositionButtonBinding;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());

		final SashForm parentComposite = new SashForm(parent, SWT.VERTICAL);
		parentComposite.SASH_WIDTH = 7;

		Composite composite = new Composite(parentComposite, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1,false));

		scrolledform = toolkit.createScrolledForm(composite);
		scrolledform.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		form = scrolledform.getForm();
		form.getBody().setLayout(new GridLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum / E calibration");
		Composite formParent = form.getBody();

		try {
			createSampleStageSections(formParent);
			createAlignmentSections(formParent);
			setupScannables();
			SingleSpectrumParametersSection singleSpectrumParametersSection = new SingleSpectrumParametersSection(formParent, SWT.None);
			singleSpectrumParametersSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
			createSampleDetailsSection(formParent);
			EDECalibrationSection eDECalibrationSection = new EDECalibrationSection(formParent, SWT.None);
			eDECalibrationSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
			SingleSpectrumCollectionView.createStartStopScanSection(parentComposite, toolkit, null, null);
			form.layout();
			parentComposite.setWeights(new int[] {7, 3});
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}

	private void createSampleDetailsSection(Composite formParent) {
		final Section sampleDetailsSection = toolkit.createSection(formParent, ExpandableComposite.NO_TITLE);
		sampleDetailsSection.setText("File");
		sampleDetailsSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sectionComposite = toolkit.createComposite(sampleDetailsSection, SWT.NONE);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		toolkit.paintBordersFor(sectionComposite);
		sampleDetailsSection.setClient(sectionComposite);

		Label fileNameLabel = toolkit.createLabel(sectionComposite, "File name: ");
		fileNameLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		Text fileNameText = toolkit.createText(sectionComposite, "", SWT.BORDER);
		fileNameText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		fileNameText.setEditable(false);

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(fileNameText),
				BeanProperties.value(SingleSpectrumCollectionModel.FILE_NAME_PROP_NAME).observe(ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						if (value != null) {
							return value;
						}
						return "";
					}
				});
	}

	private void setupScannables() {
		sampleStageCompositeBinding = dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(sampleStageSectionsParent),
				BeanProperties.value(SingleSpectrumCollectionModel.ALIGNMENT_STAGE_SELECTION).observe(ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus status = super.doSet(observableValue, !((boolean) value));
						((GridData) sampleStageSectionsParent.getLayoutData()).exclude = ((boolean) value);
						form.layout();
						return status;
					}
				});

		alignmentStageCompositeBinding = dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(alignmentStageSectionsParent),
				BeanProperties.value(SingleSpectrumCollectionModel.ALIGNMENT_STAGE_SELECTION).observe(ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus status = super.doSet(observableValue, ((boolean) value));
						((GridData) alignmentStageSectionsParent.getLayoutData()).exclude = !((boolean) value);
						form.layout();
						return status;
					}
				});

		switchWithSamplePositionButtonBinding = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(switchWithSamplePositionButton),
				BeanProperties.value(SingleSpectrumCollectionModel.ALIGNMENT_STAGE_SELECTION).observe(ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel()));

	}

	@SuppressWarnings("static-access")
	private void createAlignmentSections(Composite body) throws Exception {
		SingleSpectrumCollectionModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();
		alignmentStageSectionsParent = toolkit.createComposite(body);
		alignmentStageSectionsParent.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		alignmentStageSectionsParent.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		final Section i0Section = toolkit.createSection(alignmentStageSectionsParent, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		i0Section.setText("I0 sample position");
		i0Section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sampleI0PositionSectionComposite = toolkit.createComposite(i0Section, SWT.NONE);
		sampleI0PositionSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sampleI0PositionSectionComposite);
		i0Section.setClient(sampleI0PositionSectionComposite);

		Composite alignmentI0PositionComposite = toolkit.createComposite(sampleI0PositionSectionComposite, SWT.NONE);
		alignmentI0PositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		alignmentI0PositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		createXYPositionComposite(
				alignmentI0PositionComposite,
				singleSpectrumDataModel.getHoleLocationForAlignment(),
				AlignmentStageScannable.Location.X_POS_PROP_NAME,
				"Hole X position", createXPositionListener(singleSpectrumDataModel.getHoleLocationForAlignment(), AlignmentStageDevice.hole)
				);
		createXYPositionComposite(
				alignmentI0PositionComposite,
				singleSpectrumDataModel.getHoleLocationForAlignment(),
				AlignmentStageScannable.Location.Y_POS_PROP_NAME,
				"Hole Y position", createYPositionListener(singleSpectrumDataModel.getHoleLocationForAlignment(), AlignmentStageDevice.hole));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(i0Section);
		toolkit.paintBordersFor(defaultSectionSeparator);
		i0Section.setSeparatorControl(defaultSectionSeparator);

		final Section itSection = toolkit.createSection(alignmentStageSectionsParent, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		itSection.setText("It sample position");
		itSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sampleItPositionSectionComposite = toolkit.createComposite(itSection, SWT.NONE);
		sampleItPositionSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sampleItPositionSectionComposite);
		itSection.setClient(sampleItPositionSectionComposite);

		Composite alignmentItPositionComposite = toolkit.createComposite(sampleItPositionSectionComposite, SWT.NONE);
		alignmentItPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		alignmentItPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		createXYPositionComposite(alignmentItPositionComposite, singleSpectrumDataModel.getFoilLocationForAlignment(),
				AlignmentStageScannable.Location.X_POS_PROP_NAME,
				"Foil X position", createXPositionListener(singleSpectrumDataModel.getFoilLocationForAlignment(), AlignmentStageDevice.foil));
		createXYPositionComposite(alignmentItPositionComposite, singleSpectrumDataModel.getFoilLocationForAlignment(),
				AlignmentStageScannable.Location.Y_POS_PROP_NAME,
				"Foil Y position", createYPositionListener(singleSpectrumDataModel.getFoilLocationForAlignment(), AlignmentStageDevice.foil));

		defaultSectionSeparator = toolkit.createCompositeSeparator(itSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		itSection.setSeparatorControl(defaultSectionSeparator);
	}

	private void createSampleStageSections(Composite body) {
		final Composite stageSelectionComposite = toolkit.createComposite(body);
		stageSelectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		switchWithSamplePositionButton = toolkit.createButton(stageSelectionComposite, "Use alignment stage for sample positions", SWT.CHECK);
		switchWithSamplePositionButton.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		sampleStageSectionsParent = new SampleStageMotorsComposite(body, SWT.None, toolkit, true);
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

	@Override
	public void dispose() {
		dataBindingCtx.removeBinding(sampleStageCompositeBinding);
		sampleStageCompositeBinding.dispose();
		dataBindingCtx.removeBinding(alignmentStageCompositeBinding);
		alignmentStageCompositeBinding.dispose();
		dataBindingCtx.removeBinding(switchWithSamplePositionButtonBinding);
		switchWithSamplePositionButtonBinding.dispose();
		super.dispose();
	}

	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}
}
