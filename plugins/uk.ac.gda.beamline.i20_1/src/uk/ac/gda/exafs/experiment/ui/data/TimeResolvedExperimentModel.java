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

package uk.ac.gda.exafs.experiment.ui.data;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Vector;

import org.dawnsci.ede.CalibrationDetails;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.gson.Gson;
import com.google.gson.annotations.Expose;

import gda.device.DeviceException;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerStatus;
import gda.jython.JythonStatus;
import gda.jython.scriptcontroller.Scriptcontroller;
import gda.observable.IObserver;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.TimeResolvedExperiment;
import gda.scan.ede.TimeResolvedExperimentParameters;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.EdeDataStore;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors.ExperimentMotorPostionType;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.TimingGroup.InputTriggerLemoNumbers;

public class TimeResolvedExperimentModel extends ObservableModel {

	private static final double INITIAL_INTEGRATION_TIME = ExperimentUnit.MILLI_SEC.convertToDefaultUnit(0.001d);

	public static final int TOP_UP_DURATION_IN_SECONDS = 10;

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedExperimentModel.class);

	protected static final String TIMING_GROUPS_OBJ_NAME = "timingGroups";

	protected static Gson gson = new Gson();

	public static final String EXTERNAL_TRIGGER_DETAILS = "tfg_external_trigger_details";
	protected ExternalTriggerSetting externalTriggerSetting;

	private static final double IT_COLLECTION_START_TIME = 0.0;
	private static final double DEFAULT_INITIAL_EXPERIMENT_TIME = 20; // Should be > 0

	private static final String LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY = "LINEAR_TIME_RESOLVED_EXPERIMENT_DATA";

	private static final String LINEAR_EXPERIMENT_OBJ = "linearExperiment";

	public static final String IT_COLLECTION_DURATION_PROP_NAME = "itCollectionDuration";

	public static final String TOTAL_IT_COLLECTION_DURATION_PROP_NAME = "totalItCollectionDuration";

	public static final String NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH_PROP_NAME = "noOfSecPerSpectrumToPublish";
	private double noOfSecPerSpectrumToPublish = TimeResolvedExperiment.DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH;

	public static final String CURRENT_SCANNING_SPECTRUM_PROP_NAME = "currentScanningSpectrum";
	private SpectrumModel currentScanningSpectrum;

	public static final String SCANNING_PROP_NAME = "scanning";
	private boolean scanning;

	public static final String SCAN_DATA_SET_PROP_NAME = "scanDataSet";

	private static final int MAX_TOP_UP_TIMES = 10;
	private static final int DURATION_BETWEEN_TOP_UP_IN_MINUTES = 10;

	public static final String GENERATE_ASCII_DATA = "generateAsciiData";
	private boolean generateAsciiData;

	private DoubleDataset[] scanDataSet;

	private final WritableList groupList = new WritableList(new ArrayList<TimingGroupUIModel>(), TimingGroupUIModel.class);

	private ScanJob experimentDataCollectionJob;

	public static final String UNIT_PROP_NAME = "unit";
	private ExperimentUnit unit = ExperimentUnit.SEC;

	public static final String UNIT_IN_STRING_PROP_NAME = "unitInStr";

	protected static final String IO_IREF_DATA_SUFFIX_KEY = "_IO_IREF_DATA";

	protected static final String FAST_SHUTTER_KEY = "_USE_FAST_SHUTTER_DATA";

	private static final String SCANNABLE_DATA_KEY = "_SCANNABLES_TO_MONITOR_DATA";

	@Expose
	private String unitInStr = unit.getUnitText();

	@Expose
	private ExperimentDataModel experimentDataModel;

	protected final TimeIntervalDataModel timeIntervalData = new TimeIntervalDataModel() {
		@Override
		public void dispose() {
			// Nothing to dispose
		}
	};

	public void setup() {
		groupList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						TimingGroupUIModel timingGroupModel = ((TimingGroupUIModel) element);
						timingGroupModel.dispose();
					}

					@Override
					public void handleAdd(int index, Object element) {
					}
				});
			}
		});

		experimentDataCollectionJob = new ScanJob("Linear experiment scan");
		InterfaceProvider.getJSFObserver().addIObserver(experimentDataCollectionJob);
		Optional<Scriptcontroller> controller = Finder.getInstance().findOptional(EdeExperiment.PROGRESS_UPDATER_NAME);
		if (controller.isPresent()) {
			controller.get().addIObserver(experimentDataCollectionJob);
		}
		experimentDataCollectionJob.setUser(true);
		loadSavedGroups();
		loadGenerateAsciiData();
	}

	public void addGroupListChangeListener(IListChangeListener listener) {
		groupList.addListChangeListener(listener);
	}

	public void removeGroupListChangeListener(IListChangeListener listener) {
		groupList.removeListChangeListener(listener);
	}

	/**
	 * Create a new TimeResolvedExperimentParameters object from the current gui settings.
	 * @return TimeResolvedExperimentParameters object
	 * @throws DeviceException
	 */
	public TimeResolvedExperimentParameters getParametersBeanFromCurrentSettings() throws DeviceException {
		TimeResolvedExperimentParameters params = new TimeResolvedExperimentParameters();
		params.setI0AccumulationTime(unit.getWorkingUnit().convertTo(experimentDataModel.getI0IntegrationTime(), ExperimentUnit.SEC));
		if (experimentDataModel.isUseNoOfAccumulationsForI0()) {
			params.setI0NumAccumulations(experimentDataModel.getI0NumberOfAccumulations());
		}
		params.setItTimingGroups(getTimingGroupList());
		params.setI0MotorPositions(SampleStageMotors.INSTANCE.getSelectedMotorsMap(ExperimentMotorPostionType.I0));
		params.setItMotorPositions(SampleStageMotors.INSTANCE.getSelectedMotorsMap(ExperimentMotorPostionType.It));
		params.setDetectorName(DetectorModel.INSTANCE.getCurrentDetector().getName());
		params.setTopupMonitorName(DetectorModel.TOPUP_CHECKER);
		params.setBeamShutterScannableName(DetectorModel.SHUTTER_NAME);
		params.setItTriggerOptions(externalTriggerSetting.getTfgTrigger());

		params.setDoIref(SampleStageMotors.INSTANCE.isUseIref());
		if (params.getDoIref()) {
			params.setiRefMotorPositions(SampleStageMotors.INSTANCE.getSelectedMotorsMap(ExperimentMotorPostionType.IRef));

			if (experimentDataModel.isUseNoOfAccumulationsForI0()) {
				params.setI0ForIRefNoOfAccumulations(experimentDataModel.getI0NumberOfAccumulations());
			} else {
				params.setI0ForIRefNoOfAccumulations(experimentDataModel.getIrefNoOfAccumulations());
			}
			params.setIrefIntegrationTime(unit.getWorkingUnit().convertTo(experimentDataModel.getIrefIntegrationTime(), ExperimentUnit.SEC));
			params.setIrefNoOfAccumulations(experimentDataModel.getIrefNoOfAccumulations());
		}

		params.setFileNameSuffix(experimentDataModel.getFileNameSuffix());
		params.setSampleDetails(experimentDataModel.getSampleDetails());
		params.setGenerateAsciiData(getGenerateAsciiData());
		params.setUseFastShutter(experimentDataModel.getUseFastShutter());
		params.setFastShutterName(DetectorModel.FAST_SHUTTER_NAME);
		params.setScannablesToMonitorDuringScan(experimentDataModel.getScannablesToMonitor());

		// Set the energy calibration using parameters from 'Single collection'
		CalibrationDetails calibrationDetails = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel().getCalibrationDetails();
		params.setCalibrationDetails(calibrationDetails);

		return params;
	}


	/** Set current experiment model from TimeResolvedExperimentParameters object.
	 * This updates the gui as well from property change events fired during the model update.
	 * @param params
	 */
	public void setupFromParametersBean(TimeResolvedExperimentParameters params) {
		experimentDataModel.setFileNameSuffix(params.getFileNameSuffix());
		experimentDataModel.setSampleDetails(params.getSampleDetails());
		setGenerateAsciiData(params.getGenerateAsciiData());
		experimentDataModel.setUseFastShutter(params.getUseFastShutter());

		setupExternalTriggerSettings(params.getItTriggerOptions());

		double i0Time = ExperimentUnit.SEC.convertTo(params.getI0AccumulationTime(), ExperimentUnit.DEFAULT_EXPERIMENT_UNIT_FOR_I0_IREF);
		experimentDataModel.setI0IntegrationTime(i0Time);
		if (params.getI0NumAccumulations()>0) {
			experimentDataModel.setI0NumberOfAccumulations(params.getI0NumAccumulations());
			experimentDataModel.setUseNoOfAccumulationsForI0(true);
		} else {
			experimentDataModel.setUseNoOfAccumulationsForI0(false);
		}

		// IRef num accumulations, integration time
		if (params.getDoIref()) {
			double irefTime = ExperimentUnit.SEC.convertTo(params.getIrefIntegrationTime(), ExperimentUnit.DEFAULT_EXPERIMENT_UNIT_FOR_I0_IREF);
			experimentDataModel.setIrefIntegrationTime(irefTime);
			experimentDataModel.setIrefNoOfAccumulations(params.getIrefNoOfAccumulations());
		}

		ExperimentMotorPostion[] pos = SampleStageMotors.INSTANCE.setupExperimentMotorTargetPositions(params);
		SampleStageMotors.INSTANCE.setSelectedMotors(pos);
		SampleStageMotors.INSTANCE.setUseIref(params.getDoIref());

		setTimingGroupUIModelFromList(params.getItTimingGroups());

		experimentDataModel.setScannablesToMonitor(params.getScannablesToMonitorDuringScan());
	}

	/**
	 * Create TiminGroupUI list used for UI setup from a list of TimingGroups
	 * @param timingGroupList List<TimingGroup>
	 */
	protected void setTimingGroupUIModelFromList(List<TimingGroup> timingGroupList) {
		// Don't clear all groups, (i.e. groupsList.clear()) since gui updates to reflect this (via listeners), and all the controls disappear.
		// And they don't come back after list has been updated...

		// Remove all but one of the ui timing groups.
		while(groupList.size()>1) {
			// indices of elements are reduced by 1 after removing 0th element, so just keep removing the first one to clear the list...
			removeFromInternalGroupList((TimingGroupUIModel)groupList.get(0));
		}

		double startTime = 0;
		double endTime = 0;
		boolean firstGroup = true;
		for (TimingGroup timingGroup : timingGroupList) {
			TimingGroupUIModel uiTimingGroup =  null;
			if (firstGroup) {
				// Re-use first timing group
				uiTimingGroup = (TimingGroupUIModel)groupList.get(0);
			} else {
				// Create new timing group
				uiTimingGroup = new TimingGroupUIModel(unit.getWorkingUnit(), this);
			}

			uiTimingGroup.setName(timingGroup.getLabel());
			uiTimingGroup.setUseExternalTrigger(timingGroup.isGroupTrig());
			uiTimingGroup.setExternalTriggerAvailable(timingGroup.isGroupTrig());
			uiTimingGroup.setNumberOfSpectrum(timingGroup.getNumberOfFrames());
			uiTimingGroup.setNoOfAccumulations(timingGroup.getNumberOfScansPerFrame());
			// Conversion factor to go from seconds to default experiment units (nano seconds) (i.e. 1e9)
			double convertSecWorkingUnit = ExperimentUnit.SEC.convertTo(1.0, ExperimentUnit.DEFAULT_EXPERIMENT_UNIT);
			uiTimingGroup.setTimePerSpectrum(convertSecWorkingUnit*timingGroup.getTimePerFrame());
			uiTimingGroup.setIntegrationTime(convertSecWorkingUnit*timingGroup.getTimePerScan());
			uiTimingGroup.setDelay(convertSecWorkingUnit*timingGroup.getPreceedingTimeDelay());
			uiTimingGroup.setUseTopupChecker(timingGroup.getUseTopChecker());
			startTime = endTime;
			// endtime, including delay at end of group
			endTime = startTime + convertSecWorkingUnit*(timingGroup.getTimePerFrame()*timingGroup.getNumberOfFrames() + timingGroup.getPreceedingTimeDelay());
			uiTimingGroup.resetInitialTime(startTime, endTime-startTime, timingGroup.getPreceedingTimeDelay(), convertSecWorkingUnit*timingGroup.getTimePerFrame());

			// enable external trigger button for first group only
			uiTimingGroup.setExternalTriggerAvailable(firstGroup);

			if (!firstGroup) {
				uiTimingGroup.setExternalTriggerAvailable(false);
				addToInternalGroupList(uiTimingGroup);
			}
			firstGroup = false;
		}
	}

	private void setupExternalTriggerSettings(TFGTrigger tfgTrigger) {
		if (tfgTrigger == null) {
			tfgTrigger = new TFGTrigger();
			try {
				tfgTrigger.getSampleEnvironment().add(TriggerableObject.createNewSampleEnvEntry());
			} catch (Exception e) {
				logger.error("Unable to create sample environment entry", e);
			}
		}
		externalTriggerSetting = new ExternalTriggerSetting(tfgTrigger);

		externalTriggerSetting.getTfgTrigger().addPropertyChangeListener(TFGTrigger.TOTAL_TIME_PROP_NAME,
				evt -> TimeResolvedExperimentModel.this.firePropertyChange(TOTAL_IT_COLLECTION_DURATION_PROP_NAME, null, getTotalItCollectionDuration()));

	}

	private void loadSavedGroups() {

		TFGTrigger savedExternalTriggerSetting = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(EXTERNAL_TRIGGER_DETAILS, TFGTrigger.class);
		setupExternalTriggerSettings(savedExternalTriggerSetting);

		TimingGroupUIModel[] savedGroups = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(getDataStoreKey(), TimingGroupUIModel[].class);
		ExperimentDataModel savedExperimentDataModel = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(getI0IRefDataKey(), ExperimentDataModel.class);
		if (savedExperimentDataModel == null) {
			experimentDataModel = new ExperimentDataModel();
		} else {
			experimentDataModel = savedExperimentDataModel;
		}
		experimentDataModel.addPropertyChangeListener(
				evt -> EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(getI0IRefDataKey(), experimentDataModel));

		if (savedGroups == null) {
			timeIntervalData.setTimes(IT_COLLECTION_START_TIME, unit.convertToDefaultUnit(DEFAULT_INITIAL_EXPERIMENT_TIME));
			createNewItGroup();
			return;
		}

		for (TimingGroupUIModel loadedGroup : savedGroups) {
			TimingGroupUIModel timingGroup = new TimingGroupUIModel(unit.getWorkingUnit(), this);
			timingGroup.setName(loadedGroup.getName());
			timingGroup.setUseExternalTrigger(loadedGroup.isUseExternalTrigger());
			timingGroup.setExternalTriggerAvailable(loadedGroup.isExternalTriggerAvailable());
			timingGroup.setExternalTriggerInputLemoNumber(loadedGroup.getExternalTriggerInputLemoNumber());
			double delay = 0.0;
			if (loadedGroup.getDelay() > 0) {
				delay = loadedGroup.getDelay();
			}
			// TODO Refactor this!
			timingGroup.resetInitialTime(loadedGroup.getStartTime(), loadedGroup.getEndTime() - (delay + loadedGroup.getStartTime()), delay, loadedGroup.getTimePerSpectrum());
			timingGroup.setRealTimePerSpectrum( loadedGroup.getRealTimePerSpectrum() );
			timingGroup.setIntegrationTime(loadedGroup.getIntegrationTime());
			timingGroup.setAccumulationReadoutTime(loadedGroup.getAccumulationReadoutTime());
			if (loadedGroup.getDelayBetweenSpectrum() > 0) {
				timingGroup.setDelayBetweenSpectrum(loadedGroup.getDelayBetweenSpectrum());
			}
			timingGroup.setUseTopupChecker( loadedGroup.getUseTopupChecker() );
			addToInternalGroupList(timingGroup);
		}
		updateCollectionDuration();
	}

	protected String getDataStoreKey() {
		return LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY;
	}

	public List<?> getGroupList() {
		return groupList;
	}

	public void splitGroup(TimingGroupUIModel groupToSplit) {
		double duration = groupToSplit.getDuration();
		double endTime = groupToSplit.getEndTime();
		double startTime = groupToSplit.getStartTime();
		double timePerSpectrum=groupToSplit.getTimePerSpectrum();
		int numberOfSpectrum=groupToSplit.getNumberOfSpectrum();
		groupToSplit.resetInitialTime(startTime, duration / 2, 0, timePerSpectrum);
		groupToSplit.setNumberOfSpectrum(numberOfSpectrum/2);
		TimingGroupUIModel newGroup = new TimingGroupUIModel(unit.getWorkingUnit(), this);
		newGroup.setName("Group " + (groupList.indexOf(groupToSplit) + 2));
		newGroup.setTimePerSpectrum(groupToSplit.getTimePerSpectrum());
		newGroup.setIntegrationTime(groupToSplit.getIntegrationTime());
		newGroup.setAccumulationReadoutTime(groupToSplit.getAccumulationReadoutTime());
		newGroup.setNumberOfSpectrum(numberOfSpectrum-groupToSplit.getNumberOfSpectrum());
		addToInternalGroupList(newGroup, groupList.indexOf(groupToSplit) + 1);
		newGroup.resetInitialTime(groupToSplit.getEndTime(), endTime - groupToSplit.getEndTime(), 0, timePerSpectrum);
		for (int i = groupList.indexOf(groupToSplit) + 1; i < groupList.size(); i++) {
			((TimingGroupUIModel) groupList.get(i)).setName("Group " + i);
		}
	}

	public TimingGroupUIModel createNewItGroup() {
		TimingGroupUIModel newGroup = new TimingGroupUIModel(unit.getWorkingUnit(), this);
		newGroup.setName("Group " + groupList.size());
		addToInternalGroupList(newGroup);
		resetInitialGroupTimes(timeIntervalData.getDuration() / groupList.size());
		newGroup.setIntegrationTime(INITIAL_INTEGRATION_TIME);
		newGroup.setAccumulationReadoutTime(DetectorModel.INSTANCE.getAccumulationReadoutTime());
		newGroup.setExternalTriggerAvailable(true);
		newGroup.setExternalTriggerInputLemoNumber(InputTriggerLemoNumbers.ZERO);
		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(this.getDataStoreKey(), groupList);
		return newGroup;
	}

	private final PropertyChangeListener groupPropertyChangeListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			TimingGroupUIModel group = (TimingGroupUIModel) evt.getSource();
			if (evt.getPropertyName().equals(TimeIntervalDataModel.END_TIME_PROP_NAME)) {
				if (groupList.indexOf(evt.getSource()) < groupList.size() - 1) {
					TimingGroupUIModel nextGroup = (TimingGroupUIModel) groupList.get(groupList.indexOf(evt.getSource()) + 1);
					nextGroup.moveTo(group.getEndTime());
				}
				updateCollectionDuration();
			} else if (evt.getPropertyName().equals(TimingGroupUIModel.NO_OF_SPECTRUM_PROP_NAME) ){
				group.setNumberOfSpectrum((int)evt.getNewValue());
			} else if (evt.getPropertyName().equals(TimingGroupUIModel.ACCUMULATION_READOUT_TIME_PROP_NAME) ){
				group.setAccumulationReadoutTime((double)evt.getNewValue());
			}
			savePreferenceData();
			// ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(TimeResolvedExperimentModel.this.getDataStoreKey(), groupList);
		}
	};

	private void addToInternalGroupList(TimingGroupUIModel newGroup) {
		newGroup.addPropertyChangeListener(groupPropertyChangeListener);
		groupList.add(newGroup);
	}

	private void addToInternalGroupList(TimingGroupUIModel newGroup, int index) {
		newGroup.addPropertyChangeListener(groupPropertyChangeListener);
		groupList.add(index, newGroup);
	}

	private void removeFromInternalGroupList(TimingGroupUIModel group) {
		group.removePropertyChangeListener(groupPropertyChangeListener);
		groupList.remove(group);
	}

	private int rowIndexOfGroup = 0;

	public int getIndexOfSelectedRow() {
		return rowIndexOfGroup;
	}
	public void removeGroup(TimingGroupUIModel group) throws Exception {
		if (groupList.size() > 1 && groupList.indexOf(group) > 0) {

			TimingGroupUIModel groupToExpend = (TimingGroupUIModel) groupList.get(groupList.indexOf(group) - 1);

			// TODO index of group to remove.
			rowIndexOfGroup = groupList.indexOf(group);
			if ( rowIndexOfGroup > groupList.size()-2 ) {
				rowIndexOfGroup--;
			}

			removeFromInternalGroupList(group);
			groupToExpend.setEndTime(group.getEndTime());
			savePreferenceData();
			// ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(getDataStoreKey(), groupList);

		}
	}

	public void doCollection(String fileNameSuffix, String sampleDetails) {
		experimentDataModel.setFileNameSuffix(fileNameSuffix);
		experimentDataModel.setSampleDetails(sampleDetails);
		experimentDataCollectionJob.schedule();
	}

	// Jython command build
	// TODO This is very messy!
	protected String buildScanCommand() {
		StringBuilder builder = new StringBuilder("from gda.scan.ede import TimeResolvedExperiment;");
		// use %g format rather than %f for I0 and It integration times to avoid rounding to 0 for small values <1msec (i.e. requiring >6 decimal places). imh 7/12/2015
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + " = TimeResolvedExperiment(%g",
				ExperimentUnit.DEFAULT_EXPERIMENT_UNIT_FOR_I0_IREF.convertTo(this.getExperimentDataModel().getI0IntegrationTime(), ExperimentUnit.SEC)) );

		builder.append(String.format(", %s, mapToJava(%s), mapToJava(%s), \"%s\", \"%s\", \"%s\");\n",
				"None",
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.It),
				DetectorModel.INSTANCE.getCurrentDetector().getName(),
				DetectorModel.TOPUP_CHECKER,
				DetectorModel.SHUTTER_NAME));

		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setNoOfSecPerSpectrumToPublish(%f);\n", this.getNoOfSecPerSpectrumToPublish()));
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setFileNameSuffix(\"%s\");\n", this.getExperimentDataModel().getFileNameSuffix()));
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setWriteAsciiData(%s);\n", getGenerateAsciiData() ? "True" : "False"));
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setSampleDetails(\"%s\");\n", this.getExperimentDataModel().getSampleDetails()));
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setUseFastShutter(%s);\n", this.getExperimentDataModel().getUseFastShutter() ? "True" : "False" ) );
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setFastShutterName(\"%s\");\n", DetectorModel.FAST_SHUTTER_NAME ) );

		// Add timing groups
		addTimingGroupsMethodCallToCommand(LINEAR_EXPERIMENT_OBJ, builder);

		// Add I0 accumulations
		addI0AccumulationMethodCallToCommand(LINEAR_EXPERIMENT_OBJ, builder);

		// Add external Tfg command
		addItTriggerMethodCallToCommand(LINEAR_EXPERIMENT_OBJ, builder);

		// Add Iref commands
		addIRefMethodCallStrToCommand(LINEAR_EXPERIMENT_OBJ, builder);

		// Add names of pvs/scannables to be monitored
		addScannablesMethodCallToCommand(LINEAR_EXPERIMENT_OBJ, builder);

		// Add xml bean
		try {
			TimeResolvedExperimentParameters params = getParametersBeanFromCurrentSettings();
			String paramString = params.toXML().replace("\n", " "); // Serialized xml string of bean
			builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setParameterBean('%s'); \n", paramString));
		} catch (DeviceException e) {
			logger.warn("Problem adding TimeResolvedExperimentParameters to experiment object", e);
		}

		builder.append(LINEAR_EXPERIMENT_OBJ + ".runExperiment();");
		return builder.toString();
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

	/**
	 * Add call to set timing groups to command string
	 * @param expObject
	 * @param builder
	 */
	protected void addTimingGroupsMethodCallToCommand(String expObject, StringBuilder builder) {
		// Setup timing groups
		List<TimingGroup> groups = getTimingGroupList();
		builder.append(expObject+".setTimingGroups(\'"+gson.toJson(groups)+"\');\n");
	}

	/**
	 * Add call to set number of I0 accumulations to command string
	 * @param expObject
	 * @param builder
	 */
	protected void addI0AccumulationMethodCallToCommand(String expObject, StringBuilder builder) {
		// Set number of I0 accumulations (if different from It accumulations)
		if (this.getExperimentDataModel().isUseNoOfAccumulationsForI0()) {
			builder.append(String.format(expObject + ".setNumberI0Accumulations(%d);\n", this.getExperimentDataModel().getI0NumberOfAccumulations()));
		}
	}

	/**
	 * Add call to set number Tfg trigger options to command string
	 * @param expObject
	 * @param builder
	 */
	protected void addItTriggerMethodCallToCommand(String expObject, StringBuilder builder) {
		// Set number of I0 accumulations (if different from It accumulations)
		if (this.getTimingGroupList().get(0).isGroupTrig()) {
			String tfgTriggerString = gson.toJson(externalTriggerSetting.getTfgTrigger());
			builder.append(String.format(expObject + ".setItTriggerOptions(\'%s\');\n", tfgTriggerString));
		}
	}

	protected void addIRefMethodCallStrToCommand(String linearExperimentObj, StringBuilder builder) {
		if (!SampleStageMotors.INSTANCE.isUseIref()) {
			return;
		}

		int i0ForIRefNoOfAccumulations;
		int irefNoOfAccumulations = this.getExperimentDataModel().getIrefNoOfAccumulations();
		if (this.getExperimentDataModel().isUseNoOfAccumulationsForI0()) {
			i0ForIRefNoOfAccumulations = this.getExperimentDataModel().getI0NumberOfAccumulations();
		} else {
			i0ForIRefNoOfAccumulations = irefNoOfAccumulations;
		}
		double irefIntegrationTime = ExperimentUnit.DEFAULT_EXPERIMENT_UNIT_FOR_I0_IREF.convertTo(this.getExperimentDataModel().getIrefIntegrationTime(), ExperimentUnit.SEC);
		builder.append(String.format(linearExperimentObj + ".setIRefParameters(mapToJava(%s), mapToJava(%s), %g, %d, %g, %d);\n",
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.IRef),
				irefIntegrationTime,
				i0ForIRefNoOfAccumulations,
				irefIntegrationTime,
				irefNoOfAccumulations));
	}

	/**
	 * Create list of timing groups from UI settings.
	 * (Refactored from ScanJob class)
	 * @since 10/3/2017
	 */
	protected List<TimingGroup> getTimingGroupList() {
		final Vector<TimingGroup> timingGroups = new Vector<TimingGroup>();
		boolean isFrelon = DetectorModel.INSTANCE.getCurrentDetector().getDetectorData() instanceof FrelonCcdDetectorData;
		for (Object object : groupList) {
			TimingGroupUIModel uiTimingGroup = (TimingGroupUIModel) object;
			TimingGroup timingGroup = new TimingGroup();
			timingGroup.setLabel(uiTimingGroup.getName());
			timingGroup.setNumberOfFrames(uiTimingGroup.getNumberOfSpectrum());
			timingGroup.setNumberOfScansPerFrame(uiTimingGroup.getNoOfAccumulations());
			double timePerSpectrum = uiTimingGroup.getTimePerSpectrum();
			if (isFrelon) {
				timePerSpectrum = uiTimingGroup.getRealTimePerSpectrum();
			}
			timingGroup.setTimePerFrame(ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(timePerSpectrum, ExperimentUnit.SEC)); // convert to S

			timingGroup.setTimePerScan(ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(uiTimingGroup.getIntegrationTime(), ExperimentUnit.SEC)); // convert to S
			timingGroup.setPreceedingTimeDelay(ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(uiTimingGroup.getDelay(), ExperimentUnit.SEC)); // convert to S
			timingGroup.setGroupTrig(uiTimingGroup.isUseExternalTrigger());
			timingGroup.setUseTopupChecker(uiTimingGroup.getUseTopupChecker());
			// Set up lemo outs
			setupLemoOuts(timingGroup);
			timingGroups.add(timingGroup);
		}
		return timingGroups;
	}

	protected void setupLemoOuts(TimingGroup timingGroup) {
		timingGroup.setOutLemo0(true);
		timingGroup.setOutLemo1(true);
		timingGroup.setOutLemo2(true);
		timingGroup.setOutLemo3(true);
		timingGroup.setOutLemo4(true);
		timingGroup.setOutLemo5(true);
		timingGroup.setOutLemo6(true);
		timingGroup.setOutLemo7(true);
	}

	private class ScanJob extends Job implements IObserver {
		private static final int SCAN_DATA_SET_REPORT_INTERVAL_IN_MILLI = 1000;
		private IProgressMonitor monitor;
		private DoubleDataset currentNormalisedItData = null;
		private DoubleDataset currentEnergyData = null;

		public ScanJob(String name) {
			super(name);
		}

		@Override
		public void update(Object source, Object arg) {
			if (arg instanceof JythonServerStatus) {
				JythonServerStatus status = (JythonServerStatus) arg;
				if (TimeResolvedExperimentModel.this.isScanning() && JythonStatus.IDLE == status.scanStatus) {
					monitor.worked(1);
				}
			}
			else if (arg instanceof EdeExperimentProgressBean) {
				final EdeExperimentProgressBean edeExperimentProgress = (EdeExperimentProgressBean) arg;
				currentNormalisedItData = edeExperimentProgress.getData();
				currentNormalisedItData.setName("Normalised It");
				currentEnergyData = edeExperimentProgress.getEnergyData();
				currentEnergyData.setName("Energy");

				// TODO This is commented out to disable the marker feature to show currently scanning spectra

				//				final int currentFrameNumber = edeExperimentProgress.getProgress().getFrameNumOfThisSDP();
				//				final int currentGroupNumber = edeExperimentProgress.getProgress().getGroupNumOfThisSDP();
				//				Display.getDefault().asyncExec(new Runnable() {
				//					//					@Override
				//					//					public void run() {
				//					//						if (groupList.size() -1 < currentGroupNumber) {
				//					//							System.out.println(groupList.size());
				//					//							System.out.println(currentGroupNumber);
				//					//						}
				//					//						final TimingGroupUIModel currentGroup = (TimingGroupUIModel) groupList.get(currentGroupNumber);
				//					//						// TODO refactor the group to manage its own state
				//					//						TimeResolvedExperimentModel.this.setCurrentScanningSpectrum((SpectrumModel) currentGroup.getSpectrumList().get(currentFrameNumber));
				//					//					}
				//					//				});
			}
		}

		private Job createProgressReportingJob() {
			return new Job("Progress Report") {
				@Override
				protected IStatus run(IProgressMonitor monitor) {
					while(TimeResolvedExperimentModel.this.isScanning()) {
						setReceivedDataSet();
						try {
							Thread.sleep(SCAN_DATA_SET_REPORT_INTERVAL_IN_MILLI);
						} catch (InterruptedException e) {
							return Status.CANCEL_STATUS;
						}
					}
					setReceivedDataSet();
					return Status.OK_STATUS;
				}

				private void setReceivedDataSet() {
					if (currentNormalisedItData != null & currentEnergyData != null) {
						TimeResolvedExperimentModel.this.setScanDataSet(new DoubleDataset[] {currentEnergyData, currentNormalisedItData});
					}
				}
			};
		}

		@Override
		protected IStatus run(IProgressMonitor monitor) {
			this.monitor = monitor;
			monitor.beginTask("Scannable", 1);
			final Job progressReportingJob = createProgressReportingJob();
			progressReportingJob.setUser(false);
			currentNormalisedItData = null;
			currentEnergyData = null;
			try {
				Display.getDefault().syncExec(new Runnable() {
					@Override
					public void run() {
						String scanCommand = buildScanCommand();
						logger.info("Sending command: " + scanCommand);
						InterfaceProvider.getCommandRunner().runCommand(scanCommand);
					}
				});

			} catch (Exception e) {
				UIHelper.showWarning("Scanning has stopped", e.getMessage());
			} finally {
				monitor.done();
			}
			return Status.OK_STATUS;
		}

		@Override
		protected void canceling() {
			stopScan();
		}
	}

	public ExperimentDataModel getExperimentDataModel() {
		return experimentDataModel;
	}

	public TimeIntervalDataModel getTimeIntervalDataModel() {
		return timeIntervalData;
	}

	public void stopScan() {
		doStop();
	}

	public DoubleDataset[] getScanDataSet() {
		return scanDataSet;
	}

	public void setScanDataSet(final DoubleDataset[] value) {
		Display.getDefault().syncExec(new Runnable() {
			@Override
			public void run() {
				firePropertyChange(SCAN_DATA_SET_PROP_NAME, scanDataSet, scanDataSet = value);
			}
		});
	}

	public void setScanning(final boolean value) {
		Display.getDefault().asyncExec(new Runnable() {
			@Override
			public void run() {
				firePropertyChange(SCANNING_PROP_NAME, scanning, scanning = value);
			}
		});
	}

	public boolean isScanning() {
		return scanning;
	}

	public void doStop() {
		String stopCommand=LINEAR_EXPERIMENT_OBJ+".getMultiScan().getCurrentRunningScan().setSmartstop(True);";
		InterfaceProvider.getCommandRunner().runCommand(stopCommand);

		//		if (this.isScanning()) {
		//			JythonServerFacade.getInstance().requestFinishEarly();
		//		}
	}

	public SpectrumModel getCurrentScanningSpectrum() {
		return currentScanningSpectrum;
	}

	public void setCurrentScanningSpectrum(SpectrumModel value) {
		this.firePropertyChange(CURRENT_SCANNING_SPECTRUM_PROP_NAME, currentScanningSpectrum, currentScanningSpectrum = value);
	}

	public void updateCollectionDuration() {
		double experimentDuration = 0.0;
		int totalSpectra = 0;
		for (Object loadedGroup : groupList) {
			TimingGroupUIModel group = ((TimingGroupUIModel)loadedGroup);
			experimentDuration += group.getDuration();
			totalSpectra += group.getNumberOfSpectrum();
		}
		timeIntervalData.setTimes(IT_COLLECTION_START_TIME, experimentDuration);
		this.firePropertyChange(IT_COLLECTION_DURATION_PROP_NAME, null, getItCollectionDuration());
		this.firePropertyChange(TOTAL_IT_COLLECTION_DURATION_PROP_NAME, null, getTotalItCollectionDuration());
		externalTriggerSetting.getTfgTrigger().getDetectorDataCollection().setCollectionDuration(unit.convertTo(getItCollectionDuration(), ExperimentUnit.SEC));
		externalTriggerSetting.getTfgTrigger().getDetectorDataCollection().setNumberOfFrames(totalSpectra);
	}

	private void resetInitialGroupTimes(double groupDuration) {
		groupDuration = ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertToNearestFrame(groupDuration);
		double startTime = timeIntervalData.getStartTime();
		for (int i = 0; i < groupList.size(); i++) {
			TimingGroupUIModel group = (TimingGroupUIModel) groupList.get(i);
			if (i > 0) {
				TimingGroupUIModel previous = (TimingGroupUIModel) groupList.get(i-1);
				startTime = previous.getEndTime();
				group.setExternalTriggerAvailable(false);
			} else {
				group.setExternalTriggerAvailable(true);
			}
			group.setName("Group " + i);
			group.resetInitialTime(startTime, groupDuration, 0.0, groupDuration);
		}
	}

	public void setExperimentDuration(double value) {
		resetInitialGroupTimes(unit.convertToDefaultUnit(value) / groupList.size());
	}

	public void setupExperiment(ExperimentUnit unit, double duration, int noOfGroups) {
		timeIntervalData.setTimes(IT_COLLECTION_START_TIME, unit.convertToDefaultUnit(duration));
		this.setUnit(unit);
		groupList.clear();
		double timePerGroup = timeIntervalData.getDuration() / noOfGroups;
		for(int i = 0; i < noOfGroups; i++) {
			TimingGroupUIModel newGroup = new TimingGroupUIModel(unit.getWorkingUnit(), this);
			newGroup.setName("Group " + groupList.size());
			// TODO set time per spectrum
			newGroup.setTimePerSpectrum(timePerGroup); // Initially there is only 1 spectrum per group
			newGroup.setIntegrationTime(INITIAL_INTEGRATION_TIME);
			newGroup.setAccumulationReadoutTime(DetectorModel.INSTANCE.getAccumulationReadoutTime());
			addToInternalGroupList(newGroup);
		}
		resetInitialGroupTimes(timeIntervalData.getDuration() / groupList.size());
		savePreferenceData();
		// ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(this.getDataStoreKey(), groupList);
	}

	public double getItCollectionDuration() {
		return unit.convertFromDefaultUnit(timeIntervalData.getDuration());
	}

	public double getTotalItCollectionDuration() {
		return TFGTrigger.DEFAULT_DELAY_UNIT.convertTo(externalTriggerSetting.getTfgTrigger().getTotalTime(), unit);
	}

	public double getDurationInSec() {
		return ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(timeIntervalData.getDuration(), ExperimentUnit.SEC);
	}

	public ExperimentUnit getUnit() {
		return unit;
	}

	public String getUnitInStr() {
		return unitInStr;
	}

	public void setUnit(ExperimentUnit unit) {
		this.firePropertyChange(UNIT_PROP_NAME, this.unit, this.unit = unit);
		this.firePropertyChange(UNIT_IN_STRING_PROP_NAME, unitInStr, unitInStr = this.unit.getUnitText());
		for (Object object : getGroupList()) {
			((TimingGroupUIModel) object).setUnit(this.unit.getWorkingUnit());
		}
	}

	public double getNoOfSecPerSpectrumToPublish() {
		return noOfSecPerSpectrumToPublish;
	}

	public void setNoOfSecPerSpectrumToPublish(double noOfSecPerSpectrumToPublish) throws IllegalArgumentException {
		if (noOfSecPerSpectrumToPublish >= this.getDurationInSec()) {
			throw new IllegalArgumentException("Cannot be longer than experiment duration");
		}
		this.firePropertyChange(NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH_PROP_NAME, this.noOfSecPerSpectrumToPublish, this.noOfSecPerSpectrumToPublish = noOfSecPerSpectrumToPublish);
	}


	private String getI0IRefDataKey() {
		return getDataStoreKey() + IO_IREF_DATA_SUFFIX_KEY;
	}

	private String getGenerateAsciiDataKey() {
		return getDataStoreKey() + GENERATE_ASCII_DATA;
	}

	private String getScannablesToMonitorDataKey() {
		return getDataStoreKey() + SCANNABLE_DATA_KEY;
	}

	public double getDuration() {
		return timeIntervalData.getDuration();
	}

	public ExternalTriggerSetting getExternalTriggerSetting() {
		return externalTriggerSetting;
	}

	public boolean getGenerateAsciiData() {
		return generateAsciiData;
	}

	public void setGenerateAsciiData(boolean generateAsciiData) {
		this.firePropertyChange(GENERATE_ASCII_DATA, this.generateAsciiData, this.generateAsciiData = generateAsciiData);
		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration( getGenerateAsciiDataKey(), generateAsciiData );
	}

	private void savePreferenceData() {
		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration( getDataStoreKey(), groupList);
	}

	private void loadGenerateAsciiData() {
		try {
			generateAsciiData = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration( getGenerateAsciiDataKey(), boolean.class );
		} catch(NullPointerException e) {
			logger.info("Problem loading 'generate ascii data' option from preference store", e );
		}
	}

//	private void saveGenerateAsciiData() {
//		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration( getGenerateAsciiDataKey(), generateAsciiData );
//	}
}
