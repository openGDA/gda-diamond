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

package uk.ac.gda.exafs.experiment.ui;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.ControlListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Scale;

import de.jaret.util.date.Interval;
import de.jaret.util.date.JaretDate;
import de.jaret.util.ui.timebars.TimeBarMarker;
import de.jaret.util.ui.timebars.TimeBarMarkerImpl;
import de.jaret.util.ui.timebars.TimeBarViewerInterface;
import de.jaret.util.ui.timebars.model.ITimeBarChangeListener;
import de.jaret.util.ui.timebars.model.TimeBarRow;
import de.jaret.util.ui.timebars.swt.TimeBarViewer;
import uk.ac.gda.beamline.i20_1.utils.ExperimentTimeHelper;
import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.experiment.ui.data.CollectionModelRenderer;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentMarkerRenderer;
import uk.ac.gda.exafs.experiment.ui.data.SpectrumModel;
import uk.ac.gda.exafs.experiment.ui.data.TimeIntervalDataModel;
import uk.ac.gda.exafs.experiment.ui.data.TimeResolvedExperimentModel;
import uk.ac.gda.exafs.experiment.ui.data.TimingGroupUIModel;
import uk.ac.gda.exafs.experiment.ui.data.TimingGroupsScaleRenderer;

public class ExperimentTimeBarComposite extends ResourceComposite {

	private static final long INITIAL_TIMEBAR_MARKER_IN_MILLI = 10L;
	private static final int TIMEBAR_ZOOM_FACTOR = 10;

	private TimeBarViewer timeBarViewer;
	private TimeBarMarkerImpl marker;
	private Scale scale;
	private final TimeResolvedExperimentModel model;

	public ExperimentTimeBarComposite(Composite parent, int style, TimeResolvedExperimentModel model) {
		super(parent, style);
		this.model = model;
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		setupUI();
		doBinding();
	}

