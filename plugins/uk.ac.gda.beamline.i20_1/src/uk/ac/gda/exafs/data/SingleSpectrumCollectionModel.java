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

package uk.ac.gda.exafs.data;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.dawnsci.ede.CalibrationDetails;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.gson.annotations.Expose;

import gda.device.DeviceException;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.scannable.AlignmentStageScannable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerFacade;
import gda.jython.JythonServerStatus;
import gda.jython.JythonStatus;
import gda.observable.IObservable;
import gda.observable.IObserver;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.TimeResolvedExperimentParameters;
import gda.util.exafs.Element;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentDataModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentMotorPostion;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors.ExperimentMotorPostionType;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class SingleSpectrumCollectionModel extends ObservableModel {

	private static final Logger logger = LoggerFactory.getLogger(SingleSpectrumCollectionModel.class);

	private final AlignmentStageScannable.Location holeLocationForAlignment = new AlignmentStageScannable.Location();
	private final AlignmentStageScannable.Location foilLocationForAlignment = new AlignmentStageScannable.Location();

	private static final String SINGLE_JYTHON_DRIVER_OBJ = "singletimeresolveddriver";

	public static final int MAX_NO_OF_ACCUMULATIONS = 65536;

	public static final String IT_INTEGRATION_TIME_PROP_NAME = "itIntegrationTime";
	@Expose
	private double itIntegrationTime = 1.0;

	public static final String IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "itNumberOfAccumulations";
	@Expose
	private int itNumberOfAccumulations = 1;

	public static final String ALIGNMENT_STAGE_SELECTION = "selectAlignmentStage";
	@Expose
	private boolean selectAlignmentStage;

	public static final String FILE_NAME_PROP_NAME = "fileName";
	private String fileName;

	public static final String SCANNING_PROP_NAME = "scanning";
	private boolean scanning;

	public static final String USE_TOPUP_CHECKER_FOR_IT_PROP_NAME = "useTopupCheckerForIt";
	@Expose
	private boolean useTopupCheckerForIt;

	private CalibrationDetails calibrationDetails;

	private ScanJob job;

	@Expose
	private ExperimentDataModel experimentDataModel;

	private String elementSymbol;

	protected Binding binding;

	private static final String SINGLE_SPECTRUM_MODEL_DATA_STORE_KEY = "SINGLE_SPECTRUM_DATA";
	private static final String SINGLE_SPECTRUM_PARAMETER_BEAN_STORE_KEY = "SINGLE_SPECTRUM_PARAMETER_BEAN_DATA";


	public void setup() {
		job = new ScanJob("Performing Single spectrum scan");
		((IObservable) Finder.getInstance().find(EdeExperiment.PROGRESS_UPDATER_NAME)).addIObserver(job);
		InterfaceProvider.getJSFObserver().addIObserver(job);
		job.setUser(true);
		AlignmentParametersModel.INSTANCE.addPropertyChangeListener(AlignmentParametersModel.ELEMENT_PROP_NAME, evt -> {
			if (evt.getNewValue() != null) {
				SingleSpectrumCollectionModel.this.setCurrentElement(((Element) evt.getNewValue()).getSymbol());
			}
		});

		if (AlignmentParametersModel.INSTANCE.getElement() != null) {
			SingleSpectrumCollectionModel.this.setCurrentElement(AlignmentParametersModel.INSTANCE.getElement().getSymbol());
		}

		loadSingleSpectrumData();

		experimentDataModel.addPropertyChangeListener(evt -> saveSettings());

		this.addPropertyChangeListener(evt -> {
			if (evt.getPropertyName().equals(ALIGNMENT_STAGE_SELECTION)
					|| evt.getPropertyName().equals(IT_INTEGRATION_TIME_PROP_NAME)
					|| evt.getPropertyName().equals(IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME)
					|| evt.getPropertyName().equals(USE_TOPUP_CHECKER_FOR_IT_PROP_NAME)) {
				saveSettings();
			}
		});
	}
	/**
	 * Create a new TimeResolvedExperimentParameters object from the current gui settings.
	 * @return TimeResolvedExperimentParameters object
	 * @throws DeviceException
	 */
	public TimeResolvedExperimentParameters getParametersBeanFromCurrentSettings() throws DeviceException {
		TimeResolvedExperimentParameters params = new TimeResolvedExperimentParameters();

		// Conversion factor from seconds to default experiment time unit (ns)
		double conversion = ExperimentUnit.MILLI_SEC.convertTo(1.0, ExperimentUnit.SEC);

		int numI0Accumulations;
		if (experimentDataModel.isUseNoOfAccumulationsForI0()) {
			numI0Accumulations = experimentDataModel.getI0NumberOfAccumulations();
		} else {
			numI0Accumulations = itNumberOfAccumulations;
		}
		params.setI0NumAccumulations(numI0Accumulations);
		params.setI0AccumulationTime(conversion*experimentDataModel.getI0IntegrationTime());

		// Create timing group for the It settings (one spectrum only)
		TimingGroup timingGroup = new TimingGroup();
		timingGroup.setTimePerScan(conversion*itIntegrationTime);
		timingGroup.setNumberOfScansPerFrame(itNumberOfAccumulations);
		timingGroup.setUseTopupChecker(useTopupCheckerForIt);
		timingGroup.setNumberOfFrames(1); // single spectrum collection has 1 spectrum

		List<TimingGroup> itTimingGroups = new ArrayList<TimingGroup>();
		itTimingGroups.add(timingGroup);
		params.setItTimingGroups(itTimingGroups);

		params.setI0MotorPositions(SampleStageMotors.INSTANCE.getSelectedMotorsMap(ExperimentMotorPostionType.I0));
		params.setItMotorPositions(SampleStageMotors.INSTANCE.getSelectedMotorsMap(ExperimentMotorPostionType.It));

		if (SampleStageMotors.INSTANCE.isUseIref()) {
			params.setItMotorPositions(SampleStageMotors.INSTANCE.getSelectedMotorsMap(ExperimentMotorPostionType.IRef));
			params.setIrefNoOfAccumulations(experimentDataModel.getIrefNoOfAccumulations());
			params.setIrefIntegrationTime(conversion*experimentDataModel.getIrefIntegrationTime());
		}

		params.setDetectorName(DetectorModel.INSTANCE.getCurrentDetector().getName());
		params.setTopupMonitorName(DetectorModel.TOPUP_CHECKER);
		params.setBeamShutterScannableName(DetectorModel.SHUTTER_NAME);

		params.setUseFastShutter(experimentDataModel.getUseFastShutter());
		params.setFastShutterName(DetectorModel.FAST_SHUTTER_NAME);
		params.setFileNameSuffix(experimentDataModel.getFileNameSuffix());
		params.setSampleDetails(experimentDataModel.getSampleDetails());
		params.setScannablesToMonitorDuringScan(experimentDataModel.getScannablesToMonitor());

		// Set the calibration details, if available
		params.setCalibrationDetails(calibrationDetails);

		return params;
	}

	/**
	 * Setup the GUI from a {@link TimeResolvedExperimentParameters} object.
	 * @param params
	 */
	public void setupFromParametersBean(TimeResolvedExperimentParameters params) {
		List<TimingGroup> timingGroups = params.getItTimingGroups();
		TimingGroup group0 = timingGroups.get(0);

		double conversion = ExperimentUnit.SEC.convertTo(1.0, ExperimentUnit.MILLI_SEC);

		int numItAccum = group0.getNumberOfScansPerFrame();
		int numI0Accum = params.getI0NumAccumulations();
		boolean setI0Accum = numI0Accum!=numItAccum;
		experimentDataModel.setUseNoOfAccumulationsForI0(setI0Accum);
		experimentDataModel.setI0IntegrationTime(conversion*params.getI0AccumulationTime());

		setItIntegrationTime(conversion*group0.getTimePerScan());
		setItNumberOfAccumulations(numItAccum);
		setUseTopupCheckerForIt(group0.getUseTopChecker());

		setupSampleStageMotors(params);

		experimentDataModel.setUseFastShutter(params.getUseFastShutter());
		experimentDataModel.setFileNameSuffix(params.getFileNameSuffix());
		experimentDataModel.setSampleDetails(params.getSampleDetails());
		experimentDataModel.setScannablesToMonitor(params.getScannablesToMonitorDuringScan());

		calibrationDetails = params.createEnergyCalibration();
	}

	/**
	 * Setup selected sample stage motors from motor parameters stored in {@link TimeResolvedExperimentParameters} object.
	 * @param params
	 */
	private void setupSampleStageMotors(TimeResolvedExperimentParameters params) {
		ExperimentMotorPostion[] selectedMotors = SampleStageMotors.INSTANCE.setupExperimentMotorTargetPositions(params);
		SampleStageMotors.INSTANCE.setSelectedMotors(selectedMotors);
		SampleStageMotors.INSTANCE.setUseIref(params.getDoIref());
	}

	private void loadSingleSpectrumData() {
		SingleSpectrumCollectionModel singleSpectrumData = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(SINGLE_SPECTRUM_MODEL_DATA_STORE_KEY, SingleSpectrumCollectionModel.class);
		if (singleSpectrumData == null) {
			experimentDataModel = new ExperimentDataModel();
			return;
		}
		experimentDataModel = singleSpectrumData.getExperimentDataModel();

		this.setItIntegrationTime(singleSpectrumData.getItIntegrationTime());
		this.setItNumberOfAccumulations(singleSpectrumData.getItNumberOfAccumulations());
		this.setUseTopupCheckerForIt( singleSpectrumData.getUseTopupCheckerForIt() );

		// Try to set up motors and energy calibration from stored xml bean
		String xmlBean = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(SINGLE_SPECTRUM_PARAMETER_BEAN_STORE_KEY, String.class);
		if (xmlBean != null) {
			try {
				TimeResolvedExperimentParameters params = TimeResolvedExperimentParameters.fromXML(xmlBean);
				setupSampleStageMotors(params);
				calibrationDetails = params.createEnergyCalibration();
			}catch(Exception e) {
				logger.warn("Problem setting up energy calibration details and sample stage motors", e);
			}
		} else {
			// No motor parameters available, don't select anything
			SampleStageMotors.INSTANCE.setSelectedMotors(new ExperimentMotorPostion[] {});
		}
	}

	private void saveParameterBean() {
		try {
			TimeResolvedExperimentParameters params = getParametersBeanFromCurrentSettings();
			EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(SINGLE_SPECTRUM_PARAMETER_BEAN_STORE_KEY, params.toXML());
		} catch (DeviceException e) {
			logger.error("Problem saving TimeResolvedExperimentParameters from GUI settings", e);
		}
	}

	public void saveSettings() {
		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(SINGLE_SPECTRUM_MODEL_DATA_STORE_KEY, this);
		saveParameterBean();
	}

	private String buildScanCommand() {
		StringBuilder builder = new StringBuilder("from gda.scan.ede import SingleSpectrumScan; \n");
		int noOfAccumulations;
		if (experimentDataModel.isUseNoOfAccumulationsForI0()) {
			noOfAccumulations = experimentDataModel.getI0NumberOfAccumulations();
		} else {
			noOfAccumulations = itNumberOfAccumulations;
		}
		// use %g format rather than %f for I0 and It integration times to avoid rounding to 0 for small values <1msec (i.e. requiring >6 decimal places).
		builder.append(
				String.format(SINGLE_JYTHON_DRIVER_OBJ + " = SingleSpectrumScan(%g, %d, %g, %d, mapToJava(%s), mapToJava(%s), \"%s\", \"%s\", \"%s\"); \n",
						ExperimentUnit.MILLI_SEC.convertTo(experimentDataModel.getI0IntegrationTime(), ExperimentUnit.SEC),
						noOfAccumulations,
						ExperimentUnit.MILLI_SEC.convertTo(itIntegrationTime, ExperimentUnit.SEC),
						itNumberOfAccumulations,
						SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
						SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.It),
						DetectorModel.INSTANCE.getCurrentDetector().getName(),
						DetectorModel.TOPUP_CHECKER,
						DetectorModel.SHUTTER_NAME));

		builder.append(String.format(SINGLE_JYTHON_DRIVER_OBJ + ".setUseFastShutter(%s);", experimentDataModel.getUseFastShutter() ? "True" : "False" ) );
		builder.append(String.format(SINGLE_JYTHON_DRIVER_OBJ + ".setFastShutterName(\"%s\");", DetectorModel.FAST_SHUTTER_NAME ) );
		builder.append(String.format(SINGLE_JYTHON_DRIVER_OBJ + ".setUseTopupChecker(%s);", getUseTopupCheckerForIt() ? "True" : "False" ) );

		if (SampleStageMotors.INSTANCE.isUseIref()) {
			builder.append(String.format(SINGLE_JYTHON_DRIVER_OBJ + ".setIRefParameters(mapToJava(%s), %f, %d);",
					SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.IRef),
					ExperimentUnit.MILLI_SEC.convertTo(experimentDataModel.getIrefIntegrationTime(), ExperimentUnit.SEC), experimentDataModel.getIrefNoOfAccumulations()));
		}
		builder.append(String.format(SINGLE_JYTHON_DRIVER_OBJ + ".setFileNameSuffix(\"%s\");", experimentDataModel.getFileNameSuffix()));
		builder.append(String.format(SINGLE_JYTHON_DRIVER_OBJ + ".setSampleDetails(\"%s\");", experimentDataModel.getSampleDetails()));

		addScannablesMethodCallToCommand(SINGLE_JYTHON_DRIVER_OBJ, builder);

		addAccumulationReadoutTimeToMethodCall(SINGLE_JYTHON_DRIVER_OBJ, builder);

		try {
			TimeResolvedExperimentParameters parameters = getParametersBeanFromCurrentSettings();
			String paramString = parameters.toXML().replace("\n", " "); // Serialized xml string of bean
			builder.append(String.format(SINGLE_JYTHON_DRIVER_OBJ + ".setParameterBean('%s'); \n", paramString));
		} catch (DeviceException e) {
			logger.warn("Problem adding TimeResolvedExperimentParameters to experiment object", e);
		}

		return builder.toString();
	}

	private void addAccumulationReadoutTimeToMethodCall(String objectName, StringBuilder builder) {
		if ( DetectorModel.INSTANCE.getCurrentDetector().getDetectorData() instanceof FrelonCcdDetectorData ) {
			// Detector accumulation readout time (converted from default units[ns] to seconds)
			double accumulationReadoutTimeSecs = ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(DetectorModel.INSTANCE.getAccumulationReadoutTime(), ExperimentUnit.SEC);
			builder.append(String.format("%s.setAccumulationReadoutTime(%g);", objectName, accumulationReadoutTimeSecs) );
		}
	}

	protected void addScannablesMethodCallToCommand(String expObject, StringBuilder builder) {
		Map<String,String> scannablesToMonitor = experimentDataModel.getScannablesToMonitor();
		if (scannablesToMonitor != null) {
			for(String name : scannablesToMonitor.keySet()) {
				String pv = scannablesToMonitor.get(name);
				if (pv.length()==0) {
					// add name of scannable
					builder.append(expObject + ".addScannableToMonitorDuringScan(\'"+name+"\');\n");
				} else {
					// add name of scannable and pv
					builder.append(expObject + ".addScannableToMonitorDuringScan(\'"+pv+"\', \'"+name+"\');\n");
				}
			}
		}
	}

	private static enum ScanJobName {
		DARK_I0("Running I0 Dark scan"),
		DAR_It("Running It Dark scan"),
		I0("Running I0 scan"),
		It("Running It scan");
		String text;
		private ScanJobName(String value) {
			text = value;
		}

		public String getText() {
			return text;
		}
	}

	private class ScanJob extends Job implements IObserver {
		private IProgressMonitor monitor;
		private ScanJobName scanJobName;
		public ScanJob(String name) {
			super(name);
			scanJobName = ScanJobName.DARK_I0;
		}

		@Override
		public void update(Object source, Object arg) {
			if (arg instanceof JythonServerStatus) {
				JythonServerStatus status = (JythonServerStatus) arg;
				if (SingleSpectrumCollectionModel.this.isScanning() && JythonStatus.RUNNING == status.scanStatus) {
					monitor.subTask(scanJobName.getText());
					if (scanJobName.ordinal() <  ScanJobName.values().length - 1) {
						scanJobName = ScanJobName.values()[scanJobName.ordinal() + 1];
					}
				}
				if (SingleSpectrumCollectionModel.this.isScanning() && JythonStatus.IDLE == status.scanStatus) {
					monitor.worked(1);
				}
			}
		}

		@Override
		protected IStatus run(IProgressMonitor monitor) {
			this.monitor = monitor;
			Display.getDefault().syncExec(new Runnable() {
				@Override
				public void run() {
					SingleSpectrumCollectionModel.this.setScanning(true);
				}
			});
			monitor.beginTask("Starting " + ScanJobName.values().length + " tasks.", ScanJobName.values().length);
			try {
				String command = buildScanCommand();
				logger.info("Sending command: " + command);

				InterfaceProvider.getCommandRunner().runCommand(command);
				// give the previous command a chance to run before calling doCollection()
				Thread.sleep(150);
				final String resultFileName = InterfaceProvider.getCommandRunner().evaluateCommand(SINGLE_JYTHON_DRIVER_OBJ + ".runExperiment()");
				if (resultFileName == null) {
					//this does not stop data collection to Nexus file, just affect ASCii.
					throw new Exception("Unable to do collection. Result filename from server is NULL.");
				}
				Display.getDefault().syncExec(new Runnable() {
					@Override
					public void run() {
						try {
							SingleSpectrumCollectionModel.this.setFileName(resultFileName);
						} catch (Exception e) {
							UIHelper.showWarning("Error while loading data from saved file", e.getMessage());
						}
					}
				});
			} catch (Exception e) {
				UIHelper.showWarning("Error while scanning or canceled", e.getMessage());
			} finally {
				monitor.done();
				Display.getDefault().syncExec(new Runnable() {
					@Override
					public void run() {
						SingleSpectrumCollectionModel.this.setScanning(false);
					}
				});
			}
			return Status.OK_STATUS;
		}

		@Override
		protected void canceling() {
			doStop();
		}
	}

	public ExperimentDataModel getExperimentDataModel() {
		return experimentDataModel;
	}

	public void doCollection(boolean forExperiment, String fileNameSuffix, String sampleDetails) throws Exception {
		if (!forExperiment) {
			experimentDataModel.setFileNameSuffix(elementSymbol + "_cal");
		} else {
			experimentDataModel.setFileNameSuffix(fileNameSuffix);
			experimentDataModel.setSampleDetails(sampleDetails);
		}

		if (DetectorModel.INSTANCE.getCurrentDetector() == null) {
			throw new DetectorUnavailableException();
		}
		job.schedule();
	}

	public void setCurrentElement(String elementSymbol) {
		this.elementSymbol = elementSymbol;
	}


	public boolean isSelectAlignmentStage() {
		return selectAlignmentStage;
	}

	public void setSelectAlignmentStage(boolean selectAlignmentStage) {
		this.firePropertyChange(ALIGNMENT_STAGE_SELECTION, this.selectAlignmentStage, this.selectAlignmentStage = selectAlignmentStage);
	}

	public void setFileName(String value) {
		firePropertyChange(FILE_NAME_PROP_NAME, fileName, fileName = value);
	}

	public String getFileName() {
		return fileName;
	}

	public boolean isScanning() {
		return scanning;
	}

	protected void setScanning(boolean value) {
		this.firePropertyChange(SCANNING_PROP_NAME, scanning, scanning = value);
	}

	public double getItIntegrationTime() {
		return itIntegrationTime;
	}

	public void setItIntegrationTime(double value) {
		firePropertyChange(IT_INTEGRATION_TIME_PROP_NAME, itIntegrationTime, itIntegrationTime = value);
	}

	public int getItNumberOfAccumulations() {
		return itNumberOfAccumulations;
	}

	public void setItNumberOfAccumulations(int value) {
		firePropertyChange(IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME, itNumberOfAccumulations, itNumberOfAccumulations = value);
	}


	public AlignmentStageScannable.Location getHoleLocationForAlignment() {
		return holeLocationForAlignment;
	}

	public AlignmentStageScannable.Location getFoilLocationForAlignment() {
		return foilLocationForAlignment;
	}

	public boolean getUseTopupCheckerForIt() {
		return useTopupCheckerForIt;
	}

	public void setUseTopupCheckerForIt(boolean useTopupCheckerForIt) {
		this.firePropertyChange(USE_TOPUP_CHECKER_FOR_IT_PROP_NAME, this.useTopupCheckerForIt, this.useTopupCheckerForIt = useTopupCheckerForIt);
	}

	public CalibrationDetails getCalibrationDetails() {
		return calibrationDetails;
	}

	public void setCalibrationDetails(CalibrationDetails calibrationDetails) {
		this.calibrationDetails = calibrationDetails;
	}

	public void save() throws DetectorUnavailableException {
		if (DetectorModel.INSTANCE.getCurrentDetector() == null) {
			throw new DetectorUnavailableException();
		}
		InterfaceProvider.getCommandRunner().runCommand("alignment_stage.saveDeviceFromCurrentMotorPositions(\"slits\")");
	}

	public void doStop() {
		if (this.isScanning()) {
			JythonServerFacade.getInstance().requestFinishEarly();
		}
	}
}
