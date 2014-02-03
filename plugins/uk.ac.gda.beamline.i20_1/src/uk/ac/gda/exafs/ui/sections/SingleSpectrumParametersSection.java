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

package uk.ac.gda.exafs.ui.sections;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumUIModel;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentDataModel;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentModelHolder;
import uk.ac.gda.exafs.ui.data.experiment.SampleStageMotors;
import uk.ac.gda.ui.components.NumberEditorControl;

public class SingleSpectrumParametersSection extends ResourceComposite {

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

	private Composite i0NoOfaccumulationsComposite;

	public SingleSpectrumParametersSection(Composite parent, int style) {
		super(parent, style);
		toolkit = new FormToolkit(parent.getDisplay());
		try {
			setupUI();
			bind();
		} catch (Exception e) {
			logger.error("Unable to create controls", e);
		}
	}

	private void bind() {
		final SingleSpectrumUIModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();

		Binding i0NoOfAccumulationCheckBinding = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(i0NoOfAccumulationCheck),
				BeanProperties.value(ExperimentDataModel.USE_NO_OF_ACCUMULATIONS_FOR_I0_PROP_NAME).observe(singleSpectrumDataModel.getExperimentDataModel()),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus result = super.doSet(observableValue, value);
						updateI0noOfAccuBinding(singleSpectrumDataModel, value);
						return result;
					}
				},
				new UpdateValueStrategy());
		i0NoOfAccumulationCheckBinding.updateTargetToModel();

		dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(i0NoOfaccumulationsComposite),
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
	}

	private void createI0IRefComposites() throws Exception {
		final SingleSpectrumUIModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();

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
		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		i0NoOfAccumulationCheck.setLayoutData(gridData);

		Label label = toolkit.createLabel(i0AcquisitionSectionComposite, "Accumulation time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		NumberEditorControl i0IntegrationTimeValueText = new NumberEditorControl(i0AcquisitionSectionComposite, SWT.None, singleSpectrumDataModel.getExperimentDataModel(), ExperimentDataModel.I0_INTEGRATION_TIME_PROP_NAME, false);
		i0IntegrationTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		i0IntegrationTimeValueText.setUnit(UnitSetup.MILLI_SEC.getText());

		i0NoOfaccumulationsComposite = toolkit.createComposite(i0AcquisitionSectionComposite);
		i0NoOfaccumulationsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		i0NoOfaccumulationsComposite.setLayoutData(gridData);

		label = toolkit.createLabel(i0NoOfaccumulationsComposite, "Number of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		i0NoOfAccumulationValueText = new NumberEditorControl(i0NoOfaccumulationsComposite, SWT.None, singleSpectrumDataModel.getExperimentDataModel(), ExperimentDataModel.I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME, false);
		i0NoOfAccumulationValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

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
		iRefIntegrationTimeValueText = new NumberEditorControl(iRefDetailsComposite, SWT.None, singleSpectrumDataModel.getExperimentDataModel(), ExperimentDataModel.IREF_INTEGRATION_TIME_PROP_NAME, false);
		iRefIntegrationTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		iRefIntegrationTimeValueText.setUnit(UnitSetup.MILLI_SEC.getText());

		label = toolkit.createLabel(iRefDetailsComposite, "No. of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		iRefNoOfAccumulationValueText = new NumberEditorControl(iRefDetailsComposite, SWT.None, singleSpectrumDataModel.getExperimentDataModel(), ExperimentDataModel.IREF_NO_OF_ACCUMULATION_PROP_NAME, false);
		iRefNoOfAccumulationValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		sectionSeparator = toolkit.createCompositeSeparator(sectionIRefaccumulationSection);
		toolkit.paintBordersFor(sectionSeparator);
		sectionIRefaccumulationSection.setSeparatorControl(sectionSeparator);
	}

	private void setupUI() throws Exception {

		final SingleSpectrumUIModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		createIncludedStripsSelection();

		createI0IRefComposites();

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

		NumberEditorControl itIntegrationTimeText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumUIModel.IT_INTEGRATION_TIME_PROP_NAME, true);
		itIntegrationTimeText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		itIntegrationTimeText.setUnit(ClientConfig.UnitSetup.MILLI_SEC.getText());
		itIntegrationTimeText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label itNoOfAccumulationLabel = toolkit.createLabel(acquisitionSettingsComposite, "Number of accumulations");
		itNoOfAccumulationLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl itNoOfAccumulationText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumUIModel.IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		itNoOfAccumulationText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite acquisitionSettingsFileNameComposite = new Composite(sectionComposite, SWT.NONE);
		acquisitionSettingsFileNameComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true));
		acquisitionSettingsFileNameComposite.setLayout(new GridLayout(2, false));
		toolkit.paintBordersFor(acquisitionSettingsFileNameComposite);

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(section),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(defaultSectionSeparator);
		section.setSeparatorControl(defaultSectionSeparator);
	}

	private void createIncludedStripsSelection() {
		IncludedStripsSectionComposite includedStripsSectionComposite = new IncludedStripsSectionComposite(this, SWT.None, toolkit);
		includedStripsSectionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
	}

	@Override
	protected void disposeResource() {
		dataBindingCtx.dispose();
	}

	private void updateI0noOfAccuBinding(final SingleSpectrumUIModel singleSpectrumDataModel, Object value) {
		if (!(boolean) value && binding == null) {
			binding = dataBindingCtx.bindValue(
					BeanProperties.value(ExperimentDataModel.I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME).observe(singleSpectrumDataModel.getExperimentDataModel()),
					BeanProperties.value(SingleSpectrumUIModel.IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME).observe(singleSpectrumDataModel));
		} else {
			if (binding != null) {
				dataBindingCtx.removeBinding(binding);
				binding.dispose();
				binding = null;
			}
		}
	}
}
