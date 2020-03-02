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

import java.util.Arrays;
import java.util.List;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.detector.frelon.FrelonCcdDetectorData;
import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumCollectionModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentDataModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors;
import uk.ac.gda.exafs.experiment.ui.data.TimingGroupUIModel;
import uk.ac.gda.ui.components.NumberEditorControl;

public class SingleSpectrumParametersSection extends ResourceComposite {

	private static final int BOX_WIDTH = 250;

	private final FormToolkit toolkit;

	private static final Logger logger = LoggerFactory.getLogger(SingleSpectrumParametersSection.class);

	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private Section section;

	private Section sectionIRefaccumulationSection;

	private NumberEditorControl iRefIntegrationTimeValueText;

	private NumberEditorControl iRefNoOfAccumulationValueText;

	private NumberEditorControl i0NoOfAccumulationValueText;

	private Button i0NoOfAccumulationCheck;

	protected Binding binding;

	private Label lnoOfAcculabel;

	private boolean showAccumulationReadout = false;

	private Text accumulationReadoutTimeValueText;

	private Text realTimePerSpectrumValueText;

	private final SingleSpectrumCollectionModel singleSpectrumDataModel;

	public SingleSpectrumParametersSection(Composite parent, int style, SingleSpectrumCollectionModel singleSpectrumDataModel) {
		super(parent, style);
		this.singleSpectrumDataModel = singleSpectrumDataModel;
		toolkit = new FormToolkit(parent.getDisplay());
		try {
			showAccumulationReadout = DetectorModel.INSTANCE.getCurrentDetector().getDetectorData() instanceof FrelonCcdDetectorData;
			setupUI();
			bind();
		} catch (Exception e) {
			logger.error("Unable to create controls", e);
		}
	}

	public SingleSpectrumParametersSection(Composite parent, int style) {
		this(parent, style, ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel());
	}

	private void updateAccumulationWidgets() {
		String formatStr = "%.5f %s"; // value, unit

		if (accumulationReadoutTimeValueText == null && realTimePerSpectrumValueText == null) {
			return;
		}

		double accumationReadoutTime = DetectorModel.INSTANCE.getAccumulationReadoutTime();
		double accumulationReadoutTimeMs = ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(accumationReadoutTime, ExperimentUnit.MILLI_SEC);
		double realTimePerSpectrumMs = singleSpectrumDataModel.getItNumberOfAccumulations()*(singleSpectrumDataModel.getItIntegrationTime() + accumulationReadoutTimeMs);

		accumulationReadoutTimeValueText.setText(String.format(formatStr, accumulationReadoutTimeMs, "ms"));
		realTimePerSpectrumValueText.setText(String.format(formatStr, realTimePerSpectrumMs, "ms"));
	}



