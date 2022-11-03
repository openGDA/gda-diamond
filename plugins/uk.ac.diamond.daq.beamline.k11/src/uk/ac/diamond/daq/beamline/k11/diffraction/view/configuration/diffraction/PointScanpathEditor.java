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

import java.beans.PropertyChangeListener;

import org.eclipse.scanning.api.points.models.IMapPathModel;
import org.eclipse.scanning.api.points.models.TwoAxisPointSingleModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;

import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.region.PointMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.gda.ui.tool.ClientSWTElements;

public class PointScanpathEditor extends ScanpathEditor {

	private Text xStartText;
	private Text yStartText;

	private PointMappingRegion point;
	private PropertyChangeListener regionMoveListener = change -> handleRegionMove();

	private boolean handlingDocumentUpdate;

	@Override
	public Composite createEditorPart(Composite parent) {
		var mainComposite = super.createEditorPart(parent);

		var composite = ClientSWTElements.composite(mainComposite, 2);

		new Label(composite, SWT.NONE).setText("X Position");
		new Label(composite, SWT.NONE).setText("Y Position");
		xStartText = createTextControls(composite);
		yStartText = createTextControls(composite);

		modelToControls();

		return composite;
	}

	@Override
	protected void controlsToModel() {
		if (handlingDocumentUpdate) return;
		try {
			handlingDocumentUpdate = true;
			double xAxis = Double.parseDouble(xStartText.getText());
			double yAxis = Double.parseDouble(yStartText.getText());

			updatePoint(xAxis, yAxis);
		} finally {
			handlingDocumentUpdate = false;
		}
	}

	@Override
	protected void modelToControls() {
		if (handlingDocumentUpdate) return;
		try {
			handlingDocumentUpdate = true;
			xStartText.setText(DECIMAL_FORMAT.format(getXCoordinate()));
			yStartText.setText(DECIMAL_FORMAT.format(getYCoordinate()));
		} finally {
			handlingDocumentUpdate = false;
		}
	}

	@Override
	public void dispose() {
		if (point != null) {
			point.removePropertyChangeListener(regionMoveListener);
		}
		super.dispose();
	}

	@Override
	protected IMappingScanRegionShape modelToMappingRegion() {
		var region = new PointMappingRegion();
		region.setxPosition(getXCoordinate());
		region.setyPosition(getYCoordinate());
		return region;
	}

	@Override
	protected IMapPathModel modelToMappingPath() {
		var path = new TwoAxisPointSingleModel();
		path.setX(getXCoordinate());
		path.setY(getYCoordinate());
		path.setContinuous(false);
		path.setAlternating(false);
		return path;
	}

	private double getXCoordinate() {
		return getXAxis().getStart();
	}

	private double getYCoordinate() {
		return getYAxis().getStart();
	}

	@Override
	protected void handleMappingUpdate(RegionPathState state) {
		var updatedRegion = state.scanRegionShape();
		if (updatedRegion instanceof PointMappingRegion) {
			if (this.point != null) {
				this.point.removePropertyChangeListener(regionMoveListener);
			}
			PointMappingRegion newPoint = (PointMappingRegion) updatedRegion;
			newPoint.addPropertyChangeListener(regionMoveListener);
			this.point = newPoint;
		}
	}

	private void handleRegionMove() {
		if (handlingMappingUpdate) return;
		try {
			handlingMappingUpdate = true;
			var xAxis = point.getxPosition();
			var yAxis = point.getyPosition();
			updatePoint(xAxis, yAxis);
		} finally {
			handlingMappingUpdate = false;
		}
	}

	private void updatePoint(double xAxis, double yAxis) {
		updateAxes(modifyAxis(getXAxis(), xAxis, xAxis, 1),
				   modifyAxis(getYAxis(), yAxis, yAxis, 1));
	}

}