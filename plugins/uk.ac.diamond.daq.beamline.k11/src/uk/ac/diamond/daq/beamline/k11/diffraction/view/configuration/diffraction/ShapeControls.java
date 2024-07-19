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

import java.util.List;
import java.util.Optional;
import java.util.function.Function;
import java.util.function.Supplier;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.springframework.context.ApplicationListener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.Activator;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ShapeSelectionButtons.ShapeSelectionEvent;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent.UpdatedProperty;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument.Axis;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanningParametersUtils;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.gda.api.acquisition.TrajectoryShape;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;

public class ShapeControls implements CompositeFactory, Reloadable {

	private final Supplier<ScanningParameters> scanningParameters;

	private final List<ShapeDescriptor> shapes;
	private Optional<Function<ScanningParameters, TrajectoryShape>> shapeResolver = Optional.empty();

	private ShapeSelectionButtons buttons;

	private ScannableTrackDocumentCache axesCache;

	private RegionAndPathController mappingController;

	private Composite controls;
	private ScanpathEditor scanpathEditor;

	private ModelUpdater modelUpdater;

	/** basic way to differentiate between a scan being loaded and a manual shape change */
	private boolean reloading;

	public ShapeControls(Supplier<ScanningParameters> scanningParameters, List<ShapeDescriptor> shapes) {
		this.scanningParameters = scanningParameters;
		this.shapes = shapes;
		this.axesCache = new ScannableTrackDocumentCache(getAxes());
	}

	@Override
	public Composite createComposite(Composite parent, int ignored) {
		var composite = new Composite(parent, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(3).applyTo(composite);
		GridDataFactory.fillDefaults().applyTo(composite);

		buttons = new ShapeSelectionButtons(composite, shapes);
		buttons.addListener(this::handleShapeSelectionEvent);

		GridDataFactory.fillDefaults().align(SWT.CENTER, SWT.FILL).grab(false, true).applyTo(
				new Label(composite, SWT.VERTICAL | SWT.SEPARATOR));

		controls = new Composite(composite, SWT.NONE);
		GridLayoutFactory.fillDefaults().extendedMargins(10, 0, 0, 0).applyTo(controls);
		GridDataFactory.fillDefaults().align(SWT.FILL, SWT.TOP).grab(true, false).applyTo(controls);

		updateShapeSelectionFromDocument();

		initialiseMappingController();

		modelUpdater = new ModelUpdater();
		SpringApplicationContextFacade.addApplicationListener(modelUpdater);

		composite.addDisposeListener(disposeEvent -> dispose());
		return composite;
	}

	private List<ScannableTrackDocument> getAxes() {
		var scan = scanningParameters.get().getScanpathDocument();
		return List.of(ScanningParametersUtils.getAxis(scan, Axis.X), ScanningParametersUtils.getAxis(scan, Axis.Y));
	}

	private void handleShapeSelectionEvent(ShapeSelectionEvent event) {
		switch (event.type()) {
		case REDRAW:
			var region = getDescriptor(event.selection()).mappingRegion();
			updateMappingController(region);
			break;
		case SHAPE_CHANGE:
			updateControls(event);
			break;
		default:
			break;

		}
	}

	private void dispose() {
		if (scanpathEditor != null) {
			scanpathEditor.dispose();
		}
		SpringApplicationContextFacade.removeApplicationListener(modelUpdater);
	}

	private void updateMappingController(IMappingScanRegionShape mappingRegion) {
		mappingController.getRegionSelectorListener().handleRegionChange(mappingRegion);
	}

	private void initialiseMappingController() {
		mappingController = Activator.getService(RegionAndPathController.class);
		mappingController.initialise();
	}

	private void updateShapeSelectionFromDocument() {
		var shape = getShape();
		buttons.setSelection(shape);

	}

	private TrajectoryShape getShape() {
		var scan = scanningParameters.get().getScanpathDocument();
		var innerScan = scan.getTrajectories().get(0);

		if (shapes.stream().anyMatch(descriptor -> descriptor.shape().equals(innerScan.getShape()))) {
			return innerScan.getShape();
		} else if (shapeResolver.isPresent()) {
			return shapeResolver.get().apply(scanningParameters.get());
		}

		return TrajectoryShape.TWO_DIMENSION_GRID;
	}

	/**
	 * Callback for button selection
	 */
	private void updateControls(ShapeSelectionEvent event) {
		// cache axes relating to previous shape
		event.previousSelection().ifPresent(previousSelection -> axesCache.cache(previousSelection, getAxes()));

		// retrieve axes relating to this shape
		var shape = event.selection();
		var scan = scanningParameters.get().getScanpathDocument();

		if (!reloading) {
			// mutate scan in place with new axes
			ScanningParametersUtils.updateAxes(scan, axesCache.retrieve(shape));

			// update shape in trajectory, if both axes are in trajectory
			var oldTrajectory = scan.getTrajectories().stream()
									.filter(trajectory -> trajectory.getAxes().stream().anyMatch(scannable -> scannable.getAxis().equals(Axis.X)))
									.filter(trajectory -> trajectory.getAxes().stream().anyMatch(scannable -> scannable.getAxis().equals(Axis.Y)))
									.findFirst();

			oldTrajectory.ifPresent(trajectory -> ScanningParametersUtils.updateTrajectoryShape(scan, trajectory, shape));

		}

		if (scanpathEditor != null) {
			scanpathEditor.dispose();
		}

		scanpathEditor = getDescriptor(event.selection()).editor().get();
		scanpathEditor.addIObserver(this::updateScanpathDocument);
		scanpathEditor.setModel(scan);
		scanpathEditor.createEditorPart(controls);
		publishUpdate();
	}

	private ShapeDescriptor getDescriptor(TrajectoryShape shape) {
		return shapes.stream().filter(descriptor -> descriptor.shape().equals(shape)).findFirst().orElseThrow();
	}

	/**
	 * Callback for {@link ScanpathEditor}.
	 */
	private void updateScanpathDocument(Object source, Object argument) {
		if (source.equals(scanpathEditor) && argument instanceof ScanpathDocument document) {
			scanningParameters.get().setScanpathDocument(document);
			Display.getDefault().syncExec(() -> buttons.getSelection().ifPresent(shape -> axesCache.cache(shape, getAxes())));
			publishUpdate();
		}
	}

	private void publishUpdate() {
		SpringApplicationContextFacade.publishEvent(new ScanningAcquisitionChangeEvent(this, UpdatedProperty.PATH));
	}

	public void setShapeResolver(Function<ScanningParameters, TrajectoryShape> shapeResolver) {
		this.shapeResolver = Optional.of(shapeResolver);
	}

	private void updateModelInEditor() {
		scanpathEditor.setModel(scanningParameters.get().getScanpathDocument());
	}

	@Override
	public void reload() {
		reloading = true;
		updateShapeSelectionFromDocument();
		updateModelInEditor();
		reloading = false;
	}

	class ModelUpdater implements ApplicationListener<ScanningAcquisitionChangeEvent> {

		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			if (!event.getSource().equals(ShapeControls.this) &&
				event.getProperty().equals(UpdatedProperty.PATH)) {
					updateModelInEditor();
				}
		}

	}
}
