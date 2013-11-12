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

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.beamline.i20_1.utils.TimebarHelper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.TimingGroupModel.TimingGroupTimeBarRowModel;
import de.jaret.util.date.IntervalImpl;
import de.jaret.util.date.JaretDate;
import de.jaret.util.ui.timebars.TimeBarMarkerImpl;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;


public class TimeResolvedExperimentModel extends ExperimentTimingDataModel {

	public static final TimeResolvedExperimentModel INSTANCE = new TimeResolvedExperimentModel(0);

	private static final String TIMING_GROUPS_OBJ_NAME = "timingGroups";

	private static final double EXPERIMENT_START_TIME = 0.0;
	private static final double DEFAULT_INITIAL_EXPERIMENT_TIME = 20; // Should be > 0

	private static final String LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY = "TIME_RESOLVED_EXPERIMENT_DATA";

	private static final String JYTHON_DRIVER_OBJ = "timeresolveddriver";

	public static final String EXPERIMENT_DURATION_PROP_NAME = "experimentDuration";

	private DefaultTimeBarModel model;
	private TimingGroupTimeBarRowModel timingGroupRowModel;
	private TimingGroupTimeBarRowModel spectraRowModel;

	public static final String CURRENT_SCANNING_SPECTRUM_PROP_NAME = "currentScanningSpectrum";
	private SpectrumModel currentScanningSpectrum;

	public static final String SCANNING_PROP_NAME = "scanning";
	private boolean scanning;

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

	WritableList groupList = new WritableList(new ArrayList<TimingGroupModel>(), TimingGroupModel.class);

	private final ScanJob experimentDataCollectionJob;

	public static final String UNIT_PROP_NAME = "unit";
	private ExperimentUnit unit = ExperimentUnit.SEC;

