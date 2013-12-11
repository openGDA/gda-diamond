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
import gda.jython.JythonServerFacade;
import gda.jython.JythonServerStatus;
import gda.jython.scriptcontroller.Scriptcontroller;
import gda.observable.IObserver;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.EdeLinearExperiment;

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
import uk.ac.gda.beamline.i20_1.utils.TimebarHelper;
import uk.ac.gda.client.CommandQueueViewFactory;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.SampleStageMotors.ExperimentMotorPostionType;
import uk.ac.gda.exafs.ui.data.experiment.TimingGroupUIModel.TimingGroupTimeBarRowModel;
import de.jaret.util.date.Interval;
import de.jaret.util.date.IntervalImpl;
import de.jaret.util.date.JaretDate;
import de.jaret.util.ui.timebars.TimeBarMarkerImpl;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;
import de.jaret.util.ui.timebars.model.TimeBarRow;


public class TimeResolvedExperimentModel extends ExperimentTimingDataModel {

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedExperimentModel.class);

	private static final String TIMING_GROUPS_OBJ_NAME = "timingGroups";

	private static final double EXPERIMENT_START_TIME = 0.0;
	private static final double DEFAULT_INITIAL_EXPERIMENT_TIME = 20; // Should be > 0

	public static final String LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY = "LINEAR_TIME_RESOLVED_EXPERIMENT_DATA";

	private static final String JYTHON_DRIVER_OBJ = "timeresolvedexperiment";

	public static final String EXPERIMENT_DURATION_PROP_NAME = "experimentDuration";

	private DefaultTimeBarModel timebarModel;

	public static final String NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH_PROP_NAME = "noOfSecPerSpectrumToPublish";
	private int noOfSecPerSpectrumToPublish = EdeLinearExperiment.DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH;

	public static final String CURRENT_SCANNING_SPECTRUM_PROP_NAME = "currentScanningSpectrum";
	private SpectrumModel currentScanningSpectrum;

	public static final String SCANNING_PROP_NAME = "scanning";
	private boolean scanning;

	public static final String USE_IT_TIME_FOR_I0_PROP_NAME = "useItTimeForI0";
	private boolean useItTimeForI0 = true;

	public static final String I0_INTEGRATION_TIME_PROP_NAME = "i0IntegrationTime";
	private double i0IntegrationTime;

	public static final String I0_NO_OF_ACCUMULATION_PROP_NAME = "i0NoOfAccumulations";
	private int i0NoOfAccumulations;

	public static final String IREF_INTEGRATION_TIME_PROP_NAME = "irefIntegrationTime";
	private double irefIntegrationTime;

	public static final String IREF_NO_OF_ACCUMULATION_PROP_NAME = "irefNoOfAccumulations";
	private int irefNoOfAccumulations;

	public static final String SCAN_DATA_SET_PROP_NAME = "scanDataSet";

	private static final int MAX_TOP_UP_TIMES = 10;
	private static final int DURATION_BETWEEN_TOP_UP_IN_MINUTES = 10;
	public static final int TOP_UP_DURATION_IN_SECONDS = 10;

	public static class Topup extends TimeBarMarkerImpl {
		public Topup(boolean draggable, JaretDate date) {
			super(draggable, date);
		}
	}

	private static final Topup[] topupTimes = new Topup[MAX_TOP_UP_TIMES];

	static {
		for(int i=0; i < topupTimes.length; i++) {
			topupTimes[i] = new Topup(false, TimebarHelper.getTime().advanceMinutes((i + 1) * DURATION_BETWEEN_TOP_UP_IN_MINUTES));
		}
	}

	private DoubleDataset[] scanDataSet;

	protected WritableList groupList = new WritableList(new ArrayList<TimingGroupUIModel>(), TimingGroupUIModel.class);

	public static final String NO_OF_REPEATED_GROUPS_PROP_NAME = "noOfRepeatedGroups";
	private int noOfRepeatedGroups = 1;

	private ScanJob experimentDataCollectionJob;

	public static final String UNIT_PROP_NAME = "unit";
	private ExperimentUnit unit = ExperimentUnit.SEC;

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
						removeIntervals(timingGroupModel);
					}

					@Override
					public void handleAdd(int index, Object element) {
						addIntervals((IntervalImpl) element);
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
	}

	private void addIntervals(IntervalImpl groupModel) {
		for(int i = 0; i < timebarModel.getRowCount(); i += 2) {
			((TimingGroupTimeBarRowModel) timebarModel.getRow(i)).addInterval(groupModel);
		}
	}

	private void removeIntervals(IntervalImpl groupModel) {
		for(int i = 0; i < timebarModel.getRowCount(); i += 2) {
			((TimingGroupTimeBarRowModel) timebarModel.getRow(i)).remInterval(groupModel);
		}
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

	public void loadSavedGroups(String key) {
		TimingGroupUIModel[] savedGroups = ClientConfig.EdeDataStore.INSTANCE.loadConfiguration(key, TimingGroupUIModel[].class);
		if (savedGroups == null) {
			this.setTimes(EXPERIMENT_START_TIME, unit.convertToMilli(DEFAULT_INITIAL_EXPERIMENT_TIME));
			addGroup();
			return;
		}
		for (TimingGroupUIModel loadedGroup : savedGroups) {
			TimingGroupUIModel timingGroup = new TimingGroupUIModel(timebarModel, unit.getWorkingUnit(), this);
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

	protected String getGroupHeaderPrefix(@SuppressWarnings("unused") int index) {
		return "Groups";
	}

	private void setupTimebarModel() {
		// Each group has 2 rows, for group and spectra
		int existingRows = 0;
		if (timebarModel == null) {
			timebarModel = new DefaultTimeBarModel();
		} else {
			existingRows = timebarModel.getRowCount() / 2;
		}
		for (int i=0; i < noOfRepeatedGroups; i++) {
			if (i >= existingRows) {
				DefaultRowHeader header = new DefaultRowHeader(getGroupHeaderPrefix(i));
				TimingGroupTimeBarRowModel timingGroupRowModel = new TimingGroupTimeBarRowModel(header);
				timebarModel.addRow(timingGroupRowModel);

				header = new DefaultRowHeader("");
				TimingGroupTimeBarRowModel spectraRowModel = new TimingGroupTimeBarRowModel(header);
				timebarModel.addRow(spectraRowModel);

				if (existingRows > 0) {
					for (Interval interval : timebarModel.getRow(0).getIntervals()) {
						timingGroupRowModel.addInterval(interval);
					}
					for (Interval interval : timebarModel.getRow(1).getIntervals()) {
						spectraRowModel.addInterval(interval);
					}
				}
			}
		}
		if (noOfRepeatedGroups < existingRows) {
			List<TimeBarRow> rowsToRemove = new ArrayList<TimeBarRow>();
			for (int i = noOfRepeatedGroups; i < existingRows; i++) {
				int rowIndex = i * 2;
				rowsToRemove.add(timebarModel.getRow(rowIndex));
				rowsToRemove.add(timebarModel.getRow(rowIndex + 1));
			}
			for (TimeBarRow rowToRemove : rowsToRemove) {
				timebarModel.remRow(rowToRemove);
			}
		}
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
		TimingGroupUIModel newGroup = new TimingGroupUIModel(timebarModel, unit.getWorkingUnit(), this);
		newGroup.setName("Group " + (groupList.indexOf(groupToSplit) + 2));
		newGroup.setIntegrationTime(1.0);
		addToInternalGroupList(newGroup, groupList.indexOf(groupToSplit) + 1);
		newGroup.resetInitialTime(groupToSplit.getEndTime(), endTime - groupToSplit.getEndTime(), 0, endTime - groupToSplit.getEndTime());
		for (int i = groupList.indexOf(groupToSplit) + 1; i < groupList.size(); i++) {
			((TimingGroupUIModel) groupList.get(i)).setName("Group " + i);
		}
	}

	public TimingGroupUIModel addGroup() {
		TimingGroupUIModel newGroup = new TimingGroupUIModel(timebarModel, unit.getWorkingUnit(), this);
		newGroup.setName("Group " + groupList.size());
		newGroup.setIntegrationTime(1.0);
		addToInternalGroupList(newGroup);
		resetInitialGroupTimes(this.getDuration() / groupList.size());
		ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY, groupList);
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
			ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY, groupList);
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
		if (groupList.size() > 1) {
			removeFromInternalGroupList(group);
			resetInitialGroupTimes(this.getDuration() / groupList.size());
			ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY, groupList);
		}
	}

	public void doCollection() {
		experimentDataCollectionJob.schedule();
	}

	private String buildScanCommand() {
		StringBuilder builder = new StringBuilder(String.format("from gda.scan.ede import EdeLinearExperiment;" +
				JYTHON_DRIVER_OBJ + " = EdeLinearExperiment(%s, mapToJava(%s), mapToJava(%s), \"%s\", \"%s\", \"%s\");" +
				JYTHON_DRIVER_OBJ + ".setNoOfSecPerSpectrumToPublish(%s);",
				TIMING_GROUPS_OBJ_NAME,
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.It),
				DetectorModel.INSTANCE.getCurrentDetector().getName(),
				DetectorModel.TOPUP_CHECKER,
				DetectorModel.SHUTTER_NAME,
				this.getNoOfSecPerSpectrumToPublish()));
		if (SampleStageMotors.INSTANCE.isUseIref()) {
			builder.append(String.format(JYTHON_DRIVER_OBJ + ".setIRefParameters(mapToJava(%s), %f, %d);",
					SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.IRef),
					unit.getWorkingUnit().convertToSecond(irefIntegrationTime), irefNoOfAccumulations));
		}
		if (!this.isUseItTimeForI0()) {
			builder.append(String.format(JYTHON_DRIVER_OBJ + ".setCommonI0Parameters(%f, %d);",
					unit.getWorkingUnit().convertToSecond(i0IntegrationTime), i0NoOfAccumulations));
		} else {
			builder.append(String.format(JYTHON_DRIVER_OBJ + ".setCommonI0Parameters(%f);",
					unit.getWorkingUnit().convertToSecond(i0IntegrationTime)));
		}
		builder.append(JYTHON_DRIVER_OBJ + ".runExperiment();");
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
				final int currentFrameNumber = edeExperimentProgress.getProgress().getFrameNumOfThisSDP();
				final int currentGroupNumber = edeExperimentProgress.getProgress().getGroupNumOfThisSDP();
				Display.getDefault().asyncExec(new Runnable() {
					@Override
					public void run() {
						final TimingGroupUIModel currentGroup = (TimingGroupUIModel) groupList.get(currentGroupNumber);
						// TODO refactor the group to manage its own state
						TimeResolvedExperimentModel.this.setCurrentScanningSpectrum((SpectrumModel) currentGroup.getSpectrumList().get(currentFrameNumber));
					}
				});
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

	public void stopScan() {
		if (this.isScanning()) {
			JythonServerFacade.getInstance().haltCurrentScan();
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
		if (this.isScanning()) {
			JythonServerFacade.getInstance().haltCurrentScan();
		}
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

	public double getExperimentDuration() {
		return unit.convertFromMilli(getDuration());
	}

	public double getDurationInSec() {
		return unit.convertToSecond(unit.convertFromMilli(getDuration()));
	}

	public ExperimentUnit getUnit() {
		return unit;
	}

	public void setUnit(ExperimentUnit unit) {
		this.firePropertyChange(UNIT_PROP_NAME, this.unit, this.unit = unit);
		for (Object object : getGroupList()) {
			((TimingGroupUIModel) object).setUnit(this.unit.getWorkingUnit());
		}
	}

	public int getNoOfSecPerSpectrumToPublish() {
		return noOfSecPerSpectrumToPublish;
	}

	public void setNoOfSecPerSpectrumToPublish(int noOfSecPerSpectrumToPublish) {
		this.firePropertyChange(NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH_PROP_NAME, this.noOfSecPerSpectrumToPublish, this.noOfSecPerSpectrumToPublish = noOfSecPerSpectrumToPublish);
	}

	public boolean isUseItTimeForI0() {
		return useItTimeForI0;
	}

	public void setUseItTimeForI0(boolean useItTimeForI0) {
		this.firePropertyChange(USE_IT_TIME_FOR_I0_PROP_NAME, this.useItTimeForI0, this.useItTimeForI0 = useItTimeForI0);
	}

	public double getI0IntegrationTime() {
		return i0IntegrationTime;
	}

	public void setI0IntegrationTime(double i0IntegrationTime) {
		this.firePropertyChange(I0_INTEGRATION_TIME_PROP_NAME, this.i0IntegrationTime, this.i0IntegrationTime = i0IntegrationTime);
	}

	public int getI0NoOfAccumulations() {
		return i0NoOfAccumulations;
	}

	public void setI0NoOfAccumulations(int i0NoOfAccumulations) {
		this.firePropertyChange(I0_NO_OF_ACCUMULATION_PROP_NAME, this.i0NoOfAccumulations, this.i0NoOfAccumulations = i0NoOfAccumulations);
	}

	public double getIrefIntegrationTime() {
		return irefIntegrationTime;
	}

	public void setIrefIntegrationTime(double irefIntegrationTime) {
		this.firePropertyChange(IREF_INTEGRATION_TIME_PROP_NAME, this.irefIntegrationTime, this.irefIntegrationTime = irefIntegrationTime);
	}

	public int getIrefNoOfAccumulations() {
		return irefNoOfAccumulations;
	}

	public void setIrefNoOfAccumulations(int irefNoOfAccumulations) {
		this.firePropertyChange(IREF_NO_OF_ACCUMULATION_PROP_NAME, this.irefNoOfAccumulations, this.irefNoOfAccumulations = irefNoOfAccumulations);
	}

	public int getNoOfRepeatedGroups() {
		return noOfRepeatedGroups;
	}

	public void setNoOfRepeatedGroups(int noOfRepeatedGroups) {
		this.firePropertyChange(NO_OF_REPEATED_GROUPS_PROP_NAME, this.noOfRepeatedGroups, this.noOfRepeatedGroups = noOfRepeatedGroups);
		setupTimebarModel();
	}

	@Override
	public void dispose() {}
}
