/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.IJythonServerStatusObserver;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.scan.ScanEvent;
import gda.scan.ede.TimeResolvedExperimentParameters;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.alignment.ui.SampleStageMotorsComposite;
import uk.ac.gda.exafs.alignment.ui.SingleSpectrumParametersSection;
import uk.ac.gda.exafs.calibration.ui.EnergyCalibrationComposite;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumCollectionModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentDataModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;
import uk.ac.gda.exafs.ui.composites.ScannableListEditor;
import uk.ac.gda.exafs.ui.composites.ScannablePositionsComposite;

/**
 * Code to generate widgets and databinding used for 'Single Spectra' collection views.
 * Refactored from {@link SingleSpectrumCollectionView} and used in {@link SingleSpectrumCollectionView}
 * and {@link SingleSpectrumCollectionViewWithMapping}.
 *
 */
public class SingleSpectrumCollectionWidgets implements IObserver {

	private static Logger logger = LoggerFactory.getLogger(SingleSpectrumCollectionWidgets.class);

	private FormToolkit toolkit;
	private SingleSpectrumCollectionModel model;
	private DataBindingContext dataBindingCtx = new DataBindingContext();

	private SampleDetailsSection sampleDetailComposite;
	private ScannablePositionsComposite scannablePositions;
	private SampleStageMotorsComposite sampleStageSectionsParent;
	private EnergyCalibrationComposite energyCalComposite;

	private IJythonServerStatusObserver serverObserver;

	public SingleSpectrumCollectionWidgets() {
	}

	public void createSampleDetailsSection(Composite parent) {
		sampleDetailComposite = new SampleDetailsSection(parent, toolkit);
		sampleDetailComposite.bindWidgetsToModel(getModel().getExperimentDataModel());
		addFastShutterControls(sampleDetailComposite.getMainComposite());
		addScannablesToMonitorControls(sampleDetailComposite.getMainComposite());
	}

	/**
	 * Refactored from {@link #addCollectionControls}
	 * @since 18/4/2017
	 * @param parent
	 * @param toolkit
	 */
	private void addFastShutterControls(Composite parent) {
		// Checkbox for fast shutter
		Button useFastShutterCheckbox = toolkit.createButton(parent, "Use fast shutter", SWT.CHECK);
		useFastShutterCheckbox.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(WidgetProperties.selection().observe(useFastShutterCheckbox),
				BeanProperties.value(ExperimentDataModel.USE_FAST_SHUTTER_PROP_NAME).observe(getModel().getExperimentDataModel()) );
	}

