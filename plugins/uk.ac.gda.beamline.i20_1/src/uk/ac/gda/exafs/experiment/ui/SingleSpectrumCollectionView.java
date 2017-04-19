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

package uk.ac.gda.exafs.experiment.ui;

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

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.alignment.ui.SampleStageMotorsComposite;
import uk.ac.gda.exafs.alignment.ui.SingleSpectrumParametersSection;
import uk.ac.gda.exafs.data.SingleSpectrumCollectionModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;

public class SingleSpectrumCollectionView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.experimentSingleSpectrumView";

	private static Logger logger = LoggerFactory.getLogger(SingleSpectrumCollectionView.class);

	private FormToolkit toolkit;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ScrolledForm scrolledform;

	private Form form;

	private Composite sampleStageSectionsParent;
	private Text prefixText;
	private Text sampleDescText;

	private Binding sampleStageCompositeBinding;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledform = toolkit.createScrolledForm(parent);
		form = scrolledform.getForm();
		form.getBody().setLayout(new GridLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum");
		Composite formParent = form.getBody();
		try {
			createSampleDetailsSection(formParent);
			createSampleStageSections(formParent);
			setupScannables();
			SingleSpectrumParametersSection singleSpectrumParametersSection = new SingleSpectrumParametersSection(formParent, SWT.None);
			singleSpectrumParametersSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
			createStartStopScanSection(formParent, toolkit, prefixText, sampleDescText);
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}

	static public void createStartStopScanSection(Composite parent, FormToolkit toolkit, final Text prefixTextBox, final Text descriptionTextBox ) {
		final Section startStopScanSection = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR);
		startStopScanSection.setText("Scan run controls");
		startStopScanSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite startStopSectionComposite = toolkit.createComposite(startStopScanSection, SWT.NONE);
		startStopSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		startStopScanSection.setClient(startStopSectionComposite);
		addCollectionControls(startStopSectionComposite, toolkit, prefixTextBox, descriptionTextBox );
	}

	/**
	 * Static method to add start, stop buttons to composite and apply databinding to single spectrum model properties..
	 * Added to try and reduce code duplication between SingleSpectrumCollectionView and SingleSpectrumAlignmentView.
	 * @param parent
	 * @param toolkit
	 * @param prefixTextBox
	 * @param descriptionTextBox
	 * @26/2/2016
	 */
	static public void addCollectionControls( Composite parent, FormToolkit toolkit, final Text prefixTextBox, final Text descriptionTextBox ) {
		final DataBindingContext dataBindingCtx = new DataBindingContext();

		final SingleSpectrumCollectionModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();

		Button startAcquicitionButton = toolkit.createButton(parent, "Start", SWT.PUSH);
		startAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		startAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					if ( prefixTextBox == null ||  descriptionTextBox == null ) {
						singleSpectrumDataModel.doCollection(false, null, "");
					} else {
						singleSpectrumDataModel.doCollection(true, prefixTextBox.getText(), descriptionTextBox.getText());
					}
				} catch (Exception e) {
					UIHelper.showError("Unable to scan", e.getMessage());
					logger.error("Unable to scan", e);
				}
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startAcquicitionButton),
				BeanProperties.value(SingleSpectrumCollectionModel.SCANNING_PROP_NAME).observe(singleSpectrumDataModel),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return (!(boolean) value);
					}
				});

		Button stopAcquicitionButton = toolkit.createButton(parent, "Stop", SWT.PUSH);
		stopAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(stopAcquicitionButton),
				BeanProperties.value(SingleSpectrumCollectionModel.SCANNING_PROP_NAME).observe(singleSpectrumDataModel));
		stopAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				singleSpectrumDataModel.doStop();
			}
		});
	}

	/**
	 * Refactored from {@link #addCollectionControls}
	 * @since 18/4/2017
	 * @param parent
	 * @param toolkit
	 */
	private void addFastShutterControls( Composite parent, FormToolkit toolkit ) {
		final DataBindingContext dataBindingCtx = new DataBindingContext();

		final SingleSpectrumCollectionModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();

		// Checkbox for fast shutter
		Button useFastShutterCheckbox = toolkit.createButton(parent, "Use fast shutter", SWT.CHECK);
		useFastShutterCheckbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(WidgetProperties.selection().observe(useFastShutterCheckbox),
				BeanProperties.value(SingleSpectrumCollectionModel.USE_FAST_SHUTTER_PROP_NAME).observe( singleSpectrumDataModel ) );
	}

	private void createSampleDetailsSection(Composite formParent) {
		final Section dataCollectionSection = toolkit.createSection(formParent, ExpandableComposite.NO_TITLE);
		dataCollectionSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite dataCollectionSectionComposite = toolkit.createComposite(dataCollectionSection, SWT.NONE);
		dataCollectionSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		dataCollectionSection.setClient(dataCollectionSectionComposite);

		Composite prefixNameComposite = toolkit.createComposite(dataCollectionSectionComposite, SWT.NONE);
		prefixNameComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		prefixNameComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		Label prefixLabel = toolkit.createLabel(prefixNameComposite, "File prefix", SWT.None);
		prefixLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		prefixText = toolkit.createText(prefixNameComposite, "", SWT.BORDER);
		prefixText.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		Composite sampleDescComposite = toolkit.createComposite(dataCollectionSectionComposite, SWT.NONE);
		sampleDescComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		sampleDescComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		Label sampleDescLabel = toolkit.createLabel(sampleDescComposite, "Sample details", SWT.None);
		sampleDescLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		sampleDescText = toolkit.createText(sampleDescComposite, "", SWT.BORDER);
		sampleDescText.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		addFastShutterControls(dataCollectionSectionComposite, toolkit);
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
