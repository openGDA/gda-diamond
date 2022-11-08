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
import java.util.Collections;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

import org.eclipse.scanning.api.points.models.BoundingBox;
import org.eclipse.scanning.api.points.models.IMapPathModel;
import org.eclipse.scanning.api.points.models.TwoAxisGridPointsModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;

import gda.mscan.element.Mutator;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.region.CentredRectangleMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.gda.ui.tool.ClientSWTElements;

public class RectangleScanpathEditor extends ScanpathEditor {

	private Text xStartText;
	private Text yStartText;
	private Text xStopText;
	private Text yStopText;

	private Spinner xPointsSpinner;
	private Spinner yPointsSpinner;

	private Button stepButton;
	private Button continuousButton;
	private Button alternatingButton;

	CentredRectangleMappingRegion rectangle;
	private PropertyChangeListener regionMoveListener = change -> handleRegionMove();

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

		new Label(composite, SWT.NONE).setText("X Start");
		new Label(composite, SWT.NONE).setText("X Stop");
		xStartText = createTextControls(composite);
		xStopText = createTextControls(composite);

		new Label(composite, SWT.NONE).setText("Y Start");
		new Label(composite, SWT.NONE).setText("Y Stop");
		yStartText = createTextControls(composite);
		yStopText = createTextControls(composite);

