/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction;

import java.util.stream.Collectors;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.springframework.context.ApplicationListener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.Trajectory;
import uk.ac.gda.api.acquisition.TrajectoryShape;
import uk.ac.gda.api.acquisition.parameters.DetectorDocument;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;

public class SummaryComposite implements CompositeFactory, Reloadable {

	private Label summary;

	private ScanningParameters parameters;

	@Override
	public Composite createComposite(Composite parent, int style) {
		var stretch = GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).grab(true, false);

		var composite = new Composite(parent, SWT.NONE);

		stretch.applyTo(composite);
		GridLayoutFactory.swtDefaults().applyTo(composite);

		summary = new Label(composite, SWT.NONE);
		stretch.applyTo(summary);

		refreshParameters();
		updateSummary();

		ScanningAcquisitionListener acquisitionListener = new ScanningAcquisitionListener();
		SpringApplicationContextFacade.addApplicationListener(acquisitionListener);

		composite.addDisposeListener(dispose -> SpringApplicationContextFacade.removeApplicationListener(acquisitionListener));

		return composite;
	}

	private void updateSummary() {
		if (summary == null || summary.isDisposed()) return;
		summary.setText(getSummary());
	}

	private String getSummary() {
		var trajectories = parameters.getScanpathDocument().getTrajectories();
		var points = trajectories.stream().map(this::points).reduce(1, (t1, t2) -> t1 * t2);
		var step = trajectories.stream().map(this::stepSize)
				.filter(result -> !result.isBlank()).collect(Collectors.joining(", "));

		var summaryBuilder = new StringBuilder();
		summaryBuilder.append("Points: ").append(points).append("; ");
		if (!step.isBlank()) {
			summaryBuilder.append("Step size: ").append(step).append(";\n");
		}
		summaryBuilder.append(getExposureSummary(points));
		return summaryBuilder.toString();
	}

	private int points(Trajectory trajectory) {
		return switch (trajectory.getShape()) {
			case TWO_DIMENSION_POINT -> 1;
			case STATIC_POINT, ONE_DIMENSION_LINE, TWO_DIMENSION_LINE -> trajectory.getAxes().stream().mapToInt(this::pointsInAxis).max().orElse(1);
			case TWO_DIMENSION_GRID -> pointsInAxis(trajectory.getAxes().get(0)) * pointsInAxis(trajectory.getAxes().get(1));
			default -> throw new IllegalArgumentException("Unrecognised shape: " + trajectory.getShape());
		};
	}

	private String stepSize(Trajectory trajectory) {
		if (trajectory.getShape() == TrajectoryShape.STATIC_POINT || trajectory.getShape() == TrajectoryShape.TWO_DIMENSION_POINT) {
			return "";
		}
		return trajectory.getAxes().stream().map(this::oneDLineStepSize).collect(Collectors.joining(", "));
	}

	private String oneDLineStepSize(ScannableTrackDocument line) {
		return String.format("%s: %.2f", line.getAxis(), line.calculatedStep());
	}

	private String getExposureSummary(int points) {
		var exposurePerPoint = exposurePerPoint();
		if (points == 1) {
			return String.format("Total exposure: %.3f s", exposurePerPoint);
		}
		return String.format("Exposure: %.3f s; Total exposure: %.3f s", exposurePerPoint, exposurePerPoint * points);
	}

	/**
	 * This assumes sequential triggering of detectors,
	 * which is true for the K11 collections at this time
	 */
	private double exposurePerPoint() {
		return parameters.getDetectors().stream()
			.collect(Collectors.summingDouble(DetectorDocument::getExposure));
	}

	private int pointsInAxis(ScannableTrackDocument axis) {
		if (axis.getStep() == 0.0) {
			return axis.getPoints();
		} else {
			return (int) (Math.abs(axis.getStop() - axis.getStart()) / axis.getStep());
		}
	}

	@Override
	public void reload() {
		updateSummary();
	}

	private void refreshParameters() {
		parameters = SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class).getScanningParameters().orElseThrow();
	}

	private class ScanningAcquisitionListener implements ApplicationListener<ScanningAcquisitionChangeEvent> {

		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			refreshParameters();
			Display.getDefault().asyncExec(SummaryComposite.this::updateSummary);
		}
	}

}
