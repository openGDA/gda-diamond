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
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.SingleSpectrumUIModel;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentModelHolder;
import uk.ac.gda.exafs.ui.sections.SingleSpectrumParametersSection;

public class ExperimentSingleSpectrumView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.experimentSingleSpectrumView";

	private static Logger logger = LoggerFactory.getLogger(ExperimentSingleSpectrumView.class);

	private FormToolkit toolkit;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ScrolledForm scrolledform;

	private Form form;


	private Composite sampleStageSectionsParent;

	private Binding sampleStageCompositeBinding;


	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledform = toolkit.createScrolledForm(parent);
		form = scrolledform.getForm();
		form.getBody().setLayout(new GridLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum / E calibration");
		Composite formParent = form.getBody();
		try {
			createRunCollectionButtons(formParent);
			createSampleStageSections(formParent);
			setupScannables();
			SingleSpectrumParametersSection singleSpectrumParametersSection = new SingleSpectrumParametersSection(formParent, SWT.None);
			singleSpectrumParametersSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
			createSampleDetailsSection(formParent);
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}

	private void createSampleDetailsSection(Composite formParent) {
		final SingleSpectrumUIModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();

		final Section sampleDetailsSection = toolkit.createSection(formParent, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		sampleDetailsSection.setText("Sample details");
		sampleDetailsSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sectionComposite = toolkit.createComposite(sampleDetailsSection, SWT.NONE);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		toolkit.paintBordersFor(sectionComposite);
		sampleDetailsSection.setClient(sectionComposite);

		Label fileNameLabel = toolkit.createLabel(sectionComposite, "File name prefix");
		fileNameLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		Text fileNamePrefixText = toolkit.createText(sectionComposite, "", SWT.BORDER);
		fileNamePrefixText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		// FIXME Add validation
		dataBindingCtx.bindValue(
				WidgetProperties.text(SWT.Modify).observe(fileNamePrefixText),
				BeanProperties.value(SingleSpectrumUIModel.FILE_TEMPLATE_PROP_NAME).observe(singleSpectrumDataModel),
				new UpdateValueStrategy(),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));

		Label sampleDescLabel = toolkit.createLabel(sectionComposite, "Sample description");
		sampleDescLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		Text sampleDescLabelText = toolkit.createText(sectionComposite, "", SWT.BORDER);
		sampleDescLabelText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	private void createRunCollectionButtons(Composite formParent) {
		final SingleSpectrumUIModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();
		Composite acquisitionButtonsComposite = new Composite(formParent, SWT.NONE);
		acquisitionButtonsComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		acquisitionButtonsComposite.setLayout(new GridLayout(2, true));
		toolkit.paintBordersFor(acquisitionButtonsComposite);

		Button startAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Start", SWT.PUSH);
		startAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		startAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					singleSpectrumDataModel.doCollection(true);
				} catch (Exception e) {
					UIHelper.showError("Unable to scan", e.getMessage());
					logger.error("Unable to scan", e);
				}
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startAcquicitionButton),
				BeanProperties.value(SingleSpectrumUIModel.SCANNING_PROP_NAME).observe(singleSpectrumDataModel),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return (!(boolean) value);
					}
				});

		Button stopAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Stop", SWT.PUSH);
		stopAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(stopAcquicitionButton),
				BeanProperties.value(SingleSpectrumUIModel.SCANNING_PROP_NAME).observe(singleSpectrumDataModel));
		stopAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				singleSpectrumDataModel.doStop();
			}
		});
	}

	private void setupScannables() {
		sampleStageCompositeBinding = dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(sampleStageSectionsParent),
				BeanProperties.value(SingleSpectrumUIModel.ALIGNMENT_STAGE_SELECTION).observe(ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel()),
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
	}

	private void createSampleStageSections(Composite body) {
		sampleStageSectionsParent = new SampleStageMotorsComposite(body, SWT.None, toolkit, true);
	}

	@Override
	public void dispose() {
		dataBindingCtx.removeBinding(sampleStageCompositeBinding);
		sampleStageCompositeBinding.dispose();
		super.dispose();
	}

	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}
}