	private final PropertyChangeListener modelChangedListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			String propertyName = evt.getPropertyName();
			Object newValue =  evt.getNewValue();
			if (propertyName.equals(TimeResolvedExperimentModel.UNIT_PROP_NAME)) {
				timeBarViewer.redraw();
			} else if (propertyName.equals(TimeResolvedExperimentModel.SCANNING_PROP_NAME)) {
				if ((boolean) newValue) {
					marker.setDate(ExperimentTimeHelper.getTime());
					timeBarViewer.addMarker(marker);
				} else {
					timeBarViewer.remMarker(marker);
				}
			} else if (propertyName.equals(TimeResolvedExperimentModel.CURRENT_SCANNING_SPECTRUM_PROP_NAME)) {
				SpectrumModel spectrum = (SpectrumModel) evt.getNewValue();
				marker.setDate(spectrum.getEnd().copy());
			}
		}
	};


	private final PropertyChangeListener experimentChangedListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			String propertyName = evt.getPropertyName();
			Object newValue =  evt.getNewValue();
			if (propertyName.equals(TimeIntervalDataModel.DURATION_PROP_NAME)) {
				resetToDisplayWholeExperimentTime();
				updateScaleSelection();
				updateTopupMarkers((double) newValue);
			}
		}
	};

	private void doBinding() {
		model.getTimeIntervalDataModel().addPropertyChangeListener(experimentChangedListener);
		model.addPropertyChangeListener(modelChangedListener);
	}

	private void setupUI() {
		timeBarViewer = new TimeBarViewer(this, SWT.H_SCROLL | SWT.V_SCROLL);
		timeBarViewer.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		timeBarViewer.setTimeScalePosition(TimeBarViewerInterface.TIMESCALE_POSITION_TOP);

		timeBarViewer.setDrawRowGrid(true);
		timeBarViewer.setAutoScaleRows(2);

		timeBarViewer.setMilliAccuracy(true);
		timeBarViewer.setDrawOverlapping(true);
		timeBarViewer.setYAxisWidth(80);

		timeBarViewer.registerTimeBarRenderer(TimingGroupUIModel.class, new CollectionModelRenderer(model));
		timeBarViewer.registerTimeBarRenderer(SpectrumModel.class, new CollectionModelRenderer(model));
		timeBarViewer.setTimeScaleRenderer(new TimingGroupsScaleRenderer(model));
		timeBarViewer.setModel(model.getTimeBarModel());
		resetToDisplayWholeExperimentTime();
		timeBarViewer.setAdjustMinMaxDatesByModel(true);
		timeBarViewer.setLineDraggingAllowed(false);
		marker = new TimeBarMarkerImpl(true, ExperimentTimeHelper.getTime().advanceMillis(INITIAL_TIMEBAR_MARKER_IN_MILLI));
		timeBarViewer.addTimeBarChangeListener(new ITimeBarChangeListener() {

			@Override
			public void markerDragStopped(TimeBarMarker timeBarMarker) {
				if (timeBarMarker.getDate().getMillis() == 0) {
					timeBarViewer.setStartDate(ExperimentTimeHelper.getTime());
					marker.setDate(ExperimentTimeHelper.getTime().advanceMillis(INITIAL_TIMEBAR_MARKER_IN_MILLI));
				}
			}

			@Override
			public void markerDragStarted(TimeBarMarker arg0) {}

			@Override
			public void intervalIntermediateChange(TimeBarRow arg0, Interval arg1, JaretDate arg2, JaretDate arg3) {}

			@Override
			public void intervalChanged(TimeBarRow arg0, Interval arg1, JaretDate arg2, JaretDate arg3) {}

			@Override
			public void intervalChangeStarted(TimeBarRow arg0, Interval arg1) {}

			@Override
			public void intervalChangeCancelled(TimeBarRow arg0, Interval arg1) {}
		});


		timeBarViewer.addControlListener(new ControlListener() {
			@Override
			public void controlResized(ControlEvent e) {
				updateScaleSelection();
			}
			@Override
			public void controlMoved(ControlEvent e) {}
		});

		timeBarViewer.setMarkerRenderer(new ExperimentMarkerRenderer());


		// Controls
		Composite controls = new Composite(this, SWT.None);
		controls.setLayoutData(new GridData(SWT.END, SWT.FILL, false, true));
		controls.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		scale = new Scale(controls, SWT.VERTICAL);

		// TODO Adjust accordingly
		scale.setMinimum(10);
		scale.setSelection(10);
		scale.setMaximum(1000);

		scale.setIncrement(100);
		scale.setPageIncrement(500);

		scale.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		scale.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				int selection = scale.getSelection();
				timeBarViewer.setPixelPerSecond((double) selection / 1000);
				if (selection == scale.getMinimum()) {
					resetToDisplayWholeExperimentTime();
				} else {
					IStructuredSelection structuredSelection = (IStructuredSelection) timeBarViewer.getSelection();
					if (structuredSelection.getFirstElement() != null) {
						timeBarViewer.scrollIntervalToVisible((Interval) structuredSelection.getFirstElement());
					}
				}
			}
		});
		updateTopupMarkers(model.getDuration());
	}

	public TimeBarViewer getTimeBarViewer() {
		return timeBarViewer;
	}

	private void updateTopupMarkers(double duration) {
		if (timeBarViewer.getMarkers() != null) {
			timeBarViewer.getMarkers().clear();
		}
		for (TimeBarMarker marker : TimeResolvedExperimentModel.getTopupTimes()) {
			if (duration >= marker.getDate().getMillisInDay()) {
				timeBarViewer.addMarker(marker);
			}
		}
	}

	private void resetToDisplayWholeExperimentTime() {
		//timeBarViewer.scrollIntervalToVisible((Interval) model.getGroupList().get(0));
		timeBarViewer.scrollDateToVisible(ExperimentTimeHelper.getTime());
		double width = timeBarViewer.getClientArea().width - timeBarViewer.getYAxisWidth();
		if (width > 0) {
			double pixelPerSecond = width / (model.getDurationInSec());
			if (pixelPerSecond > 0) {
				timeBarViewer.setPixelPerSecond(pixelPerSecond);
			}
		}
	}

	private void updateScaleSelection() {
		double width = timeBarViewer.getClientArea().width - timeBarViewer.getYAxisWidth();
		if (width > 0) {
			double pixelPerSecond = width / model.getDurationInSec();
			scale.setMaximum((int)(TIMEBAR_ZOOM_FACTOR * pixelPerSecond * 1000));
			scale.setMinimum((int) (pixelPerSecond * 1000));
			scale.setSelection(scale.getMinimum());
			if (pixelPerSecond > 0) {
				timeBarViewer.setPixelPerSecond((double) scale.getSelection() / 1000);
			}
		}
	}

	@Override
	protected void disposeResource() {
		model.removePropertyChangeListener(modelChangedListener);
	}

}
