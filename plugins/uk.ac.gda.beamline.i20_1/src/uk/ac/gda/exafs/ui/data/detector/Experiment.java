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

import gda.scan.ede.position.EdePositionType;
import gda.scan.ede.position.EdeScanPosition;
import gda.scan.ede.position.ExplicitScanPositions;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import de.jaret.util.date.IntervalImpl;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;


public class Experiment extends CollectionModel {
	public static final Experiment INSTANCE = new Experiment();
	private static final long DEFAULT_INITIAL_EXPERIMENT_TIME_IN_SEC = 20; // Should be > 0

	WritableList groupList = new WritableList(new ArrayList<Group>(), Group.class);
	private DefaultTimeBarModel model;
	private DefaultTimeBarRowModel timingGroupRow;
	private DefaultTimeBarRowModel spectrumRow;

	public static final String DELAY_BETWEEN_GROUPS_PROP_NAME = "delayBetweenGroups";
	private double delayBetweenGroups;

	public Experiment() {
		this.setStartTime(0.0);
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

	public void doCollection() throws Exception {
		EdeScanParameters edeScanParameters = new EdeScanParameters();
		for (Object object : groupList) {
			Group uiTimingGroup = (Group) object;
			TimingGroup timingGroup = new TimingGroup();
			timingGroup.setLabel(uiTimingGroup.getName());
			timingGroup.setNumberOfFrames(uiTimingGroup.getNumberOfSpectrums());
			timingGroup.setTimePerScan(uiTimingGroup.getIntegrationTime());
			timingGroup.setTimePerFrame(uiTimingGroup.getDuration());
			edeScanParameters.addGroup(timingGroup);
		}
		// TODO Complete implementation
		EdeScanPosition i0Position = new ExplicitScanPositions(
				EdePositionType.OUTBEAM,
				SingleSpectrumModel.INSTANCE.getI0xPosition(),
				SingleSpectrumModel.INSTANCE.getI0yPosition(),
				ClientConfig.ScannableSetup.SAMPLE_X_POSITION.getScannable(),
				ClientConfig.ScannableSetup.SAMPLE_Y_POSITION.getScannable());
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

	public static final String DURATION_IN_SEC_PROP_NAME = "durationInSec";
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
