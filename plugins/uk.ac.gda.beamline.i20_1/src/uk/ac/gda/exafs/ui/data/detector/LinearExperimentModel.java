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

package uk.ac.gda.exafs.ui.data.detector;

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

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.UIHelper;
import de.jaret.util.date.IntervalImpl;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;


public class LinearExperimentModel extends CollectionModel {

	public static final LinearExperimentModel INSTANCE = new LinearExperimentModel();

	private static final String TIMING_GROUPS_OBJ_NAME = "timingGroups";

	private static final double EXPERIMENT_START_TIME = 0.0;
	private static final long DEFAULT_INITIAL_EXPERIMENT_TIME_IN_SEC = 20; // Should be > 0

	public static final String DURATION_IN_SEC_PROP_NAME = "durationInSec";

	private static final String DATA_PROPERTIES_KEY_NAME = "LinearExperimentModel";

	private DefaultTimeBarModel model;
	private DefaultTimeBarRowModel timingGroupRow;
	private DefaultTimeBarRowModel spectrumRow;

	public static final String CURRENT_SCANNING_SPECTRUM_PROP_NAME = "currentScanningSpectrum";
	private Spectrum currentScanningSpectrum;

	public static final String SCANNING_PROP_NAME = "scanning";
	private boolean scanning;

	public static final String DELAY_BETWEEN_GROUPS_PROP_NAME = "delayBetweenGroups";
	private double delayBetweenGroups;

	WritableList groupList = new WritableList(new ArrayList<Group>(), Group.class);

	private final ScanJob job;

	public LinearExperimentModel() {
		this.setStartTime(EXPERIMENT_START_TIME);
		this.setDurationInSec(DEFAULT_INITIAL_EXPERIMENT_TIME_IN_SEC);
		setupTimebarModel();
		groupList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						timingGroupRow.remInterval((IntervalImpl) element);
					}