	private TimeResolvedExperimentModel(@SuppressWarnings("unused") int dummy) {
		setupTimebarModel();
		groupList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						TimingGroupModel timingGroupModel = ((TimingGroupModel) element);
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
		TimingGroupModel[] savedGroups = ClientConfig.EdeDataStore.INSTANCE.loadConfiguration(LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY, TimingGroupModel[].class);
		if (savedGroups == null) {
			this.setTimes(EXPERIMENT_START_TIME, unit.convertToMilli(DEFAULT_INITIAL_EXPERIMENT_TIME));
			addGroup();
			return;
		}
		for (TimingGroupModel loadedGroup : savedGroups) {
			TimingGroupModel timingGroup = new TimingGroupModel(spectraRowModel, unit.getWorkingUnit());
			timingGroup.setName(loadedGroup.getName());
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

	private void setupTimebarModel() {
		model = new DefaultTimeBarModel();
		DefaultRowHeader header = new DefaultRowHeader("Timing groups");
		timingGroupRowModel = new TimingGroupTimeBarRowModel(header);
		header = new DefaultRowHeader("Spectra");
		spectraRowModel = new TimingGroupTimeBarRowModel(header);
		model.addRow(timingGroupRowModel);
		model.addRow(spectraRowModel);
	}

	public DefaultTimeBarModel getTimeBarModel() {
		return model;
	}

	public List<?> getGroupList() {
		return groupList;
	}

	public void splitGroup(TimingGroupModel groupToSplit) {
		double duration = groupToSplit.getDuration();
		double endTime = groupToSplit.getEndTime();
		double startTime = groupToSplit.getStartTime();
		groupToSplit.resetInitialTime(startTime, duration / 2, 0, duration / 2);
		TimingGroupModel newGroup = new TimingGroupModel(spectraRowModel, unit.getWorkingUnit());
		newGroup.setName("Group " + (groupList.indexOf(groupToSplit) + 2));
		newGroup.setIntegrationTime(1.0);
		addToInternalGroupList(newGroup, groupList.indexOf(groupToSplit) + 1);
		newGroup.resetInitialTime(groupToSplit.getEndTime(), endTime - groupToSplit.getEndTime(), 0, endTime - groupToSplit.getEndTime());
		for (int i = groupList.indexOf(groupToSplit) + 1; i < groupList.size(); i++) {
			((TimingGroupModel) groupList.get(i)).setName("Group " + (i + 1));
		}
	}

	public TimingGroupModel addGroup() {
		TimingGroupModel newGroup = new TimingGroupModel(spectraRowModel, unit.getWorkingUnit());
		newGroup.setName("Group " + (groupList.size() + 1));
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
				TimingGroupModel group = (TimingGroupModel) evt.getSource();
				if (groupList.indexOf(evt.getSource()) < groupList.size() - 1) {
					TimingGroupModel nextGroup = (TimingGroupModel) groupList.get(groupList.indexOf(evt.getSource()) + 1);
					nextGroup.moveTo(group.getEndTime());
				}
				updateExperimentDuration();
			}
			ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY, groupList);
		}
	};

	private void addToInternalGroupList(TimingGroupModel newGroup) {
		newGroup.addPropertyChangeListener(groupPropertyChangeListener);
		groupList.add(newGroup);
	}

	private void addToInternalGroupList(TimingGroupModel newGroup, int index) {
		newGroup.addPropertyChangeListener(groupPropertyChangeListener);
		groupList.add(index, newGroup);
	}

	private void removeFromInternalGroupList(TimingGroupModel group) {
		group.removePropertyChangeListener(groupPropertyChangeListener);
		groupList.remove(group);
	}

	public void removeGroup(TimingGroupModel group) {
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
		return String.format("from gda.scan.ede.drivers import LinearExperimentDriver;" +
				JYTHON_DRIVER_OBJ + " = LinearExperimentDriver(\"%s\",\"%s\",%s,%s);" +
				JYTHON_DRIVER_OBJ + ".setInBeamPosition(%f,%f);" +
				JYTHON_DRIVER_OBJ + ".setOutBeamPosition(%f,%f)",
				DetectorModel.INSTANCE.getCurrentDetector().getName(),
				DetectorModel.TOPUP_CHECKER,
				TIMING_GROUPS_OBJ_NAME,
				DetectorModel.SHUTTER_NAME,
				0.0,
				0.0,
				0.0,
				0.0
				);
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
						final TimingGroupModel currentGroup = (TimingGroupModel) groupList.get(currentGroupNumber);
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
			Job progressReportingJob = createProgressReportingJob();
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
							TimingGroupModel uiTimingGroup = (TimingGroupModel) object;
							TimingGroup timingGroup = new TimingGroup();
							timingGroup.setLabel(uiTimingGroup.getName());
							timingGroup.setNumberOfFrames(uiTimingGroup.getNumberOfSpectrum());
							timingGroup.setTimePerFrame(unit.getWorkingUnit().convertToSecond(uiTimingGroup.getTimePerSpectrum())); // convert to S
							timingGroup.setTimePerScan(unit.getWorkingUnit().convertToSecond(uiTimingGroup.getIntegrationTime())); // convert to S
							timingGroups.add(timingGroup);
						}

						InterfaceProvider.getJythonNamespace().placeInJythonNamespace(TIMING_GROUPS_OBJ_NAME, timingGroups);
						String scanCommand = buildScanCommand();
						InterfaceProvider.getCommandRunner().runCommand(scanCommand);
					}
				});
				progressReportingJob.schedule();

				// give the previous command a chance to run before calling doCollection()
				Thread.sleep(50);
				InterfaceProvider.getCommandRunner().evaluateCommand(JYTHON_DRIVER_OBJ + ".doCollection()");
			} catch (Exception e) {
				UIHelper.showWarning("Scanning has stopped", e.getMessage());
			}
			TimeResolvedExperimentModel.this.setScanning(false);
			monitor.done();
			return Status.OK_STATUS;
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
			experimentDuration += ((TimingGroupModel)loadedGroup).getDuration();
		}
		this.setTimes(EXPERIMENT_START_TIME, experimentDuration);
		this.firePropertyChange(EXPERIMENT_DURATION_PROP_NAME, null, getExperimentDuration());
	}

	private void resetInitialGroupTimes(double groupDuration) {
		double startTime = this.getStartTime();
		for (int i = 0; i < groupList.size(); i++) {
			TimingGroupModel group = (TimingGroupModel) groupList.get(i);
			if (i > 0) {
				TimingGroupModel previous = (TimingGroupModel) groupList.get(i-1);
				startTime = previous.getEndTime();
			}
			group.setName("Group " + (i + 1));
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
			((TimingGroupModel) object).setUnit(this.unit.getWorkingUnit());
		}
	}

	@Override
	public void dispose() {}
}