	private void addScannablesToMonitorControls(Composite parent) {
		Button setupScannableButton = toolkit.createButton(parent, "Setup scannables/PVs to monitor", SWT.PUSH);
		setupScannableButton.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false));
		ScannableListEditor scannableListEditor = new ScannableListEditor(parent.getShell());

		setupScannableButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				scannableListEditor.setScannableInfoFromMap(getModel().getExperimentDataModel().getScannablesToMonitor());
				scannableListEditor.open();
				if (scannableListEditor.getReturnCode() == Window.OK) {
					getModel().getExperimentDataModel().setScannablesToMonitor(scannableListEditor.getScannableMapFromList());
				}
			}
		});
	}

	public void createSampleStageSections(Composite parent) {
		sampleStageSectionsParent = new SampleStageMotorsComposite(parent, SWT.None, toolkit, true);

		dataBindingCtx.bindValue(
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

	public void createSpectrumParametersSection(Composite parent) {
		SingleSpectrumParametersSection singleSpectrumParametersSection = new SingleSpectrumParametersSection(parent, SWT.None, getModel());
		singleSpectrumParametersSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
	}

	public void createEnergyCalibrationSection(Composite parent) {
		energyCalComposite = new EnergyCalibrationComposite(parent);
		energyCalComposite.setShowPositions(false);
		energyCalComposite.createSection("EDE calibration");

		// Get calibration from detector, update the model and gui
		CalibrationDetails currentDetectorCalibration = DetectorModel.INSTANCE.getCurrentDetector().getEnergyCalibration();

		// always want to deal with SingleSpectrumCollection model for the calibration details
		final SingleSpectrumCollectionModel modelForEnergyCalibration = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();

		modelForEnergyCalibration.setCalibrationDetails(currentDetectorCalibration);
		updateCalibrationGui(currentDetectorCalibration);

		// Update the detector and model after calibration has completed.
		energyCalComposite.setAfterCalibrationRunnable(() -> {
			CalibrationDetails calibration = energyCalComposite.getCalibrationDetails();
			DetectorModel.INSTANCE.getCurrentDetector().setEnergyCalibration(calibration);
			modelForEnergyCalibration.setCalibrationDetails(calibration);
		});

		// Listener to automatically update the GUI when the calibration model changes
		modelForEnergyCalibration.addPropertyChangeListener(SingleSpectrumCollectionModel.CALIBRATION_DETAILS, event -> {
			CalibrationDetails calibration = (CalibrationDetails) event.getNewValue();
			updateCalibrationGui(calibration);

			// Also set the calibration for SingleSpectrumCollectionWithMapping to match the new one.
			if (model == ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentMappingModel()) {
				model.setCalibrationDetails(calibration);
			}
		});
	}

	private void updateCalibrationGui(CalibrationDetails calibrationDetails) {
		if( energyCalComposite.getSampleFileTextbox().isDisposed()) {
			return;
		}
		if (calibrationDetails != null) {
			energyCalComposite.setPolynomialString(calibrationDetails.getFormattedPolinormal());
			energyCalComposite.setSampleFileName(calibrationDetails.getSampleDataFileName());
			energyCalComposite.setReferenceFileName(calibrationDetails.getReferenceDataFileName());
		} else {
			energyCalComposite.setPolynomialString("");
			energyCalComposite.setSampleFileName("");
			energyCalComposite.setReferenceFileName("");
		}
		energyCalComposite.updateGuiFromParameters();
	}

	public void createScannablePositionsSection(Composite parent) {
		Section section = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE);
		section.setText("Set scannable positions");
		section.setExpanded(true);
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite mainComposite = toolkit.createComposite(section, SWT.NONE);
		mainComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		section.setClient(mainComposite);

		scannablePositions = new ScannablePositionsComposite(mainComposite, toolkit);
		scannablePositions.addSection();
		updateScannablePositionsGui();
		scannablePositions.addIObserver(this);
	}

	@Override
	public void update(Object source, Object arg) {
		// Update the model when something in the scannable positions GUI changes
		logger.debug("Updating model from scannable positions GUI");
		ExperimentDataModel dataModel = getModel().getExperimentDataModel();
		dataModel.setCollectMultipleItSpectra(scannablePositions.isCollectMultipleSpectra());
		dataModel.setScannableToMoveForItScan(scannablePositions.getScannableName());
		dataModel.setPositionsForItScan(scannablePositions.getScannablePositions());
	}

	private void updateScannablePositionsGui() {
		if (scannablePositions == null) {
			return;
		}
		logger.debug("Update scannable positions GUI from model");
		ExperimentDataModel dataModel = getModel().getExperimentDataModel();
		scannablePositions.setCollectMultipleSpectra(dataModel.isCollectMultipleItSpectra());
		scannablePositions.setScannableName(dataModel.getScannableToMoveForItScan());
		scannablePositions.setScannablePositions(dataModel.getPositionsForItScan());
	}

	public void dispose() {
		ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel().saveSettings();
		dataBindingCtx.dispose();
		if (serverObserver != null) {
			InterfaceProvider.getScanDataPointProvider().deleteScanEventObserver(serverObserver);
		}
	}

	public void createStartStopScanSection(Composite parent) {
		final Section startStopScanSection = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR);
		startStopScanSection.setText("Scan run controls");
		startStopScanSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite startStopSectionComposite = toolkit.createComposite(startStopScanSection, SWT.NONE);
		startStopSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		startStopScanSection.setClient(startStopSectionComposite);
		addCollectionControls(startStopSectionComposite);

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
	private void addCollectionControls( Composite parent) {
		final Text suffixTextBox  = sampleDetailComposite.getSuffixTextbox();
		final Text descriptionTextBox = sampleDetailComposite.getSampleDescriptionTextbox();

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
	 * Linear experiment specific implementation of SaveLoadButtons class
	 * (get parameters from gui, setup gui from parameters implemented)
	 */
	private class SaveLoadButtonsForSingleCollection extends SaveLoadButtonsComposite {

		public SaveLoadButtonsForSingleCollection(Composite parent, FormToolkit toolkit) {
			super(parent, toolkit);
		}

		@Override
		protected void saveParametersToFile(String filename) throws Exception {
			TimeResolvedExperimentParameters params = getModel().getParametersBeanFromCurrentSettings();
			params.saveToFile(filename);
		}

		@Override
		protected void loadParametersFromFile(String filename) throws Exception {
			if (!beanIsCorrectType(filename, TimeResolvedExperimentParameters.class)) {
				return;
			}
			TimeResolvedExperimentParameters params = TimeResolvedExperimentParameters.fromXML(getBeanFromFile(filename));
			updateCalibrationDetails(params);
			getModel().setupFromParametersBean(params);
			updateScannablePositionsGui();
		}
	}

	/**
	 * Update the SingleSpectrum energy calibration with new value from {@link TimeResolvedExperimentParameters}; check with user to confirm first.
	 * The new calibration details in the {@code params} are overwritten with the current values if the user wants
	 * to keep the current settings.
	 * @param params
	 */
	public static void updateCalibrationDetails(TimeResolvedExperimentParameters params) {
		CalibrationDetails currentCalibration = DetectorModel.INSTANCE.getCurrentDetector().getEnergyCalibration();
		String currentPoly = currentCalibration == null ? "" : currentCalibration.getFormattedPolinormal();

		CalibrationDetails newCalibration = params.createEnergyCalibration();
		String newPoly = newCalibration == null ? "" : newCalibration.getFormattedPolinormal();

		logger.debug("Checking whether to update energy calibration polynomical : old value = {}, new value = {}",currentPoly, newPoly);

		boolean updateDetectorCalibration = true;
		if (!currentPoly.isEmpty() && !newPoly.equals(currentPoly)){
			String message = "Replace current energy calibration polynomial : \n\t '"+currentPoly+"'\n "+
							 "with the one from the file : \n\t'"+newPoly+"' ?";
			updateDetectorCalibration = MessageDialog.openQuestion(Display.getDefault().getActiveShell(), "Replace detector energy polynomial", message);
		}

		SingleSpectrumCollectionModel model = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();

		// Update the model and detector with the new calibration if required
		if (updateDetectorCalibration) {
			logger.debug("Updating energy calibration polynomial to : {}", newPoly);
			model.setCalibrationDetails(newCalibration);
			DetectorModel.INSTANCE.getCurrentDetector().setEnergyCalibration(newCalibration);
		} else {
			// change the parameters to have the old calibration
			params.setCalibrationDetails(currentCalibration);
		}
	}

	public SingleSpectrumCollectionModel getModel() {
		return model;
	}

	public void setModel(SingleSpectrumCollectionModel model) {
		this.model = model;
	}

	public FormToolkit getToolkit() {
		return toolkit;
	}

	public void setToolkit(FormToolkit toolkit) {
		this.toolkit = toolkit;
	}

	public void addServerObserver() {
		serverObserver = getServerObserver();
		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);
	}

	private IJythonServerStatusObserver getServerObserver() {
		return (source, changeCode) -> {
			if (changeCode instanceof ScanEvent) {
				switch (((ScanEvent) changeCode).getLatestStatus()) {
					case COMPLETED_AFTER_FAILURE:
					case COMPLETED_AFTER_STOP:
					case COMPLETED_EARLY:
					case NOTSTARTED:
					case FINISHING_EARLY:
					case TIDYING_UP_AFTER_FAILURE:
					case TIDYING_UP_AFTER_STOP:
					case COMPLETED_OKAY:
						getModel().setScanning(false);
						break;
					case PAUSED:
					case RUNNING:
						getModel().setScanning(true);
						break;
					default:
						getModel().setScanning(false);
						break;
				}
			}
		};
	}
}