	private void bind() {

		Binding i0NoOfAccumulationCheckBinding = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(i0NoOfAccumulationCheck),
				BeanProperties.value(ExperimentDataModel.USE_NO_OF_ACCUMULATIONS_FOR_I0_PROP_NAME).observe(singleSpectrumDataModel.getExperimentDataModel()),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus result = super.doSet(observableValue, value);
						// Same number of I0 and It accumulations is handled when setting up SingleSpectrum scan command, so binding here is redundant
						// (and also behaving incorrectly now for some reason)... imh 7/12/2015
						// updateI0noOfAccuBinding(singleSpectrumDataModel, value);
						return result;
					}
				},
				new UpdateValueStrategy());
		i0NoOfAccumulationCheckBinding.updateTargetToModel();

		dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(lnoOfAcculabel),
				BeanProperties.value(ExperimentDataModel.USE_NO_OF_ACCUMULATIONS_FOR_I0_PROP_NAME).observe(singleSpectrumDataModel.getExperimentDataModel()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy());

		dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(i0NoOfAccumulationValueText),
				BeanProperties.value(ExperimentDataModel.USE_NO_OF_ACCUMULATIONS_FOR_I0_PROP_NAME).observe(singleSpectrumDataModel.getExperimentDataModel()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy());

		dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(sectionIRefaccumulationSection),
				BeanProperties.value(SampleStageMotors.USE_IREF_PROP_NAME).observe(SampleStageMotors.INSTANCE),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus result = super.doSet(observableValue, value);
						boolean useIRef = (boolean) value;
						((GridData) sectionIRefaccumulationSection.getLayoutData()).exclude = !useIRef;
						((GridData) sectionIRefaccumulationSection.getLayoutData()).exclude = !((boolean) value);
						((GridLayout) sectionIRefaccumulationSection.getParent().getLayout()).numColumns = useIRef ? 2 : 1;
						UIHelper.revalidateLayout(sectionIRefaccumulationSection.getParent());
						return result;
					}
				});

		updateAccumulationWidgets();

		// Update when accumulation readout time changes
		DetectorModel.INSTANCE.addPropertyChangeListener( event -> {
			if (event.getPropertyName().equals(TimingGroupUIModel.ACCUMULATION_READOUT_TIME_PROP_NAME)) {
				updateAccumulationWidgets();
			}
		});

		// Update when number of accumulations or accumulation time change
		singleSpectrumDataModel.addPropertyChangeListener( event -> {
			List<String> updateEvents = Arrays.asList(SingleSpectrumCollectionModel.IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME,
					SingleSpectrumCollectionModel.IT_INTEGRATION_TIME_PROP_NAME);
			if (updateEvents.contains(event.getPropertyName())) {
				updateAccumulationWidgets();
			}
		});
	}

	private void createI0IRefComposites() throws Exception {

		// I0 and IRef accumulation times
		Composite composite = toolkit.createComposite(this);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));

		// I0
		Section i0AcquisitionSection = toolkit.createSection(composite, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		i0AcquisitionSection.setText("I0 acquisition settings");
		i0AcquisitionSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		final Composite i0AcquisitionSectionComposite = toolkit.createComposite(i0AcquisitionSection, SWT.NONE);
		i0AcquisitionSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		i0AcquisitionSection.setClient(i0AcquisitionSectionComposite);

		i0NoOfAccumulationCheck = toolkit.createButton(i0AcquisitionSectionComposite, "Set I0 number of accumulations", SWT.CHECK);
		GridData gridData = new GridData(SWT.LEFT, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		i0NoOfAccumulationCheck.setLayoutData(gridData);

		gridData = new GridData(SWT.FILL, SWT.CENTER, false, false);
		gridData.widthHint = BOX_WIDTH;
		GridDataFactory fixedWidthGridData = GridDataFactory.createFrom(gridData);

		Composite i0Composite = new Composite(i0AcquisitionSectionComposite,  SWT.None);
		i0Composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, false, false));
		i0Composite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		Label label = toolkit.createLabel(i0Composite, "Accumulation time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		NumberEditorControl i0IntegrationTimeValueText = new NumberEditorControl(i0Composite, SWT.None, singleSpectrumDataModel.getExperimentDataModel(), ExperimentDataModel.I0_INTEGRATION_TIME_PROP_NAME, true);
		fixedWidthGridData.applyTo(i0IntegrationTimeValueText);

		i0IntegrationTimeValueText.setLayoutData(gridData);
		i0IntegrationTimeValueText.setUnit(DetectorModel.INSTANCE.getUnitForAccumulationTime().getUnitText());
		i0IntegrationTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		lnoOfAcculabel = toolkit.createLabel(i0Composite, "Number of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		i0NoOfAccumulationValueText = new NumberEditorControl(i0Composite, SWT.None, singleSpectrumDataModel.getExperimentDataModel(), ExperimentDataModel.I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		i0NoOfAccumulationValueText.setRange(1, SingleSpectrumCollectionModel.MAX_NO_OF_ACCUMULATIONS);
		fixedWidthGridData.applyTo(i0NoOfAccumulationValueText);

		Composite sectionSeparator = toolkit.createCompositeSeparator(i0AcquisitionSection);
		toolkit.paintBordersFor(sectionSeparator);
		i0AcquisitionSection.setSeparatorControl(sectionSeparator);

		// IRef
		sectionIRefaccumulationSection = toolkit.createSection(composite, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		sectionIRefaccumulationSection.setText("IRef acquisition settings");
		sectionIRefaccumulationSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		final Composite iRefDetailsComposite = toolkit.createComposite(sectionIRefaccumulationSection, SWT.NONE);
		iRefDetailsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		sectionIRefaccumulationSection.setClient(iRefDetailsComposite);

		label = toolkit.createLabel(iRefDetailsComposite, "Accumulation time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		iRefIntegrationTimeValueText = new NumberEditorControl(iRefDetailsComposite, SWT.None, singleSpectrumDataModel.getExperimentDataModel(), ExperimentDataModel.IREF_INTEGRATION_TIME_PROP_NAME, true);
		iRefIntegrationTimeValueText.setUnit(DetectorModel.INSTANCE.getUnitForAccumulationTime().getUnitText());
		iRefIntegrationTimeValueText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		fixedWidthGridData.applyTo(iRefIntegrationTimeValueText);

		label = toolkit.createLabel(iRefDetailsComposite, "No. of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		iRefNoOfAccumulationValueText = new NumberEditorControl(iRefDetailsComposite, SWT.None, singleSpectrumDataModel.getExperimentDataModel(), ExperimentDataModel.IREF_NO_OF_ACCUMULATION_PROP_NAME, true);
		fixedWidthGridData.applyTo(iRefNoOfAccumulationValueText);

		sectionSeparator = toolkit.createCompositeSeparator(sectionIRefaccumulationSection);
		toolkit.paintBordersFor(sectionSeparator);
		sectionIRefaccumulationSection.setSeparatorControl(sectionSeparator);
	}

	private void setupUI() throws Exception {

		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		createI0IRefComposites();

		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, false, false);
		gridData.widthHint = BOX_WIDTH;
		GridDataFactory fixedWidthGridData = GridDataFactory.createFrom(gridData);

		// It acquisition settings
		section = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		section.setText("It acquisition settings");
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sectionComposite);
		section.setClient(sectionComposite);


		Composite acquisitionSettingsComposite = new Composite(sectionComposite, SWT.NONE);
		acquisitionSettingsComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, true));
		acquisitionSettingsComposite.setLayout(new GridLayout(2, false));
		toolkit.paintBordersFor(acquisitionSettingsComposite);

		Label itIntegrationTimeLabel = toolkit.createLabel(acquisitionSettingsComposite, "Accumulation time");
		itIntegrationTimeLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl itIntegrationTimeText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumCollectionModel.IT_INTEGRATION_TIME_PROP_NAME, true);
		itIntegrationTimeText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		itIntegrationTimeText.setUnit(DetectorModel.INSTANCE.getUnitForAccumulationTime().getUnitText());
		fixedWidthGridData.applyTo(itIntegrationTimeText);

		if (showAccumulationReadout) {
			Label label = toolkit.createLabel(acquisitionSettingsComposite, "Accumulation readout time", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			accumulationReadoutTimeValueText = toolkit.createText(acquisitionSettingsComposite, "");
			accumulationReadoutTimeValueText.setEditable(false);
			accumulationReadoutTimeValueText.setEnabled(false);
			fixedWidthGridData.applyTo(accumulationReadoutTimeValueText);
		}

		Label itNoOfAccumulationLabel = toolkit.createLabel(acquisitionSettingsComposite, "Number of accumulations");
		itNoOfAccumulationLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl itNoOfAccumulationText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumCollectionModel.IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		fixedWidthGridData.applyTo(itNoOfAccumulationText);

		if (showAccumulationReadout) {
			Label label = toolkit.createLabel(acquisitionSettingsComposite, "Real time per spectrum", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			realTimePerSpectrumValueText = toolkit.createText(acquisitionSettingsComposite, "");
			realTimePerSpectrumValueText.setEditable(false);
			realTimePerSpectrumValueText.setEnabled(false);
			fixedWidthGridData.applyTo(realTimePerSpectrumValueText);
		}

		Composite acquisitionSettingsFileNameComposite = new Composite(sectionComposite, SWT.NONE);
		acquisitionSettingsFileNameComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true));
		acquisitionSettingsFileNameComposite.setLayout(new GridLayout(2, false));
		toolkit.paintBordersFor(acquisitionSettingsFileNameComposite);

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(section),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));


		// 'Use topup checker' checkbox and databinding
		Button useTopupCheckerCheckbox = toolkit.createButton(acquisitionSettingsComposite, "Use topup checker", SWT.CHECK);
		useTopupCheckerCheckbox.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false));
		useTopupCheckerCheckbox.setEnabled(true);

		dataBindingCtx.bindValue(WidgetProperties.selection().observe(useTopupCheckerCheckbox),
				BeanProperties.value(SingleSpectrumCollectionModel.USE_TOPUP_CHECKER_FOR_IT_PROP_NAME).observe(singleSpectrumDataModel));


		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(defaultSectionSeparator);
		section.setSeparatorControl(defaultSectionSeparator);
	}

	@Override
	protected void disposeResource() {
		dataBindingCtx.dispose();
	}

	private void updateI0noOfAccuBinding(final SingleSpectrumCollectionModel singleSpectrumDataModel, Object value) {
		if (!(boolean) value && binding == null) {
			binding = dataBindingCtx.bindValue(
					BeanProperties.value(ExperimentDataModel.I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME).observe(singleSpectrumDataModel.getExperimentDataModel()),
					BeanProperties.value(SingleSpectrumCollectionModel.IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME).observe(singleSpectrumDataModel));
		} else {
			if (binding != null) {
				dataBindingCtx.removeBinding(binding);
				binding.dispose();
				binding = null;
			}
		}
	}
}
