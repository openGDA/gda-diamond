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

		ScanningAcquistionListener acquisitionListener = new ScanningAcquistionListener();
		SpringApplicationContextFacade.addApplicationListener(acquisitionListener);

		composite.addDisposeListener(dispose -> SpringApplicationContextFacade.removeApplicationListener(acquisitionListener));

		return composite;
	}

	private void updateSummary() {
		if (summary == null || summary.isDisposed()) return;
		summary.setText(getSummary());
	}

	private String getSummary() {
		var document = parameters.getScanpathDocument();
		var xAxis = document.getScannableTrackDocuments().get(0);
		var yAxis = document.getScannableTrackDocuments().get(1);
		var exposure = exposurePerPoint();
		var points = 0;
		switch (document.getModelDocument()) {
		case TWO_DIMENSION_GRID:
			points = pointsInAxis(xAxis) * pointsInAxis(yAxis);
			var xStepSize = xAxis.calculatedStep();
			var yStepSize = yAxis.calculatedStep();
			return String.format("Points: %d; Step size X: %.2f, Y: %.2f;%nExposure: %.2f s; Total exposure: %.2f s", points, xStepSize, yStepSize, exposure, points * exposure);
		case TWO_DIMENSION_LINE:
			points = pointsInAxis(xAxis);
			var stepSize = Math.sqrt((xAxis.calculatedStep() * xAxis.calculatedStep()) + (yAxis.calculatedStep() * yAxis.calculatedStep()));
			return String.format("Points: %d; Step size: %.2f;%nExposure: %.2f s; Total exposure: %.2f s", points, stepSize, exposure, points * exposure);
		case TWO_DIMENSION_POINT:
			return String.format("Points: 1; Total exposure: %.2f s", exposure);
		default:
			throw new IllegalArgumentException("Unsupported type: " + document.getModelDocument().toString());
		}
	}

	private double exposurePerPoint() {
		return parameters.getDetectors().stream()
			.map(DetectorDocument::getExposure)
			.max(Double::compareTo).orElse(0.0);
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

	private class ScanningAcquistionListener implements ApplicationListener<ScanningAcquisitionChangeEvent> {

		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			refreshParameters();
			Display.getDefault().asyncExec(SummaryComposite.this::updateSummary);
		}
	}

}
