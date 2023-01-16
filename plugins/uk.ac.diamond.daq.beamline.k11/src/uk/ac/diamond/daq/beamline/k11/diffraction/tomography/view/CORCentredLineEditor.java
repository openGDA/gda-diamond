/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.tomography.view;

import static uk.ac.gda.ui.tool.ClientSWTElements.label;

import org.eclipse.dawnsci.analysis.dataset.roi.LinearROI;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Text;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.LineScanpathEditor;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.region.SnappedLineMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;

/**
 * Expects a {@link SnappedLineMappingRegion}; centres region around centre of rotation
 */
public class CORCentredLineEditor extends LineScanpathEditor {

	private Text xLength;
	private Text yPosition;

	private CentreOfRotationLocator corLocator;

	@Override
	public Composite createEditorPart(Composite parent) {
		corLocator = new CentreOfRotationLocator(parent.getShell());
		return super.createEditorPart(parent);
	}

	@Override
	protected void createShapeControls(Composite composite) {
		label(composite, "X Length");
		xLength = createTextControls(composite);

		label(composite, "Y Position");
		yPosition = createTextControls(composite);
	}

	@Override
	protected void modelToControlsShape() {
		var x = Math.abs(getXAxis().getStop() - getXAxis().getStart());
		xLength.setText(DECIMAL_FORMAT.format(x));

		var y = getYAxis().getStart();
		yPosition.setText(DECIMAL_FORMAT.format(y));
	}

	@Override
	protected double xStart() {
		return corLocator.getCentreOfRotation() - Double.parseDouble(xLength.getText()) / 2.0;
	}

	@Override
	protected double xStop() {
		return corLocator.getCentreOfRotation() + Double.parseDouble(xLength.getText()) / 2.0;
	}

	@Override
	protected double yStart() {
		return Double.parseDouble(yPosition.getText());
	}

	@Override
	protected double yStop() {
		return yStart();
	}

	@Override
	protected IMappingScanRegionShape modelToMappingRegion() {
		var region = new SnappedLineMappingRegion();
		region.updateFromROI(new LinearROI(new double[] {getXAxis().getStart(), getYAxis().getStart()},
										   new double[] {getXAxis().getStop(), getYAxis().getStop()}));
		return region;
	}

	@Override
	protected void handleMappingUpdate(RegionPathState state) {
		var updatedRegion = state.scanRegionShape();
		if (updatedRegion instanceof SnappedLineMappingRegion newLine) {
			if (this.line != null) {
				this.line.removePropertyChangeListener(getRegionModifiedListener());
			}
			newLine.addPropertyChangeListener(getRegionModifiedListener());
			this.line = newLine;
		}
	}

	@Override
	protected void handleRegionMove() {
		super.handleRegionMove();
		if (handlingMappingUpdate) return;
		try {
			handlingMappingUpdate = true;
			var length = Math.abs(getXAxis().getStop() - getXAxis().getStart());
			var cor = corLocator.getCentreOfRotation();
			updateAxes(modifyAxis(getXAxis(), cor - length / 2.0, cor + length / 2.0, getXAxis().getPoints()), getYAxis());

			var y0 = getYAxis().getStart() + (getYAxis().getStop() - getYAxis().getStart()) / 2.0;
			line.centre(cor, y0);
		} finally {
			handlingMappingUpdate = false;
		}
	}

}