					@Override
					public void handleAdd(int index, Object element) {
						timingGroupRow.addInterval((IntervalImpl) element);
					}
				});
			}
		});

		job = new ScanJob("Performing Linear Experiment");
		InterfaceProvider.getJSFObserver().addIObserver(job);
		Findable controller = Finder.getInstance().findNoWarn(EdeExperiment.PROGRESS_UPDATER_NAME);
		if (controller != null) {
			((Scriptcontroller) controller).addIObserver(job);
		}
		job.setUser(true);

		loadSavedGroups();
	}

	private void loadSavedGroups() {
		Group[] savedGroups = ClientConfig.EdeDataStore.INSTANCE.loadConfiguration(DATA_PROPERTIES_KEY_NAME, Group[].class);
		if (savedGroups == null) {
			addGroup();
			return;
		}
		for (Group loadedGroup : savedGroups) {
			Group newGroup = new Group(spectrumRow);
			newGroup.setStartTime(loadedGroup.getStartTime());
			newGroup.setEndTime(loadedGroup.getEndTime());
			newGroup.setDelay(loadedGroup.getDelay());
			newGroup.setName(loadedGroup.getName());
			newGroup.setIntegrationTime(loadedGroup.getIntegrationTime());
			newGroup.setTimePerSpectrum(loadedGroup.getTimePerSpectrum());
			newGroup.setDelayBetweenSpectrum(loadedGroup.getDelayBetweenSpectrum());
			addToInternalGroupList(newGroup);
		}
	}

	private void setupTimebarModel() {
		model = new DefaultTimeBarModel();
		DefaultRowHeader header = new DefaultRowHeader("Timing Groups");
		timingGroupRow = new DefaultTimeBarRowModel(header);
		header = new DefaultRowHeader("Spectrum");
		spectrumRow = new DefaultTimeBarRowModel(header);
		model.addRow(timingGroupRow);
		model.addRow(spectrumRow);
	}

	public DefaultTimeBarModel getTimeBarModel() {
		return model;
	}

	public List<?> getGroupList() {
		return groupList;
	}

	public Group addGroup() {
		Group newGroup = new Group(spectrumRow);
		newGroup.setStartTime(this.getStartTime());
		newGroup.setEndTime(this.getEndTime());
		newGroup.setName("Group " + (groupList.size() + 1));
		addToInternalGroupList(newGroup);
		setAllGroupTimes();
		ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(DATA_PROPERTIES_KEY_NAME, groupList);
		return newGroup;
	}

	private final PropertyChangeListener groupPropertyChangeListener = new PropertyChangeListener() {

		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(DATA_PROPERTIES_KEY_NAME, groupList);
		}
	};

	private void addToInternalGroupList(Group newGroup) {
		newGroup.addPropertyChangeListener(groupPropertyChangeListener);
		groupList.add(newGroup);
	}

	private void removeFromInternalGroupList(Group group) {
		group.removePropertyChangeListener(groupPropertyChangeListener);
		groupList.remove(group);
	}

	public void removeGroup(Group group) {
		group.getSpectrumList().clear();
		removeFromInternalGroupList(group);
		setAllGroupTimes();
		ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(DATA_PROPERTIES_KEY_NAME, groupList);
	}

	final Vector<TimingGroup> timingGroups = new Vector<TimingGroup>();

	public void doCollection() {
		timingGroups.clear();
		for (Object object : groupList) {
			Group uiTimingGroup = (Group) object;
			TimingGroup timingGroup = new TimingGroup();
			timingGroup.setLabel(uiTimingGroup.getName());
			timingGroup.setNumberOfFrames(uiTimingGroup.getNumberOfSpectrums());
			timingGroup.setTimePerScan(uiTimingGroup.getIntegrationTime());
			timingGroup.setTimePerFrame(uiTimingGroup.getDuration());
			timingGroup.setNumberOfScansPerFrame(uiTimingGroup.getNoOfAccumulations());
			timingGroups.add(timingGroup);
		}
		job.schedule();
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
		private IProgressMonitor monitor;
		private int frame;
		private int group;
		public ScanJob(String name) {
			super(name);
		}

		@Override
		public void update(Object source, Object arg) {
			if (arg instanceof JythonServerStatus) {
				JythonServerStatus status = (JythonServerStatus) arg;
				if (LinearExperimentModel.this.isScanning() && Jython.IDLE == status.scanStatus) {
					monitor.worked(1);
				}
				else if (arg instanceof EdeExperimentProgressBean) {
					final EdeExperimentProgressBean edeExperimentProgress = (EdeExperimentProgressBean) arg;
					Display.getDefault().syncExec(new Runnable() {
						@Override
						public void run() {
							int currentFrame =  edeExperimentProgress.getProgress().getFrameNumOfThisSDP();
							int currentGroup =  edeExperimentProgress.getProgress().getFrameNumOfThisSDP();
						}
					});
				}
			}
		}

		@Override
		protected IStatus run(IProgressMonitor monitor) {
			this.monitor = monitor;
			frame = 0;
			group = 0;
			monitor.beginTask("Scannable", 1);
			Display.getDefault().syncExec(new Runnable() {
				@Override
				public void run() {
					LinearExperimentModel.this.setScanning(true);
					for (Object object : groupList) {
						Group uiTimingGroup = (Group) object;
						TimingGroup timingGroup = new TimingGroup();
						timingGroup.setLabel(uiTimingGroup.getName());
						timingGroup.setNumberOfFrames(uiTimingGroup.getNumberOfSpectrums());
						timingGroup.setTimePerScan(uiTimingGroup.getIntegrationTime() / 1000.0); // convert from ms to s
						timingGroup.setTimePerFrame(uiTimingGroup.getTimePerSpectrum() / 1000.0); // convert from ms to s
						timingGroups.add(timingGroup);
					}
				}
			});
			InterfaceProvider.getJythonNamespace().placeInJythonNamespace(TIMING_GROUPS_OBJ_NAME, timingGroups);
			String scanCommand = buildScanCommand();
			InterfaceProvider.getCommandRunner().runCommand(scanCommand);
			try {
				// give the previous command a chance to run before calling doCollection()
				Thread.sleep(50);
				InterfaceProvider.getCommandRunner().runCommand(buildScanCommand());
				final String resultFileName = InterfaceProvider.getCommandRunner().evaluateCommand("scan_driver.doCollection()");
				if (resultFileName == null) {
					throw new Exception("Unable to do collection.");
				}
			} catch (Exception e) {
				UIHelper.showWarning("Error while scanning or canceled", e.getMessage());
			}
			Display.getDefault().syncExec(new Runnable() {
				@Override
				public void run() {
					LinearExperimentModel.this.setScanning(false);
				}
			});
			monitor.done();
			return Status.OK_STATUS;
		}

		@Override
		protected void canceling() {
			doStop();
		}
	}

	public void doStop() {
		if (this.isScanning()) {
			JythonServerFacade.getInstance().haltCurrentScan();
		}
	}

	protected void setScanning(boolean value) {
		this.firePropertyChange(SCANNING_PROP_NAME, scanning, scanning = value);
	}

	public boolean isScanning() {
		return scanning;
	}

	public Spectrum getCurrentScanningSpectrum() {
		return currentScanningSpectrum;
	}

	public void setCurrentScanningSpectrum(Spectrum value) {
		this.firePropertyChange(CURRENT_SCANNING_SPECTRUM_PROP_NAME, currentScanningSpectrum, currentScanningSpectrum = value);
	}

	private void setAllGroupTimes() {
		if (!groupList.isEmpty()) {
			double duration;
			if (groupList.size() ==  1 | delayBetweenGroups == 0) {
				duration = this.getDuration() / groupList.size();
			} else {
				duration = this.getDuration() - ((groupList.size() - 1) * delayBetweenGroups) / groupList.size();
			}
			double startTime = this.getStartTime();
			for (int i = 0; i < groupList.size(); i++) {
				Group entry = (Group) groupList.get(i);
				entry.setStartTime(startTime);
				entry.setEndTime(startTime + duration);
				startTime = entry.getEndTime() + delayBetweenGroups;
			}
		}
	}

	private void setGroupTimes(double groupDuration) {
		for (int i = 0; i < groupList.size(); i++) {
			Group group = (Group) groupList.get(i);
			if (i > 0) {
				Group previous = (Group) groupList.get(i-1);
				group.setStartTime(previous.getEndTime());
			}
			group.setEndTime(group.getStartTime() + groupDuration);
		}
	}

	public void setGroupStartTime(Group group, double value) {
		int index = groupList.indexOf(group);
		if (index != 0) {
			Group prevGroup = (Group) groupList.get(index - 1);
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

	public void setGroupEndTime(Group group, double value) {
		int index = groupList.indexOf(group);
		if (index != groupList.size() - 1) {
			Group nextGroup = (Group) groupList.get(index + 1);
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
		this.setEndTime(this.getStartTime() + value * 1000);
		this.firePropertyChange(DURATION_IN_SEC_PROP_NAME, duration, getDurationInSec());

	}

	public double getDurationInSec() {
		return (this.getDuration() / 1000);
	}

	@Override
	public void setEndTime(double value) {
		super.setEndTime(value);
		double groupDuration = value / groupList.size();
		setGroupTimes(groupDuration);
	}

	public double getDelayBetweenGroups() {
		return delayBetweenGroups;
	}


	public void setDelayBetweenGroups(double value) {
		this.firePropertyChange(DELAY_BETWEEN_GROUPS_PROP_NAME, delayBetweenGroups, delayBetweenGroups = value);
		setAllGroupTimes();
	}

	@Override
	public void dispose() {}
}
