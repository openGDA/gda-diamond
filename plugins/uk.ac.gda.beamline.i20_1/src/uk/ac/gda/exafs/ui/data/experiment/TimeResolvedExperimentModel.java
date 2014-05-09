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

package uk.ac.gda.exafs.ui.data.experiment;

import gda.commandqueue.JythonCommandCommandProvider;
import gda.commandqueue.Queue;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.Jython;
import gda.jython.JythonServerStatus;
import gda.jython.scriptcontroller.Scriptcontroller;
import gda.observable.IObserver;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;

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
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.beamline.i20_1.utils.ExperimentTimeHelper;
import uk.ac.gda.client.CommandQueueViewFactory;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentDataModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors.ExperimentMotorPostionType;
import uk.ac.gda.exafs.experiment.ui.data.SpectrumModel;
import uk.ac.gda.exafs.experiment.ui.data.TimingGroupUIModel;
import uk.ac.gda.exafs.experiment.ui.data.TimingGroupUIModel.TimingGroupTimeBarRowModel;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.UIHelper;

import com.google.gson.annotations.Expose;

import de.jaret.util.date.IntervalImpl;
import de.jaret.util.date.JaretDate;
import de.jaret.util.ui.timebars.TimeBarMarkerImpl;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;

public class TimeResolvedExperimentModel extends ExperimentTimingDataModel {

