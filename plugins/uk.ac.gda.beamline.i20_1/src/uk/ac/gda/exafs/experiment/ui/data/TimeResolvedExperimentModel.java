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

import gda.factory.Findable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.Jython;
import gda.jython.JythonServerFacade;
import gda.jython.JythonServerStatus;
import gda.jython.scriptcontroller.Scriptcontroller;
import gda.observable.IObserver;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.TimeResolvedExperiment;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;
import java.util.Vector;

import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i20_1.utils.ExperimentTimeHelper;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors.ExperimentMotorPostionType;
import uk.ac.gda.exafs.experiment.ui.data.TimingGroupUIModel.TimingGroupTimeBarRowModel;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.TimingGroup.InputTriggerLemoNumbers;

import com.google.gson.Gson;
import com.google.gson.annotations.Expose;

import de.jaret.util.date.IntervalImpl;
import de.jaret.util.date.JaretDate;
import de.jaret.util.ui.timebars.TimeBarMarkerImpl;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;

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

	private DefaultTimeBarModel timebarModel;
	private TimingGroupTimeBarRowModel timingGroupRowModel;
	private TimingGroupTimeBarRowModel spectraRowModel;

	public static final String NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH_PROP_NAME = "noOfSecPerSpectrumToPublish";
	private double noOfSecPerSpectrumToPublish = TimeResolvedExperiment.DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH;

	public static final String CURRENT_SCANNING_SPECTRUM_PROP_NAME = "currentScanningSpectrum";
	private SpectrumModel currentScanningSpectrum;

	public static final String SCANNING_PROP_NAME = "scanning";
	private boolean scanning;

	public static final String SCAN_DATA_SET_PROP_NAME = "scanDataSet";

	private static final int MAX_TOP_UP_TIMES = 10;
	private static final int DURATION_BETWEEN_TOP_UP_IN_MINUTES = 10;

	public static class Topup extends TimeBarMarkerImpl {
		public Topup(boolean draggable, JaretDate date) {
			super(draggable, date);
		}
	}

	private static final Topup[] topupTimes = new Topup[MAX_TOP_UP_TIMES];

	static {
		for(int i=0; i < topupTimes.length; i++) {
			topupTimes[i] = new Topup(false, ExperimentTimeHelper.getTime().advanceMinutes((i + 1) * DURATION_BETWEEN_TOP_UP_IN_MINUTES));
		}
	}

	private DoubleDataset[] scanDataSet;

	private final WritableList groupList = new WritableList(new ArrayList<TimingGroupUIModel>(), TimingGroupUIModel.class);

	private ScanJob experimentDataCollectionJob;

	public static final String UNIT_PROP_NAME = "unit";
	private ExperimentUnit unit = ExperimentUnit.SEC;

	public static final String UNIT_IN_STRING_PROP_NAME = "unitInStr";

	protected static final String IO_IREF_DATA_SUFFIX_KEY = "_IO_IREF_DATA";

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
		setupTimebarModel();
		groupList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						TimingGroupUIModel timingGroupModel = ((TimingGroupUIModel) element);
						timingGroupModel.dispose();
						timingGroupRowModel.remInterval(timingGroupModel);
					}

					@Override
					public void handleAdd(int index, Object element) {
						timingGroupRowModel.addInterval((IntervalImpl) element);
					}
				});
			}
		});

		experimentDataCollectionJob = new ScanJob("Linear experiment scan");
		InterfaceProvider.getJSFObserver().addIObserver(experimentDataCollectionJob);
		Findable controller = Finder.getInstance().findNoWarn(EdeExperiment.PROGRESS_UPDATER_NAME);
		if (controller != null) {
			((Scriptcontroller) controller).addIObserver(experimentDataCollectionJob);
		}
		experimentDataCollectionJob.setUser(true);
		loadSavedGroups();
	}

	public void addGroupListChangeListener(IListChangeListener listener) {
		groupList.addListChangeListener(listener);
	}

	public void removeGroupListChangeListener(IListChangeListener listener) {
		groupList.removeListChangeListener(listener);
	}

	public static Topup[] getTopupTimes() {
		return topupTimes;
	}

	private void loadSavedGroups() {

		TFGTrigger savedExternalTriggerSetting = ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(EXTERNAL_TRIGGER_DETAILS, TFGTrigger.class);
		if (savedExternalTriggerSetting == null) {
			savedExternalTriggerSetting = new TFGTrigger();
			try {
				savedExternalTriggerSetting.getSampleEnvironment().add(savedExternalTriggerSetting.createNewSampleEnvEntry());
			} catch (Exception e) {
				logger.error("Unable to create sample environment entry", e);
			}
		}
		externalTriggerSetting = new ExternalTriggerSetting(savedExternalTriggerSetting);

		externalTriggerSetting.getTfgTrigger().addPropertyChangeListener(TFGTrigger.TOTAL_TIME_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				TimeResolvedExperimentModel.this.firePropertyChange(TOTAL_IT_COLLECTION_DURATION_PROP_NAME, null, getTotalItCollectionDuration());
			}
		});

		TimingGroupUIModel[] savedGroups = ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(getDataStoreKey(), TimingGroupUIModel[].class);
		ExperimentDataModel savedExperimentDataModel = ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(getI0IRefDataKey(), ExperimentDataModel.class);
		if (savedExperimentDataModel == null) {
			experimentDataModel = new ExperimentDataModel();
		} else {
			experimentDataModel = savedExperimentDataModel;
		}
		experimentDataModel.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(getI0IRefDataKey(), experimentDataModel);
			}
		});
		if (savedGroups == null) {
			timeIntervalData.setTimes(IT_COLLECTION_START_TIME, unit.convertToDefaultUnit(DEFAULT_INITIAL_EXPERIMENT_TIME));
			createNewItGroup();
			return;
		}

		for (TimingGroupUIModel loadedGroup : savedGroups) {
			TimingGroupUIModel timingGroup = new TimingGroupUIModel(spectraRowModel, unit.getWorkingUnit(), this);
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
			timingGroup.setIntegrationTime(loadedGroup.getIntegrationTime());
			if (loadedGroup.getDelayBetweenSpectrum() > 0) {
				timingGroup.setDelayBetweenSpectrum(loadedGroup.getDelayBetweenSpectrum());
			}
			addToInternalGroupList(timingGroup);
		}
		updateCollectionDuration();
	}

	protected String getDataStoreKey() {
		return LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY;
	}

	private void setupTimebarModel() {
		timebarModel = new DefaultTimeBarModel();
		DefaultRowHeader header = new DefaultRowHeader("Groups");
		timingGroupRowModel = new TimingGroupTimeBarRowModel(header);
		header = new DefaultRowHeader("Spectra");
		spectraRowModel = new TimingGroupTimeBarRowModel(header);
		timebarModel.addRow(timingGroupRowModel);
		timebarModel.addRow(spectraRowModel);
	}

	public DefaultTimeBarModel getTimeBarModel() {
		return timebarModel;
	}

	public List<?> getGroupList() {
		return groupList;
	}

	public void splitGroup(TimingGroupUIModel groupToSplit) {
		double duration = groupToSplit.getDuration();
		double endTime = groupToSplit.getEndTime();
		double startTime = groupToSplit.getStartTime();
		groupToSplit.resetInitialTime(startTime, duration / 2, 0, duration / 2);
		TimingGroupUIModel newGroup = new TimingGroupUIModel(spectraRowModel, unit.getWorkingUnit(), this);
		newGroup.setName("Group " + (groupList.indexOf(groupToSplit) + 2));
		newGroup.setIntegrationTime(INITIAL_INTEGRATION_TIME);
		addToInternalGroupList(newGroup, groupList.indexOf(groupToSplit) + 1);
		newGroup.resetInitialTime(groupToSplit.getEndTime(), endTime - groupToSplit.getEndTime(), 0, endTime - groupToSplit.getEndTime());
		for (int i = groupList.indexOf(groupToSplit) + 1; i < groupList.size(); i++) {
			((TimingGroupUIModel) groupList.get(i)).setName("Group " + i);
		}
	}

	public TimingGroupUIModel createNewItGroup() {
		TimingGroupUIModel newGroup = new TimingGroupUIModel(spectraRowModel, unit.getWorkingUnit(), this);
		newGroup.setName("Group " + groupList.size());
		addToInternalGroupList(newGroup);
		resetInitialGroupTimes(timeIntervalData.getDuration() / groupList.size());
		newGroup.setIntegrationTime(INITIAL_INTEGRATION_TIME);
		newGroup.setExternalTriggerAvailable(true);
		newGroup.setExternalTriggerInputLemoNumber(InputTriggerLemoNumbers.ZERO);
		ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(this.getDataStoreKey(), groupList);
		return newGroup;
	}

	private final PropertyChangeListener groupPropertyChangeListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals(TimeIntervalDataModel.END_TIME_PROP_NAME)) {
				TimingGroupUIModel group = (TimingGroupUIModel) evt.getSource();
				if (groupList.indexOf(evt.getSource()) < groupList.size() - 1) {
					TimingGroupUIModel nextGroup = (TimingGroupUIModel) groupList.get(groupList.indexOf(evt.getSource()) + 1);
					nextGroup.moveTo(group.getEndTime());
				}
				updateCollectionDuration();
			}
			ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(TimeResolvedExperimentModel.this.getDataStoreKey(), groupList);
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

	public void removeGroup(TimingGroupUIModel group) throws Exception {
		if (groupList.size() > 1 && groupList.indexOf(group) > 0) {
			TimingGroupUIModel groupToExpend = (TimingGroupUIModel) groupList.get(groupList.indexOf(group) - 1);
			removeFromInternalGroupList(group);
			groupToExpend.setEndTime(group.getEndTime());
			ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(getDataStoreKey(), groupList);
		}
	}

	public void doCollection(String fileNamePrefix, String sampleDetails) {
		experimentDataModel.setFileNamePrefix(fileNamePrefix);
		experimentDataModel.setSampleDetails(sampleDetails);
		experimentDataCollectionJob.schedule();
	}

	// Jython command build
	// TODO This is very messy!
	protected String buildScanCommand() {
		StringBuilder builder = new StringBuilder("from gda.scan.ede import TimeResolvedExperiment;");
		if (this.getExperimentDataModel().isUseNoOfAccumulationsForI0()) {
			builder.append(String.format(LINEAR_EXPERIMENT_OBJ + " = TimeResolvedExperiment(%f, %d",
					ExperimentUnit.DEFAULT_EXPERIMENT_UNIT_FOR_I0_IREF.convertTo(this.getExperimentDataModel().getI0IntegrationTime(), ExperimentUnit.SEC),
					this.getExperimentDataModel().getI0NumberOfAccumulations()));
		} else {
			builder.append(String.format(LINEAR_EXPERIMENT_OBJ + " = TimeResolvedExperiment(%f",
					ExperimentUnit.DEFAULT_EXPERIMENT_UNIT_FOR_I0_IREF.convertTo(this.getExperimentDataModel().getI0IntegrationTime(), ExperimentUnit.SEC)));
		}
		builder.append(String.format(", %s, mapToJava(%s), mapToJava(%s), \"%s\", \"%s\", \"%s\", \'%s\');",
				TIMING_GROUPS_OBJ_NAME,
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.It),
				DetectorModel.INSTANCE.getCurrentDetector().getName(),
				DetectorModel.TOPUP_CHECKER,
				DetectorModel.SHUTTER_NAME,
				gson.toJson(externalTriggerSetting.getTfgTrigger())));
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setNoOfSecPerSpectrumToPublish(%f);", this.getNoOfSecPerSpectrumToPublish()));
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setFileNamePrefix(\"%s\");", this.getExperimentDataModel().getFileNamePrefix()));
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setSampleDetails(\"%s\");", this.getExperimentDataModel().getSampleDetails()));
		if (SampleStageMotors.INSTANCE.isUseIref()) {
			addIRefMethodCallStrToCommand(LINEAR_EXPERIMENT_OBJ, builder);
		}
		builder.append(LINEAR_EXPERIMENT_OBJ + ".runExperiment();");
		return builder.toString();
	}

	protected void addIRefMethodCallStrToCommand(String linearExperimentObj, StringBuilder builder) {
		int i0ForIRefNoOfAccumulations;
		int irefNoOfAccumulations = this.getExperimentDataModel().getIrefNoOfAccumulations();
		if (this.getExperimentDataModel().isUseNoOfAccumulationsForI0()) {
			i0ForIRefNoOfAccumulations = this.getExperimentDataModel().getI0NumberOfAccumulations();
		} else {
			i0ForIRefNoOfAccumulations = irefNoOfAccumulations;
		}
		double irefIntegrationTime = ExperimentUnit.DEFAULT_EXPERIMENT_UNIT_FOR_I0_IREF.convertTo(this.getExperimentDataModel().getIrefIntegrationTime(), ExperimentUnit.SEC);
		builder.append(String.format(linearExperimentObj + ".setIRefParameters(mapToJava(%s), mapToJava(%s), %f, %d, %f, %d);",
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.IRef),
				irefIntegrationTime,
				i0ForIRefNoOfAccumulations,
				irefIntegrationTime,
				irefNoOfAccumulations));
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
				if (TimeResolvedExperimentModel.this.isScanning() && Jython.IDLE == status.scanStatus) {
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
						// FIXME This scanning method needs to be improved
						final Vector<TimingGroup> timingGroups = new Vector<TimingGroup>();
						TimeResolvedExperimentModel.this.setScanning(true);
						for (Object object : groupList) {
							TimingGroupUIModel uiTimingGroup = (TimingGroupUIModel) object;
							TimingGroup timingGroup = new TimingGroup();
							timingGroup.setLabel(uiTimingGroup.getName());
							timingGroup.setNumberOfFrames(uiTimingGroup.getNumberOfSpectrum());
							timingGroup.setNumberOfScansPerFrame(uiTimingGroup.getNoOfAccumulations());
							timingGroup.setTimePerFrame(ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(uiTimingGroup.getTimePerSpectrum(), ExperimentUnit.SEC)); // convert to S
							// integration time is always in milli sec
							timingGroup.setTimePerScan(ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(uiTimingGroup.getIntegrationTime(), ExperimentUnit.SEC)); // convert to S
							timingGroup.setPreceedingTimeDelay(ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(uiTimingGroup.getDelay(), ExperimentUnit.SEC)); // convert to S
							timingGroup.setGroupTrig(uiTimingGroup.isUseExternalTrigger());
							// Set up lemo outs
							setupLemoOuts(timingGroup);
							timingGroups.add(timingGroup);
						}
						InterfaceProvider.getJythonNamespace().placeInJythonNamespace(TIMING_GROUPS_OBJ_NAME, timingGroups);
						String scanCommand = buildScanCommand();
						logger.info("Sending command: " + scanCommand);
						InterfaceProvider.getCommandRunner().runCommand(scanCommand);
					}
				});

			} catch (Exception e) {
				UIHelper.showWarning("Scanning has stopped", e.getMessage());
			}
			TimeResolvedExperimentModel.this.setScanning(false);
			monitor.done();
			return Status.OK_STATUS;
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

	protected void setScanning(final boolean value) {
		Display.getDefault().syncExec(new Runnable() {
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
		if (this.isScanning()) {
			JythonServerFacade.getInstance().requestFinishEarly();
		}
	}

	public SpectrumModel getCurrentScanningSpectrum() {
		return currentScanningSpectrum;
	}

	public void setCurrentScanningSpectrum(SpectrumModel value) {
		this.firePropertyChange(CURRENT_SCANNING_SPECTRUM_PROP_NAME, currentScanningSpectrum, currentScanningSpectrum = value);
	}

	private void updateCollectionDuration() {
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
		for(int i = 0; i < noOfGroups; i++) {
			TimingGroupUIModel newGroup = new TimingGroupUIModel(spectraRowModel, unit.getWorkingUnit(), this);
			newGroup.setName("Group " + groupList.size());
			newGroup.setIntegrationTime(INITIAL_INTEGRATION_TIME);
			addToInternalGroupList(newGroup);
		}
		resetInitialGroupTimes(timeIntervalData.getDuration() / groupList.size());
		ClientConfig.EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(this.getDataStoreKey(), groupList);
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

	public double getDuration() {
		return timeIntervalData.getDuration();
	}

	public ExternalTriggerSetting getExternalTriggerSetting() {
		return externalTriggerSetting;
	}
}
