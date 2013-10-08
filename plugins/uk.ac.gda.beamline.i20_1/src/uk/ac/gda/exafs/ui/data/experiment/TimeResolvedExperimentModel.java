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
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.UIHelper;
import de.jaret.util.date.IntervalImpl;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;


public class TimeResolvedExperimentModel extends ExperimentTimingDataModel {

	public static final TimeResolvedExperimentModel INSTANCE = new TimeResolvedExperimentModel();

	private static final String TIMING_GROUPS_OBJ_NAME = "timingGroups";

	private static final double EXPERIMENT_START_TIME = 0.0;
	private static final long DEFAULT_INITIAL_EXPERIMENT_TIME_IN_SEC = 20; // Should be > 0

	public static final String DURATION_IN_SEC_PROP_NAME = "durationInSec";

	private static final String LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY = "LinearExperimentModel";

	private DefaultTimeBarModel model;
	private DefaultTimeBarRowModel timingGroupRowModel;

	public static final String CURRENT_SCANNING_SPECTRUM_PROP_NAME = "currentScanningSpectrum";
	private SpectrumModel currentScanningSpectrum;

	public static final String SCANNING_PROP_NAME = "scanning";
	private boolean scanning;

	public static final String SCAN_DATA_SET_PROP_NAME = "scanDataSet";
	private DoubleDataset[] scanDataSet;

	WritableList groupList = new WritableList(new ArrayList<TimingGroupModel>(), TimingGroupModel.class);

	private final ScanJob experimentJob;

	public TimeResolvedExperimentModel() {
		this.setStartTime(EXPERIMENT_START_TIME);
		this.setDurationInSec(DEFAULT_INITIAL_EXPERIMENT_TIME_IN_SEC);
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

		experimentJob = new ScanJob("Linear Experiment Scan");
		InterfaceProvider.getJSFObserver().addIObserver(experimentJob);
		Findable controller = Finder.getInstance().findNoWarn(EdeExperiment.PROGRESS_UPDATER_NAME);
		if (controller != null) {
			((Scriptcontroller) controller).addIObserver(experimentJob);
		}
		experimentJob.setUser(true);
		loadSavedGroups();
	}

	private void loadSavedGroups() {
		TimingGroupModel[] savedGroups = ClientConfig.EdeDataStore.INSTANCE.loadConfiguration(LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY, TimingGroupModel[].class);
		if (savedGroups == null) {
			addGroup();
			return;
		}
		for (TimingGroupModel loadedGroup : savedGroups) {
			TimingGroupModel timingGroup = new TimingGroupModel(timingGroupRowModel);
			timingGroup.setName(loadedGroup.getName());
			timingGroup.setTimes(loadedGroup.getStartTime(), loadedGroup.getEndTime());
			timingGroup.setDelay(loadedGroup.getDelay());
			timingGroup.setIntegrationTime(loadedGroup.getIntegrationTime());
			timingGroup.setDelayBetweenSpectrum(loadedGroup.getDelayBetweenSpectrum());
			addToInternalGroupList(timingGroup);
			timingGroup.setTimePerSpectrum(loadedGroup.getTimePerSpectrum());
		}
	}

	private void setupTimebarModel() {
		model = new DefaultTimeBarModel();
		DefaultRowHeader header = new DefaultRowHeader("Timing groups");
		timingGroupRowModel = new DefaultTimeBarRowModel(header);
		model.addRow(timingGroupRowModel);
	}

	public DefaultTimeBarModel getTimeBarModel() {
		return model;
	}

	public List<?> getGroupList() {
		return groupList;
	}

