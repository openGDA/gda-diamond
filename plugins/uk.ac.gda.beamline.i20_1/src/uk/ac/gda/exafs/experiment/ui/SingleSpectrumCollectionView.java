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

import org.dawnsci.ede.CalibrationDetails;
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

import gda.device.DeviceException;
import gda.scan.ede.TimeResolvedExperimentParameters;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.alignment.ui.SampleStageMotorsComposite;
import uk.ac.gda.exafs.alignment.ui.SingleSpectrumParametersSection;
import uk.ac.gda.exafs.calibration.ui.EnergyCalibrationComposite;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumCollectionModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentDataModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;

public class SingleSpectrumCollectionView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.experimentSingleSpectrumView";

	private static Logger logger = LoggerFactory.getLogger(SingleSpectrumCollectionView.class);

	private FormToolkit toolkit;

	private DataBindingContext dataBindingCtx;

	private ScrolledForm scrolledform;

//	private Form form;

	private Composite sampleStageSectionsParent;
	private Text suffixText;
	private Text sampleDescText;
	private EnergyCalibrationComposite energyCalComposite;

	private Binding sampleStageCompositeBinding;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		dataBindingCtx = new DataBindingContext();

		final SashForm parentComposite = new SashForm(parent, SWT.VERTICAL);
		parentComposite.SASH_WIDTH = 7;

		Composite composite = new Composite(parentComposite, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1,false));
		scrolledform = toolkit.createScrolledForm(composite);
		scrolledform.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new GridLayout(1, true));

		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum");
		Composite formParent = form.getBody();
		try {
			createSampleDetailsSection(formParent);
			createSampleStageSections(formParent);
			setupScannables();
			SingleSpectrumParametersSection singleSpectrumParametersSection = new SingleSpectrumParametersSection(formParent, SWT.None);
			singleSpectrumParametersSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
			createEnergyCalibrationSection(formParent);
			createStartStopScanSection(parentComposite, toolkit, suffixText, sampleDescText);
			form.layout();
			parentComposite.setWeights(new int[] {5, 1});
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}

	private void createStartStopScanSection(Composite parent, FormToolkit toolkit, final Text suffixTextBox, final Text descriptionTextBox ) {
		final Section startStopScanSection = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR);
		startStopScanSection.setText("Scan run controls");
		startStopScanSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite startStopSectionComposite = toolkit.createComposite(startStopScanSection, SWT.NONE);
		startStopSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		startStopScanSection.setClient(startStopSectionComposite);
		addCollectionControls(startStopSectionComposite, toolkit, suffixTextBox, descriptionTextBox );

		SaveLoadButtonsForSingleCollection saveLoadButtons = new SaveLoadButtonsForSingleCollection(startStopSectionComposite, toolkit);
	}

	/**
	 * Method to add start, stop buttons to composite and apply databinding to single spectrum model properties..
	 *
	 * @param parent
	 * @param toolkit
	 * @param suffixTextBox
	 * @param descriptionTextBox
	 * @26/2/2016
	 */
	private void addCollectionControls( Composite parent, FormToolkit toolkit, final Text suffixTextBox, final Text descriptionTextBox ) {
		final DataBindingContext dataBindingCtx = new DataBindingContext();

		Button startAcquicitionButton = toolkit.createButton(parent, "Start", SWT.PUSH);
		startAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		startAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					if ( suffixTextBox == null ||  descriptionTextBox == null ) {
						getModel().doCollection(false, null, "");
					} else {
						getModel().doCollection(true, suffixTextBox.getText(), descriptionTextBox.getText());
					}
				} catch (Exception e) {
					UIHelper.showError("Unable to scan", e.getMessage());
					logger.error("Unable to scan", e);
				}
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startAcquicitionButton),
				BeanProperties.value(SingleSpectrumCollectionModel.SCANNING_PROP_NAME).observe(getModel()),
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
				BeanProperties.value(SingleSpectrumCollectionModel.SCANNING_PROP_NAME).observe(getModel()));
		stopAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				getModel().doStop();
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
		// Checkbox for fast shutter
		Button useFastShutterCheckbox = toolkit.createButton(parent, "Use fast shutter", SWT.CHECK);
		useFastShutterCheckbox.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(WidgetProperties.selection().observe(useFastShutterCheckbox),
				BeanProperties.value(ExperimentDataModel.USE_FAST_SHUTTER_PROP_NAME).observe(getModel().getExperimentDataModel()) );
	}

	/**
	 * Linear experiment specific implementation of SaveLoadButtons class
	 * (get parameters from gui, setup gui from parameters implemented)
	 */
	private class SaveLoadButtonsForSingleCollection extends SaveLoadButtonsComposite {

		public SaveLoadButtonsForSingleCollection(Composite parent, FormToolkit toolkit) {
			super(parent, toolkit);
		}

		@Override
		protected void saveParametersToFile(String filename) throws DeviceException {
			TimeResolvedExperimentParameters params = getModel().getParametersBeanFromCurrentSettings();
			params.saveToFile(filename);
		}

		@Override
		protected void loadParametersFromFile(String filename) throws Exception {
			TimeResolvedExperimentParameters params = TimeResolvedExperimentParameters.loadFromFile(filename);
			getModel().setupFromParametersBean(params);
			updateCalibrationGui(getModel().getCalibrationDetails());
			// Update the detector with the new calibration
			DetectorModel.INSTANCE.getCurrentDetector().setEnergyCalibration(getModel().getCalibrationDetails());
		}
	}

	private void createSampleDetailsSection(Composite formParent) {
		SampleDetailsSection sampleDetailComp = new SampleDetailsSection(formParent, toolkit);
		sampleDetailComp.bindWidgetsToModel(getModel().getExperimentDataModel());

		suffixText = sampleDetailComp.getSuffixTextbox();
		sampleDescText = sampleDetailComp.getSampleDescriptionTextbox();
		addFastShutterControls(sampleDetailComp.getMainComposite(), toolkit);
	}

	private void updateCalibrationGui(CalibrationDetails calibrationDetails) {
		if (calibrationDetails != null) {
			energyCalComposite.setPolynomialString(calibrationDetails.getFormattedPolinormal());
			energyCalComposite.setSampleFileName(calibrationDetails.getSampleDataFileName());
			energyCalComposite.setReferenceFileName(calibrationDetails.getReferenceDataFileName());
			energyCalComposite.updateGuiFromParameters();
		}
	}

	private void createEnergyCalibrationSection(Composite parent) {
		energyCalComposite = new EnergyCalibrationComposite(parent);
		energyCalComposite.setShowPositions(false);
		energyCalComposite.createSection("EDE calibration");

		// Get calibration from detector, update the model and gui
		CalibrationDetails currentDetectorCalibration = DetectorModel.INSTANCE.getCurrentDetector().getEnergyCalibration();
		getModel().setCalibrationDetails(currentDetectorCalibration);
		updateCalibrationGui(currentDetectorCalibration);

		// Update the detector and model after calibration has completed.
		energyCalComposite.setAfterCalibrationRunnable(() -> {
			CalibrationDetails calibration = energyCalComposite.getCalibrationDetails();
			DetectorModel.INSTANCE.getCurrentDetector().setEnergyCalibration(calibration);
			getModel().setCalibrationDetails(calibration);
			updateCalibrationGui(calibration);
		});
	}

	private static SingleSpectrumCollectionModel getModel() {
		return ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();
	}

	private void setupScannables() {
		sampleStageCompositeBinding = dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(sampleStageSectionsParent),
				BeanProperties.value(SingleSpectrumCollectionModel.ALIGNMENT_STAGE_SELECTION).observe(getModel()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus status = super.doSet(observableValue, !((boolean) value));
						((GridData) sampleStageSectionsParent.getLayoutData()).exclude = ((boolean) value);
						return status;
					}
				});
	}

	private void createSampleStageSections(Composite body) {
		sampleStageSectionsParent = new SampleStageMotorsComposite(body, SWT.None, toolkit, true);
	}

	@Override
	public void dispose() {
		ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel().saveSettings();
		dataBindingCtx.removeBinding(sampleStageCompositeBinding);
		sampleStageCompositeBinding.dispose();
		super.dispose();
	}

	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}
}