	public static final int TOP_UP_DURATION_IN_SECONDS = 10;

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedExperimentModel.class);

	protected static final String TIMING_GROUPS_OBJ_NAME = "timingGroups";

	private static final double EXPERIMENT_START_TIME = 0.0;
	private static final double DEFAULT_INITIAL_EXPERIMENT_TIME = 20; // Should be > 0

	private static final String LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY = "LINEAR_TIME_RESOLVED_EXPERIMENT_DATA";

	private static final String LINEAR_EXPERIMENT_OBJ = "linearExperiment";

	public static final String EXPERIMENT_DURATION_PROP_NAME = "experimentDuration";

	private DefaultTimeBarModel timebarModel;
	private TimingGroupTimeBarRowModel timingGroupRowModel;
	private TimingGroupTimeBarRowModel spectraRowModel;

	public static final String NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH_PROP_NAME = "noOfSecPerSpectrumToPublish";
	private int noOfSecPerSpectrumToPublish = EdeLinearExperiment.DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH;

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

		experimentDataCollectionJob = new ScanJob("Linear Experiment Scan");
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
		TimingGroupUIModel[] savedGroups = ClientConfig.EdeDataStore.INSTANCE.loadConfiguration(getDataStoreKey(), TimingGroupUIModel[].class);
		ExperimentDataModel savedExperimentDataModel = ClientConfig.EdeDataStore.INSTANCE.loadConfiguration(getI0IRefDataKey(), ExperimentDataModel.class);
		if (savedExperimentDataModel == null) {
			experimentDataModel = new ExperimentDataModel();
		} else {
			experimentDataModel = savedExperimentDataModel;
		}
		experimentDataModel.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(getI0IRefDataKey(), experimentDataModel);
			}
		});
		if (savedGroups == null) {
			this.setTimes(EXPERIMENT_START_TIME, unit.convertToMilli(DEFAULT_INITIAL_EXPERIMENT_TIME));
			addItGroup();
			return;
		}

		for (TimingGroupUIModel loadedGroup : savedGroups) {
			TimingGroupUIModel timingGroup = new TimingGroupUIModel(spectraRowModel, unit.getWorkingUnit(), this);
			timingGroup.setName(loadedGroup.getName());
			timingGroup.setUseExernalTrigger(loadedGroup.isUseExernalTrigger());
			timingGroup.setExernalTriggerAvailable(loadedGroup.isExernalTriggerAvailable());
			timingGroup.setExernalTriggerInputLemoNumber(loadedGroup.getExernalTriggerInputLemoNumber());
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
		updateExperimentDuration();
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
		newGroup.setIntegrationTime(1.0);
		addToInternalGroupList(newGroup, groupList.indexOf(groupToSplit) + 1);
		newGroup.resetInitialTime(groupToSplit.getEndTime(), endTime - groupToSplit.getEndTime(), 0, endTime - groupToSplit.getEndTime());
		for (int i = groupList.indexOf(groupToSplit) + 1; i < groupList.size(); i++) {
			((TimingGroupUIModel) groupList.get(i)).setName("Group " + i);
		}
	}

	public TimingGroupUIModel addItGroup() {
		TimingGroupUIModel newGroup = new TimingGroupUIModel(spectraRowModel, unit.getWorkingUnit(), this);
		newGroup.setName("Group " + groupList.size());
		newGroup.setIntegrationTime(1.0);
		addToInternalGroupList(newGroup);
		resetInitialGroupTimes(this.getDuration() / groupList.size());
		ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(this.getDataStoreKey(), groupList);
		return newGroup;
	}

	private final PropertyChangeListener groupPropertyChangeListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals(ExperimentTimingDataModel.END_TIME_PROP_NAME)) {
				TimingGroupUIModel group = (TimingGroupUIModel) evt.getSource();
				if (groupList.indexOf(evt.getSource()) < groupList.size() - 1) {
					TimingGroupUIModel nextGroup = (TimingGroupUIModel) groupList.get(groupList.indexOf(evt.getSource()) + 1);
					nextGroup.moveTo(group.getEndTime());
				}
				updateExperimentDuration();
			}
			ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(TimeResolvedExperimentModel.this.getDataStoreKey(), groupList);
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

	public void removeGroup(TimingGroupUIModel group) {
		if (groupList.size() > 1 && groupList.indexOf(group) > 0) {
			TimingGroupUIModel groupToExpend = (TimingGroupUIModel) groupList.get(groupList.indexOf(group) - 1);
			removeFromInternalGroupList(group);
			groupToExpend.setEndTime(group.getEndTime());
			ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(getDataStoreKey(), groupList);
		}
	}

	public void doCollection() {
		experimentDataCollectionJob.schedule();
	}

	protected String buildScanCommand() {
		StringBuilder builder = new StringBuilder("from gda.scan.ede import EdeLinearExperiment;");
		if (this.getExperimentDataModel().isUseNoOfAccumulationsForI0()) {
			builder.append(String.format(LINEAR_EXPERIMENT_OBJ + " = EdeLinearExperiment(%f, %d",
					ExperimentTimeHelper.fromMilliToSec(this.getExperimentDataModel().getI0IntegrationTime()),
					this.getExperimentDataModel().getI0NumberOfAccumulations()));
		} else {
			builder.append(String.format(LINEAR_EXPERIMENT_OBJ + " = EdeLinearExperiment(%f",
					ExperimentTimeHelper.fromMilliToSec(this.getExperimentDataModel().getI0IntegrationTime())));
		}
		builder.append(String.format(", %s, mapToJava(%s), mapToJava(%s), \"%s\", \"%s\", \"%s\");",
				TIMING_GROUPS_OBJ_NAME,
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.It),
				DetectorModel.INSTANCE.getCurrentDetector().getName(),
				DetectorModel.TOPUP_CHECKER,
				DetectorModel.SHUTTER_NAME));
		builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setNoOfSecPerSpectrumToPublish(%d);", this.getNoOfSecPerSpectrumToPublish()));
		if (SampleStageMotors.INSTANCE.isUseIref()) {
			builder.append(String.format(LINEAR_EXPERIMENT_OBJ + ".setIRefParameters(mapToJava(%s), %f, %d);",
					SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.IRef),
					ExperimentTimeHelper.fromMilliToSec(this.getExperimentDataModel().getIrefIntegrationTime()), this.getExperimentDataModel().getIrefNoOfAccumulations()));
		}
		builder.append(LINEAR_EXPERIMENT_OBJ + ".runExperiment();");
		return builder.toString();
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

				// This is commented out to disable the marker feature to show currently scanning spectra

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
						final Vector<TimingGroup> timingGroups = new Vector<TimingGroup>();
						TimeResolvedExperimentModel.this.setScanning(true);
						for (Object object : groupList) {
							TimingGroupUIModel uiTimingGroup = (TimingGroupUIModel) object;
							TimingGroup timingGroup = new TimingGroup();
							timingGroup.setLabel(uiTimingGroup.getName());
							timingGroup.setNumberOfFrames(uiTimingGroup.getNumberOfSpectrum());
							timingGroup.setTimePerFrame(unit.getWorkingUnit().convertToSecond(uiTimingGroup.getTimePerSpectrum())); // convert to S
							timingGroup.setTimePerScan(unit.getWorkingUnit().convertToSecond(uiTimingGroup.getIntegrationTime())); // convert to S
							timingGroup.setPreceedingTimeDelay(unit.getWorkingUnit().convertToSecond(uiTimingGroup.getDelay())); // convert to S
							if (uiTimingGroup.isUseExernalTrigger()) {
								timingGroup.setGroupTrig(true);
								timingGroup.setGroupTrigLemo(uiTimingGroup.getExternalTrigLemoNumber());
								timingGroup.setGroupTrigRisingEdge(!uiTimingGroup.getExernalTriggerInputLemoNumber().isFallingEdge());
							}
							// Set up lemo outs
							setupLemoOuts(timingGroup);
							timingGroups.add(timingGroup);
						}
						InterfaceProvider.getJythonNamespace().placeInJythonNamespace(TIMING_GROUPS_OBJ_NAME, timingGroups);
						String scanCommand = buildScanCommand();
						logger.info("Sending command: " + scanCommand);
						//InterfaceProvider.getCommandRunner().runCommand(scanCommand);
						Queue queue = CommandQueueViewFactory.getQueue();
						if (queue != null) {
							try {
								progressReportingJob.schedule();
								queue.addToTail(new JythonCommandCommandProvider(scanCommand, "Do a collection", null));
							} catch (Exception e) {
								e.printStackTrace();
								// TODO Auto-generated catch block
							}
						}
					}
				});


				// give the previous command a chance to run before calling doCollection()
				//Thread.sleep(50);
				//				InterfaceProvider.getCommandRunner().evaluateCommand(JYTHON_DRIVER_OBJ + ".doCollection()");

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

	public void stopScan() {
		if (this.isScanning()) {
			InterfaceProvider.getCurrentScanController().requestFinishEarly();
		}
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
		stopScan();
	}

	public SpectrumModel getCurrentScanningSpectrum() {
		return currentScanningSpectrum;
	}

	public void setCurrentScanningSpectrum(SpectrumModel value) {
		this.firePropertyChange(CURRENT_SCANNING_SPECTRUM_PROP_NAME, currentScanningSpectrum, currentScanningSpectrum = value);
	}

	private void updateExperimentDuration() {
		double experimentDuration = 0.0;
		for (Object loadedGroup : groupList) {
			experimentDuration += ((TimingGroupUIModel)loadedGroup).getDuration();
		}
		this.setTimes(EXPERIMENT_START_TIME, experimentDuration);
		this.firePropertyChange(EXPERIMENT_DURATION_PROP_NAME, null, getExperimentDuration());
	}

	private void resetInitialGroupTimes(double groupDuration) {
		double startTime = this.getStartTime();
		for (int i = 0; i < groupList.size(); i++) {
			TimingGroupUIModel group = (TimingGroupUIModel) groupList.get(i);
			if (i > 0) {
				TimingGroupUIModel previous = (TimingGroupUIModel) groupList.get(i-1);
				startTime = previous.getEndTime();
				group.setExernalTriggerAvailable(false);
			} else {
				group.setExernalTriggerAvailable(true);
			}
			group.setName("Group " + i);
			group.resetInitialTime(startTime, groupDuration, 0.0, groupDuration);
		}
	}

	public void setExperimentDuration(double value) {
		resetInitialGroupTimes(unit.convertToMilli(value) / groupList.size());
	}

	public void setupExperiment(ExperimentUnit unit, double duration, int noOfGroups) {
		this.setTimes(EXPERIMENT_START_TIME, unit.convertToMilli(duration));
		this.setUnit(unit);
		groupList.clear();
		for(int i = 0; i < noOfGroups; i++) {
			TimingGroupUIModel newGroup = new TimingGroupUIModel(spectraRowModel, unit.getWorkingUnit(), this);
			newGroup.setName("Group " + groupList.size());
			newGroup.setIntegrationTime(1.0);
			addToInternalGroupList(newGroup);
		}
		resetInitialGroupTimes(this.getDuration() / groupList.size());
		ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(this.getDataStoreKey(), groupList);
	}

	public double getExperimentDuration() {
		return unit.convertFromMilli(getDuration());
	}

	public double getDurationInSec() {
		return unit.convertToSecond(unit.convertFromMilli(getDuration()));
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

	public int getNoOfSecPerSpectrumToPublish() {
		return noOfSecPerSpectrumToPublish;
	}

	public void setNoOfSecPerSpectrumToPublish(int noOfSecPerSpectrumToPublish) throws IllegalArgumentException {
		if (noOfSecPerSpectrumToPublish >= this.getDurationInSec()) {
			throw new IllegalArgumentException("Cannot be longer than experiment duration");
		}
		this.firePropertyChange(NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH_PROP_NAME, this.noOfSecPerSpectrumToPublish, this.noOfSecPerSpectrumToPublish = noOfSecPerSpectrumToPublish);
	}

	@Override
	public void dispose() {
		// Nothing to dispose
	}

	private String getI0IRefDataKey() {
		return getDataStoreKey() + IO_IREF_DATA_SUFFIX_KEY;
	}
}