	public TimingGroupModel addGroup() {
		TimingGroupModel newGroup = new TimingGroupModel(timingGroupRowModel);
		newGroup.setName("Group " + (groupList.size() + 1));
		newGroup.setTimes(this.getStartTime(), this.getEndTime());
		newGroup.setIntegrationTime(1.0);
		addToInternalGroupList(newGroup);
		setAllGroupTimes();
		newGroup.setTimePerSpectrum(newGroup.getDuration());
		ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY, groupList);
		return newGroup;
	}

	private final PropertyChangeListener groupPropertyChangeListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY, groupList);
		}
	};

	private void addToInternalGroupList(TimingGroupModel newGroup) {
		newGroup.addPropertyChangeListener(groupPropertyChangeListener);
		groupList.add(newGroup);
	}

	private void removeFromInternalGroupList(TimingGroupModel group) {
		group.removePropertyChangeListener(groupPropertyChangeListener);
		groupList.remove(group);
	}

	public void removeGroup(TimingGroupModel group) {
		removeFromInternalGroupList(group);
		setAllGroupTimes();
		ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(LINEAR_EXPERIMENT_MODEL_DATA_STORE_KEY, groupList);
	}

	public void doCollection() {
		experimentJob.schedule();
	}

	private String buildScanCommand() {
		return String.format("from gda.scan.ede.drivers import LinearExperimentDriver;" +
				"scan_driver = LinearExperimentDriver(\"%s\",%s);" +
				"scan_driver.setInBeamPosition(%f,%f);" +
				"scan_driver.setOutBeamPosition(%f,%f)",
				DetectorModel.INSTANCE.getCurrentDetector().getName(),
				TIMING_GROUPS_OBJ_NAME,
				SingleSpectrumModel.INSTANCE.getiTxPosition(),
				SingleSpectrumModel.INSTANCE.getiTxPosition(),
				SingleSpectrumModel.INSTANCE.getI0xPosition(),
				SingleSpectrumModel.INSTANCE.getI0xPosition()
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
				currentNormalisedItData = edeExperimentProgress.getNormalisedIt();
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
						if (currentNormalisedItData != null & currentEnergyData != null) {
							setReceivedDataSet();
						}
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
					TimeResolvedExperimentModel.this.setScanDataSet(new DoubleDataset[] {currentEnergyData, currentNormalisedItData});
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
							timingGroup.setNumberOfFrames(uiTimingGroup.getNumberOfSpectrums());
							timingGroup.setTimePerFrame(uiTimingGroup.getTimePerSpectrum() / 1000.0); // convert from ms to S
							timingGroup.setTimePerScan(uiTimingGroup.getIntegrationTime() / 1000.0); // convert from ms to S
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
				InterfaceProvider.getCommandRunner().evaluateCommand("scan_driver.doCollection()");
			} catch (InterruptedException e) {
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

	public SpectrumModel getCurrentScanningSpectrum() {
		return currentScanningSpectrum;
	}

	public void setCurrentScanningSpectrum(SpectrumModel value) {
		this.firePropertyChange(CURRENT_SCANNING_SPECTRUM_PROP_NAME, currentScanningSpectrum, currentScanningSpectrum = value);
	}

	private void setAllGroupTimes() {
		if (!groupList.isEmpty()) {
			double duration;
			if (groupList.size() ==  1) {
				duration = this.getDuration();
			} else {
				duration = this.getDuration() / groupList.size();
			}
			double startTime = this.getStartTime();
			for (int i = 0; i < groupList.size(); i++) {
				TimingGroupModel entry = (TimingGroupModel) groupList.get(i);
				entry.setTimes(startTime, startTime + duration);
				startTime = entry.getEndTime();
			}
		}
	}

	private void setGroupTimes(double groupDuration) {
		double startTime = this.getStartTime();
		for (int i = 0; i < groupList.size(); i++) {
			TimingGroupModel group = (TimingGroupModel) groupList.get(i);
			if (i > 0) {
				TimingGroupModel previous = (TimingGroupModel) groupList.get(i-1);
				startTime = previous.getEndTime();
			}
			group.setTimes(startTime, group.getStartTime() + groupDuration);
		}
	}

	public void setGroupStartTime(TimingGroupModel group, double value) {
		int index = groupList.indexOf(group);
		if (index != 0) {
			TimingGroupModel prevGroup = (TimingGroupModel) groupList.get(index - 1);
			if (value > prevGroup.getStartTime()) {
				group.setStartTime(value);
				if (value < prevGroup.getEndTime()) {
					prevGroup.setEndTime(value);
				}
			}
		} else {
			if (value  > this.getStartTime()) {
				group.setStartTime(value);
			}
		}
	}

	public void setGroupEndTime(TimingGroupModel group, double value) {
		int index = groupList.indexOf(group);
		if (index != groupList.size() - 1) {
			TimingGroupModel nextGroup = (TimingGroupModel) groupList.get(index + 1);
			if (value < nextGroup.getEndTime()) {
				group.setEndTime(value);
				nextGroup.setStartTime(value);
			}
		} else {
			if (value < this.getEndTime()) {
				group.setEndTime(value);
			}
		}
	}

	public void setDurationInSec(double value) {
		double duration = getDurationInSec();
		this.setEndTime(this.getStartTime() + value * 1000); // Converts to milli
		this.firePropertyChange(DURATION_IN_SEC_PROP_NAME, duration, getDurationInSec());
	}

	public double getDurationInSec() {
		return (this.getDuration() / 1000); // Converts to sec
	}

	@Override
	public void setEndTime(double value) {
		super.setEndTime(value);
		double groupDuration = value / groupList.size();
		setGroupTimes(groupDuration);
	}

	@Override
	public void dispose() {}
}
