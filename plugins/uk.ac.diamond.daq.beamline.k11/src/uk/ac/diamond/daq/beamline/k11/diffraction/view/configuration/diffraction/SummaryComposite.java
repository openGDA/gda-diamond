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
		var points = numberOfPoints();
		var exposure = exposurePerPoint();
		var message = String.format("Points: %d; Exposure: %.2f s; Total exposure: %.2f s", points, exposure, points * exposure);
		summary.setText(message);
	}

	private int numberOfPoints() {
		var document = parameters.getScanpathDocument();
		switch (document.getModelDocument()) {
		case TWO_DIMENSION_GRID:
			return pointsInAxis(document.getScannableTrackDocuments().get(0)) * pointsInAxis(document.getScannableTrackDocuments().get(1));
		case TWO_DIMENSION_LINE:
			return pointsInAxis(document.getScannableTrackDocuments().get(0));
		case TWO_DIMENSION_POINT:
			return 1;
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
