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

import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Text;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.RectangleScanpathEditor;

/**
 * Centres region around centre of rotation
 */
public class CORCentredRectangleEditor extends RectangleScanpathEditor {

	private Text xLength;
	private CentreOfRotationLocator corLocator;

	@Override
	public Composite createEditorPart(Composite parent) {
		corLocator = new CentreOfRotationLocator(parent.getShell());
		return super.createEditorPart(parent);
	}

	@Override
	protected void createXControls(Composite composite) {
		space(composite);
		label(composite, "X Length");

		space(composite);
		xLength = createTextControls(composite);
	}

	private double length() {
		return Double.parseDouble(xLength.getText());
	}

	@Override
	protected double xStart() {
		return corLocator.getCentreOfRotation() - length() / 2.0;
	}

	@Override
	protected double xStop() {
		return corLocator.getCentreOfRotation() + length() / 2.0;
	}

	@Override
	protected void updateXControls() {
		var length = Math.abs(getXAxis().getStop() - getXAxis().getStart());
		xLength.setText(DECIMAL_FORMAT.format(length));
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
			rectangle.centre(cor, y0);
		} finally {
			handlingMappingUpdate = false;
		}
	}

	private void space(Composite composite) {
		label(composite, "");
	}

}