		new Label(composite, SWT.NONE).setText("X Points");
		new Label(composite, SWT.NONE).setText("Y Points");
		xPointsSpinner = createSpinner(composite);
		yPointsSpinner = createSpinner(composite);
	}

	private void createMutatorsControls(Composite parent) {
		Composite radioButtonComposite = ClientSWTElements.composite(parent, 2);

		stepButton = new Button(radioButtonComposite, SWT.RADIO);
		stepButton.setText("Step");
		stepButton.setToolTipText("Step scan");

		continuousButton = new Button(radioButtonComposite, SWT.RADIO);
		continuousButton.setText("Continuous");
		continuousButton.setData(Mutator.CONTINUOUS);
		continuousButton.setToolTipText("Fly scan");
		continuousButton.addSelectionListener(SelectionListener.widgetSelectedAdapter(this::handleMutatorSelection));

		Composite checkBoxComposite = ClientSWTElements.composite(parent, 1);
		alternatingButton = new Button(checkBoxComposite, SWT.CHECK);
		alternatingButton.setText("Alternating");
		alternatingButton.setData(Mutator.ALTERNATING);
		alternatingButton.setToolTipText("Alternating scan");
		alternatingButton.addSelectionListener(SelectionListener.widgetSelectedAdapter(this::handleMutatorSelection));
	}

	private void handleMutatorSelection(SelectionEvent event) {
		var button = (Button) event.getSource();
		var mutator = (Mutator) button.getData();
		if (button.getSelection()) {
			updateModel(addMutator(mutator));
		} else {
			updateModel(removeMutator(mutator));
		}
	}

	@Override
	protected void controlsToModel(){
		if (handlingDocumentUpdate) return;
		try {
			handlingDocumentUpdate = true;
			double xStart = Double.parseDouble(xStartText.getText());
			double yStart = Double.parseDouble(yStartText.getText());
			double xStop = Double.parseDouble(xStopText.getText());
			double yStop = Double.parseDouble(yStopText.getText());
			int xPoints = Integer.parseInt(xPointsSpinner.getText());
			int yPoints = Integer.parseInt(yPointsSpinner.getText());

			updateAxes(modifyAxis(getXAxis(), xStart, xStop, xPoints),
					   modifyAxis(getYAxis(), yStart, yStop, yPoints));

		} finally {
			handlingDocumentUpdate = false;
		}
	}

	@Override
	protected void modelToControls() {
		if (handlingDocumentUpdate) return;
		try {
			handlingDocumentUpdate = true;
			xStartText.setText(DECIMAL_FORMAT.format(getXAxis().getStart()));
			yStartText.setText(DECIMAL_FORMAT.format(getYAxis().getStart()));
			xStopText.setText(DECIMAL_FORMAT.format(getXAxis().getStop()));
			yStopText.setText(DECIMAL_FORMAT.format(getYAxis().getStop()));
			xPointsSpinner.setSelection(getXAxis().getPoints());
			yPointsSpinner.setSelection(getYAxis().getPoints());
			stepButton.setSelection(!isContinuous());
			continuousButton.setSelection(isContinuous());
			alternatingButton.setSelection(isAlternating());
		} finally {
			handlingDocumentUpdate = false;
		}
	}

	@Override
	public void dispose() {
		if (rectangle != null) {
			rectangle.removePropertyChangeListener(regionMoveListener);
		}
		super.dispose();
	}

	@Override
	protected IMappingScanRegionShape modelToMappingRegion() {
		var region = new CentredRectangleMappingRegion();
		region.setxCentre(getxCentre());
		region.setyCentre(getyCentre());
		region.setxRange(getxRange());
		region.setyRange(getyRange());
		return region;
	}


	@Override
	protected IMapPathModel modelToMappingPath() {
		var path = new TwoAxisGridPointsModel();
		path.setxAxisPoints(getXAxis().getPoints());
		path.setyAxisPoints(getYAxis().getPoints());
		path.setBoundingBox(getBoundingBoxFromModel());
		path.setContinuous(isContinuous());
		path.setAlternating(isAlternating());
		return path;
	}

	private BoundingBox getBoundingBoxFromModel() {
		double[] start = new double[] {getXAxis().getStart(), getYAxis().getStart()};
		double[] stop = new double[] {getXAxis().getStop(), getYAxis().getStop()};
		return new BoundingBox(start, stop);
	}

	@Override
	protected void handleMappingUpdate(RegionPathState state) {
		var updatedRegion = state.scanRegionShape();
		if (updatedRegion instanceof CentredRectangleMappingRegion) {
			if (this.rectangle != null) {
				this.rectangle.removePropertyChangeListener(regionMoveListener);
			}
			CentredRectangleMappingRegion newRectangle = (CentredRectangleMappingRegion) updatedRegion;
			newRectangle.addPropertyChangeListener(regionMoveListener);
			this.rectangle = newRectangle;
		}
	}

	private void handleRegionMove() {
		if (handlingMappingUpdate) return;
		try {
			handlingMappingUpdate = true;
			double xStart = rectangle.getxCentre() - rectangle.getxRange()/2;
			double xStop = rectangle.getxCentre() + rectangle.getxRange()/2;
			double yStart = rectangle.getyCentre() - rectangle.getyRange()/2;
			double yStop = rectangle.getyCentre() + rectangle.getyRange()/2;
			int xPoints = getXAxis().calculatedPoints();
			int yPoints = getYAxis().calculatedPoints();

			updateAxes(modifyAxis(getXAxis(), xStart, xStop, xPoints),
					   modifyAxis(getYAxis(), yStart, yStop, yPoints));
		} finally {
			handlingMappingUpdate = false;
		}
	}

	private ScanpathDocument addMutator(Mutator mutator) {
		Map<Mutator, List<Number>> mutatorMap = new EnumMap<>(Mutator.class);
		mutatorMap.put(mutator, Collections.emptyList());

		// Checks whether current map of mutators had another mutator selected and adds it
		if (getModel().getMutators().size() > 0) {
			mutatorMap.put(getCurrentMutator(mutator), Collections.emptyList());
		}

		return new ScanpathDocument(getModel().getModelDocument(), getModel().getScannableTrackDocuments(), mutatorMap);
	}

	private ScanpathDocument removeMutator(Mutator mutator) {
		Map<Mutator, List<Number>> mutatorMap = new EnumMap<>(Mutator.class);

		// Checks whether current map of mutators had another mutator selected and adds it
		if (getModel().getMutators().size() > 1) {
			mutatorMap.put(getCurrentMutator(mutator), Collections.emptyList());
		}

		return new ScanpathDocument(getModel().getModelDocument(), getModel().getScannableTrackDocuments(), mutatorMap);
	}

	private Mutator getCurrentMutator(Mutator mutator) {
		return getModel().getMutators().entrySet().stream()
				.filter(e -> !e.getKey().equals(mutator))
				.map(Map.Entry::getKey)
				.findFirst()
				.orElseThrow(() -> new IllegalStateException("Mutator not found"));
	}

	private double getxRange() {
		return Math.abs(getXAxis().getStop() - getXAxis().getStart());
	}

	private double getyRange() {
		return Math.abs(getYAxis().getStop() - getYAxis().getStart());
	}

	private double getxCentre () {
		return getXAxis().getStart() + getxRange() / 2;
	}

	private double getyCentre() {
		return getYAxis().getStart() + getyRange() / 2;
	}
}