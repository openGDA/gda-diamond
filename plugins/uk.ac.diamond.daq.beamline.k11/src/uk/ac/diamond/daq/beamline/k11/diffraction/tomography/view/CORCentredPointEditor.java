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

import java.beans.PropertyChangeListener;

import org.eclipse.scanning.api.points.models.IMapPathModel;
import org.eclipse.scanning.api.points.models.TwoAxisPointSingleModel;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Text;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ScanpathEditor;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.constants.RegionConstants;
import uk.ac.diamond.daq.mapping.region.PointMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.gda.ui.tool.ClientSWTElements;

/**
 * Centres point around centre of rotation
 */
public class CORCentredPointEditor extends ScanpathEditor {

	private Text yPosition;

	private PointMappingRegion point;

	private PropertyChangeListener regionMoveListener = change -> {
		if (change.getPropertyName().equals(RegionConstants.UPDATE_COMPLETE)) {
			handleRegionMove();
		}
	};

	private CentreOfRotationLocator corLocator;

	private boolean handlingDocumentUpdate;

	@Override
	public Composite createEditorPart(Composite parent) {
		var mainComposite = super.createEditorPart(parent);

		var composite = ClientSWTElements.composite(mainComposite, 2);

		space(composite);
		ClientSWTElements.label(composite, "Y Position");

		space(composite);
		yPosition = createTextControls(composite);

		modelToControls();

		corLocator = new CentreOfRotationLocator(composite.getShell());

		return composite;
	}

	private void space(Composite composite) {
		ClientSWTElements.label(composite, "");
	}

	@Override
	protected void controlsToModel() {
		if (handlingDocumentUpdate) return;
		try {
			handlingDocumentUpdate = true;

			var x = corLocator.getCentreOfRotation();
			var y = Double.parseDouble(yPosition.getText());

			updatePoint(x, y);
		} finally {
			handlingDocumentUpdate = false;
		}
	}

	@Override
	protected void modelToControls() {
		if (handlingDocumentUpdate) return;
		try {
			handlingDocumentUpdate = true;
			var y = getYAxis().getStart();
			yPosition.setText(DECIMAL_FORMAT.format(y));
		} finally {
			handlingDocumentUpdate = false;
		}
	}

	@Override
	protected IMappingScanRegionShape modelToMappingRegion() {
		var region = new PointMappingRegion();
		region.setxPosition(getXAxis().getStart());
		region.setyPosition(getYAxis().getStart());
		return region;
	}

	@Override
	protected IMapPathModel modelToMappingPath() {
		var path = new TwoAxisPointSingleModel();
		path.setX(getXAxis().getStart());
		path.setY(getYAxis().getStart());
		path.setContinuous(false);
		path.setAlternating(false);
		return path;
	}

	@Override
	protected void handleMappingUpdate(RegionPathState state) {
		var updatedRegion = state.scanRegionShape();
		if (updatedRegion instanceof PointMappingRegion newPoint) {
			if (this.point != null) {
				this.point.removePropertyChangeListener(regionMoveListener);
			}
			newPoint.addPropertyChangeListener(regionMoveListener);
			this.point = newPoint;
		}
	}

	private void handleRegionMove() {
		if (handlingMappingUpdate) return;
		try {
			handlingMappingUpdate = true;
			var x = corLocator.getCentreOfRotation();
			var y = point.getyPosition();

			point.centre(x, y);

			updatePoint(x, y);
		} finally {
			handlingMappingUpdate = false;
		}
	}

	private void updatePoint(double xAxis, double yAxis) {
		updateAxes(modifyAxis(getXAxis(), xAxis, xAxis, 1),
				   modifyAxis(getYAxis(), yAxis, yAxis, 1));
	}
}
