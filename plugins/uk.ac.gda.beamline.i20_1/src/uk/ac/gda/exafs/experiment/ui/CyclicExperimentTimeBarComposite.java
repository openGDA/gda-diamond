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

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.ControlListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;

import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.experiment.ui.data.CyclicExperimentModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentMarkerRenderer;
import uk.ac.gda.exafs.experiment.ui.data.TimeResolvedExperimentModel;
import de.jaret.util.ui.timebars.TimeBarMarker;
import de.jaret.util.ui.timebars.TimeBarViewerInterface;
import de.jaret.util.ui.timebars.swt.TimeBarViewer;

public class CyclicExperimentTimeBarComposite extends ResourceComposite {

	private final CyclicExperimentModel model;

	private TimeBarViewer timeBarViewer;

	public CyclicExperimentTimeBarComposite(Composite parent, int style, CyclicExperimentModel model) {
		super(parent, style);
		this.model = model;
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		setupUI();
		doBinding();
	}


	private void setupUI() {
		timeBarViewer = new TimeBarViewer(this, SWT.H_SCROLL | SWT.V_SCROLL);
		timeBarViewer.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		timeBarViewer.setTimeScalePosition(TimeBarViewerInterface.TIMESCALE_POSITION_TOP);

		timeBarViewer.setDrawRowGrid(true);
		timeBarViewer.setAutoScaleRows(1);
		timeBarViewer.setMilliAccuracy(true);
		timeBarViewer.setDrawOverlapping(true);
		timeBarViewer.setYAxisWidth(80);
		timeBarViewer.setTimeScaleRenderer(new CyclesTimebarScaleRenderer(model));
		timeBarViewer.setMarkerRenderer(new ExperimentMarkerRenderer());
		timeBarViewer.setModel(model.getCyclicTimeBarModel());

		timeBarViewer.addControlListener(new ControlListener() {
			@Override
			public void controlResized(ControlEvent e) {
				resetToDisplayWholeExperimentTime();
			}
			@Override
			public void controlMoved(ControlEvent e) {}
		});
		resetToDisplayWholeExperimentTime();
	}

	private final PropertyChangeListener modelChangedListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals(CyclicExperimentModel.CYCLES_DURATION_PROP_NAME)) {
				resetToDisplayWholeExperimentTime();
				updateTopupMarkers((double) evt.getNewValue());
			}
		}
	};

	private void doBinding() {
		model.addPropertyChangeListener(modelChangedListener);
	}

	protected void updateTopupMarkers(double duration) {
		if (timeBarViewer.getMarkers() != null) {
			timeBarViewer.getMarkers().clear();
		}
		for (TimeBarMarker marker : TimeResolvedExperimentModel.getTopupTimes()) {
			if (duration >= marker.getDate().getMillisInDay()) {
				timeBarViewer.addMarker(marker);
			}
		}
	}

	@Override
	protected void disposeResource() {
		model.removePropertyChangeListener(modelChangedListener);
	}

	private void resetToDisplayWholeExperimentTime() {
		timeBarViewer.scrollIntervalToVisible(timeBarViewer.getModel().getRow(0).getIntervals().get(0));
		double width = timeBarViewer.getClientArea().width - timeBarViewer.getYAxisWidth();
		if (width > 0 && model.getCyclesDurationInSec() > 0) {
			double pixelPerSecond = width / model.getCyclesDurationInSec();
			if (pixelPerSecond > 0) {
				timeBarViewer.setPixelPerSecond(pixelPerSecond);
			}
		}
	}

}
