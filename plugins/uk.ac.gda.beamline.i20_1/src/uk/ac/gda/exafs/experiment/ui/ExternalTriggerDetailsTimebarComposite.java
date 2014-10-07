/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.experiment.ui;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;

import uk.ac.gda.beamline.i20_1.utils.ExperimentTimeHelper;
import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;
import uk.ac.gda.exafs.experiment.ui.data.ExternalTriggerSetting;
import de.jaret.util.date.IntervalImpl;
import de.jaret.util.ui.timebars.TimeBarRowSorter;
import de.jaret.util.ui.timebars.TimeBarViewerInterface;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;
import de.jaret.util.ui.timebars.model.TimeBarRow;
import de.jaret.util.ui.timebars.swt.TimeBarViewer;
import de.jaret.util.ui.timebars.swt.renderer.DefaultGapRenderer;

public class ExternalTriggerDetailsTimebarComposite extends ResourceComposite {

	private TimeBarViewer timeBarViewer;
	private final ExternalTriggerSetting externalTriggerSetting;

	public ExternalTriggerDetailsTimebarComposite(ExternalTriggerSetting externalTriggerSetting, Composite parent, int style) {
		super(parent, style);
		this.externalTriggerSetting = externalTriggerSetting;
		setupUI();
		setupTimebar();
	}

	private void setupUI() {
		this.setLayout(new GridLayout());
		timeBarViewer = new TimeBarViewer(this, SWT.H_SCROLL | SWT.V_SCROLL);
		timeBarViewer.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		timeBarViewer.setTimeScalePosition(TimeBarViewerInterface.TIMESCALE_POSITION_TOP);

		timeBarViewer.setDrawRowGrid(true);
		timeBarViewer.setMilliAccuracy(true);
		timeBarViewer.setDrawOverlapping(false);
		timeBarViewer.setYAxisWidth(120);
		timeBarViewer.setDrawOverlapping(true);
	}

	private final DefaultTimeBarModel timebarModel = new DefaultTimeBarModel();
	private final Map<TriggerableObject, TimeBarRow> objectRowMap = new HashMap<TriggerableObject, TimeBarRow>();
	private final Map<TriggerableObject, PropertyChangeListener> objectPropertyListenerMap = new HashMap<TriggerableObject, PropertyChangeListener>();

	private void setupTimebar() {
		externalTriggerSetting.getSampleEnvironment().addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						TriggerableObject object = (TriggerableObject) element;
						removeRow(object);
					}
					@Override
					public void handleAdd(int index, Object element) {
						final TriggerableObject object = (TriggerableObject) element;
						addRow(object);
					}
				});
			}
		});
		for (Object element :externalTriggerSetting.getSampleEnvironment()) {
			addRow((TriggerableObject) element);
		}
		addRow(externalTriggerSetting.getTfgTrigger().getDetectorDataCollection());

		timeBarViewer.setModel(timebarModel);
		timeBarViewer.setAdjustMinMaxDatesByModel(true);
		timeBarViewer.setInitialDisplayRange(ExperimentTimeHelper.getTime(), (int) externalTriggerSetting.getTfgTrigger().getTotalTime() + 1);
		timeBarViewer.registerTimeBarRenderer(TFGTriggerEvent.class, new ExternalTriggerEventRenderer());
		timeBarViewer.setRowSorter(new TimeBarRowSorter() {

			@Override
			public void removePropertyChangeListener(PropertyChangeListener arg0) {}

			@Override
			public void addPropertyChangeListener(PropertyChangeListener arg0) {}

			@Override
			public int compare(TimeBarRow o1, TimeBarRow o2) {
				TriggerableObject obj1 = ((TFGTriggerEvent) o1.getIntervals().get(0)).getTriggerableObject();
				TriggerableObject obj2 = ((TFGTriggerEvent) o2.getIntervals().get(0)).getTriggerableObject();
				return ((obj1.getTriggerDelay() > obj2.getTriggerDelay()) ? 1 : -1);
			}
		});
		timeBarViewer.setGapRenderer(new DefaultGapRenderer());
		timeBarViewer.setStrictClipTimeCheck(true);
	}
	private void removeRow(TriggerableObject object) {
		timebarModel.remRow(objectRowMap.remove(object));
		object.removePropertyChangeListener(objectPropertyListenerMap.remove(object));
	}
	private void addRow(final TriggerableObject object) {
		final DefaultRowHeader header = new DefaultRowHeader(object.getName());
		final DefaultTimeBarRowModel timeBarRowModel = new DefaultTimeBarRowModel(header);

		final TFGTriggerEvent triggerEvent = new TFGTriggerEvent(object);
		timeBarRowModel.addInterval(triggerEvent);
		objectRowMap.put(object, timeBarRowModel);

		PropertyChangeListener listener = new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				switch (evt.getPropertyName()) {
				case TriggerableObject.NAME_PROP_NAME:
					header.setLabel((String) evt.getNewValue());
					break;
				case TriggerableObject.TRIGGER_DELAY_PROP_NAME:
					triggerEvent.setBegin(ExperimentTimeHelper.getTime().advanceSeconds(object.getTriggerDelay()));
					triggerEvent.setEnd(ExperimentTimeHelper.getTime().advanceSeconds(object.getTriggerDelay() + object.getTriggerPulseLength()));
					removeRow((TriggerableObject) evt.getSource());
					addRow((TriggerableObject) evt.getSource());
					break;
				case TriggerableObject.TOTAL_DELAY_PROP_NAME:
					triggerEvent.setEnd(ExperimentTimeHelper.getTime().advanceSeconds(object.getTotalDelay()));
					break;
				}
				updateZoom();
			}
		};
		object.addPropertyChangeListener(listener);
		objectPropertyListenerMap.put(object, listener);
		timebarModel.addRow(timeBarRowModel);

	}

	private void updateZoom() {
		timeBarViewer.setInitialDisplayRange(ExperimentTimeHelper.getTime(), (int) externalTriggerSetting.getTfgTrigger().getTotalTime() + 1);
	}

	@Override
	protected void disposeResource() {
		// Noting to dispose
	}

	public static class TFGTriggerEvent extends IntervalImpl {
		private final TriggerableObject triggerableObject;

		public TFGTriggerEvent(TriggerableObject triggerableObject) {
			super(ExperimentTimeHelper.getTime().advanceSeconds(triggerableObject.getTriggerDelay()), ExperimentTimeHelper.getTime().advanceSeconds(triggerableObject.getTotalDelay()));
			this.triggerableObject = triggerableObject;
		}

		public TriggerableObject getTriggerableObject() {
			return triggerableObject;
		}
	}
}
