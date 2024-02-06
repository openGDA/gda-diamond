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

import org.eclipse.scanning.api.points.models.BoundingLine;
import org.eclipse.scanning.api.points.models.IMapPathModel;
import org.eclipse.scanning.api.points.models.TwoAxisLinePointsModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;

import uk.ac.diamond.daq.mapping.api.ILineMappingRegion;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.constants.RegionConstants;
import uk.ac.diamond.daq.mapping.region.LineMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.gda.ui.tool.ClientSWTElements;

public class LineScanpathEditor extends ScanpathEditor {

	private Text xStartText;
	private Text yStartText;
	private Text xStopText;
	private Text yStopText;

	private Spinner pointsSpinner;

	private Button stepButton;
	private Button continuousButton;

	protected ILineMappingRegion line;

	private PropertyChangeListener regionMoveListener = change -> {
		if (change.getPropertyName().equals(RegionConstants.UPDATE_COMPLETE)) {
			handleRegionMove();
		}
	};

	private boolean handlingDocumentUpdate;

	@Override
	public Composite createEditorPart(Composite parent) {
		var mainComposite = super.createEditorPart(parent);

		createRegionControls(mainComposite);
		createMutatorsControls(mainComposite);

		modelToControls();

		return mainComposite;

	}

	private void createRegionControls(Composite parent) {
		Composite composite = ClientSWTElements.composite(parent, 2);

		createShapeControls(composite);
		createPathControls(composite);
	}

	protected void createShapeControls(Composite composite) {
		new Label(composite, SWT.NONE).setText("X Start");
		new Label(composite, SWT.NONE).setText("X Stop");
		xStartText = createTextControls(composite);
		xStopText = createTextControls(composite);

		new Label(composite, SWT.NONE).setText("Y Start");
		new Label(composite, SWT.NONE).setText("Y Stop");
		yStartText = createTextControls(composite);
		yStopText = createTextControls( composite);
	}

	private void createPathControls(Composite composite) {
		new Label(composite, SWT.NONE).setText("Points");
		pointsSpinner = createSpinner(composite);
	}

	private void createMutatorsControls(Composite parent) {
		Composite composite = ClientSWTElements.composite(parent, 2);

		stepButton = new Button(composite, SWT.RADIO);
		stepButton.setText("Step");

		continuousButton = new Button(composite, SWT.RADIO);
		continuousButton.setText("Continuous");
		continuousButton.addSelectionListener(SelectionListener.widgetSelectedAdapter(this::handleMutatorSelection));
	}

	private void handleMutatorSelection(SelectionEvent event) {

		var button = (Button) event.getSource();
		var continuous = button.getSelection();

		getXAxis().setContinuous(continuous);
		getYAxis().setContinuous(continuous);

		updateModel(getModel());

	}


	@Override
	protected void controlsToModel() {
		if (handlingDocumentUpdate) return;
		try {
			handlingDocumentUpdate = true;
			int numberPoints = Integer.parseInt(pointsSpinner.getText());
			updateAxes(modifyAxis(getXAxis(), xStart(), xStop(), numberPoints),
					   modifyAxis(getYAxis(), yStart(), yStop(), numberPoints));
		} finally {
			handlingDocumentUpdate = false;
		}
	}

	protected double xStart() {
		return Double.parseDouble(xStartText.getText());
	}

	protected double xStop() {
		return Double.parseDouble(xStopText.getText());
	}

	protected double yStart() {
		return Double.parseDouble(yStartText.getText());
	}

	protected double yStop() {
		return Double.parseDouble(yStopText.getText());
	}

	protected int getPoints() {
		return Integer.parseInt(pointsSpinner.getText());
	}

	@Override
	protected void modelToControls() {
		if (handlingDocumentUpdate) return;
		try {
			handlingDocumentUpdate = true;
			modelToControlsShape();
			modelToControlsPath();
		} finally {
			handlingDocumentUpdate = false;
		}
	}

	protected void modelToControlsShape() {
		xStartText.setText(DECIMAL_FORMAT.format(getXAxis().getStart()));
		yStartText.setText(DECIMAL_FORMAT.format(getYAxis().getStart()));
		xStopText.setText(DECIMAL_FORMAT.format(getXAxis().getStop()));
		yStopText.setText(DECIMAL_FORMAT.format(getYAxis().getStop()));
	}

	private void modelToControlsPath() {
		pointsSpinner.setSelection(Math.max(getXAxis().getPoints(), getYAxis().getPoints()));
		stepButton.setSelection(!isContinuous());
		continuousButton.setSelection(isContinuous());
	}

	@Override
	public void dispose() {
		if (line != null) {
			line.removePropertyChangeListener(getRegionModifiedListener());
		}
		super.dispose();
	}

	@Override
	protected IMappingScanRegionShape modelToMappingRegion() {
		var region = new LineMappingRegion();
		region.setxStart(getXAxis().getStart());
		region.setyStart(getYAxis().getStart());
		region.setxStop(getXAxis().getStop());
		region.setyStop(getYAxis().getStop());
		return region;
	}

	@Override
	protected IMapPathModel modelToMappingPath() {
		var path = new TwoAxisLinePointsModel();
		path.setPoints(Math.max(getXAxis().getPoints(), getYAxis().getPoints()));
		path.setBoundingLine(getBoundingLineFromModel());
		path.setAlternating(false);
		path.setContinuous(isContinuous());
		return path;
	}

	private BoundingLine getBoundingLineFromModel() {
		var xStart = getXAxis().getStart();
		var yStart = getYAxis().getStart();
		var length = getXAxis().getStop() - xStart;
		var angle = getYAxis().getStop()- yStart;
		return new BoundingLine(xStart, yStart, length, angle);
	}

	@Override
	protected void handleMappingUpdate(RegionPathState state) {
		var updatedRegion = state.scanRegionShape();
		if (updatedRegion instanceof LineMappingRegion newLine) {
			if (this.line != null) {
				this.line.removePropertyChangeListener(getRegionModifiedListener());
			}
			newLine.addPropertyChangeListener(getRegionModifiedListener());
			this.line = newLine;
		}
	}

	protected void handleRegionMove() {
		if (handlingMappingUpdate) return;
		try {
			handlingMappingUpdate = true;
			double xStart = line.getxStart();
			double yStart = line.getyStart();
			double xStop = line.getxStop();
			double yStop = line.getyStop();
			int numberPoints = getXAxis().calculatedPoints();
			updateAxes(modifyAxis(getXAxis(), xStart, xStop, numberPoints),
					   modifyAxis(getYAxis(), yStart, yStop, numberPoints));
		} finally {
			handlingMappingUpdate = false;
		}
	}

	public PropertyChangeListener getRegionModifiedListener() {
		return regionMoveListener;
	}
}