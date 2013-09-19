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

import gda.jython.InterfaceProvider;
import gda.jython.JythonServerFacade;
import gda.observable.IObserver;

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

import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.data.UIHelper;
import de.jaret.util.date.IntervalImpl;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;


public class LinearExperimentModel extends CollectionModel {

	private static final String TIMING_GROUPS_OBJ_NAME = "timingGroups";

	public static final LinearExperimentModel INSTANCE = new LinearExperimentModel();

	private static final double EXPERIMENT_START_TIME = 0.0;
	private static final long DEFAULT_INITIAL_EXPERIMENT_TIME_IN_SEC = 20; // Should be > 0

	public static final String DURATION_IN_SEC_PROP_NAME = "durationInSec";

	private DefaultTimeBarModel model;
	private DefaultTimeBarRowModel timingGroupRow;
	private DefaultTimeBarRowModel spectrumRow;

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
		addGroup();

		job = new ScanJob("Performing Single spectrum scan");
		InterfaceProvider.getJSFObserver().addIObserver(job);
		job.setUser(true);
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

	public void addGroup() {
		Group group = new Group(spectrumRow);
		group.setStartTime(this.getStartTime());
		group.setEndTime(this.getEndTime());
		group.setName("Group " + (groupList.size() + 1));
		groupList.add(group);
		setAllGroupTimes();
	}

	public void removeGroup(Group group) {
		group.getSpectrumList().clear();
		groupList.remove(group);
		setAllGroupTimes();
	}

	public void doCollection() {
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
		public ScanJob(String name) {
			super(name);
		}

		@Override
		public void update(Object source, Object arg) {
			//
		}

		@Override
		protected IStatus run(IProgressMonitor monitor) {
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					LinearExperimentModel.this.setScanning(true);
				}
			});
			monitor.beginTask("Scannable", 1);
			final Vector<TimingGroup> timingGroups = new Vector<TimingGroup>();
			Display.getDefault().syncExec(new Runnable() {
				@Override
				public void run() {
					LinearExperimentModel.this.setScanning(true);
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
				}
			});

			InterfaceProvider.getJythonNamespace().placeInJythonNamespace(TIMING_GROUPS_OBJ_NAME, timingGroups);
			InterfaceProvider.getCommandRunner().runCommand(buildScanCommand());
			try {
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
