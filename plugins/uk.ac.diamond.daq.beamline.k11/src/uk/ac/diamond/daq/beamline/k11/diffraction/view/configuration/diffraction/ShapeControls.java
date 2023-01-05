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
import java.util.function.Supplier;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.springframework.context.ApplicationListener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.Activator;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ShapeSelectionButtons.ShapeSelectionEvent;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent.UpdatedProperty;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.gda.api.acquisition.AcquisitionTemplateType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;

public class ShapeControls implements CompositeFactory, Reloadable {

	private final Supplier<ScanningParameters> scanningParameters;

	private final List<ShapeDescriptor> shapes;

	private ShapeSelectionButtons buttons;

	private ScanpathDocumentCache scanpathDocumentCache;

	private RegionAndPathController mappingController;

	private Composite controls;
	private ScanpathEditor scanpathEditor;

	private ModelUpdater modelUpdater;

	public ShapeControls(Supplier<ScanningParameters> scanningParameters, List<ShapeDescriptor> shapes) {
		this.scanningParameters = scanningParameters;
		this.shapes = shapes;
		this.scanpathDocumentCache = new ScanpathDocumentCache();
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

		updateSelectionFromDocument();

		initialiseMappingController();

		modelUpdater = new ModelUpdater();
		SpringApplicationContextFacade.addApplicationListener(modelUpdater);

		composite.addDisposeListener(disposeEvent -> dispose());
		return composite;
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

	private void updateSelectionFromDocument() {
		var shape = getInnerScanShape();
		buttons.setSelection(shape);
	}

	private AcquisitionTemplateType getInnerScanShape() {
		var shape = scanningParameters.get().getScanpathDocument().getModelDocument();

		if (shape == AcquisitionTemplateType.DIFFRACTION_TOMOGRAPHY) {
			// I can't handle the outer dimension, so I'll assume you want a grid
			shape = AcquisitionTemplateType.TWO_DIMENSION_GRID;
		}

		return shape;
	}

	/**
	 * Callback for button selection
	 */
	private void updateControls(ShapeSelectionEvent event) {
		var shape = event.selection();
		var oldPath = scanningParameters.get().getScanpathDocument();
		var document = scanpathDocumentCache.cacheAndChangeShape(oldPath, shape);
		scanningParameters.get().setScanpathDocument(document);

		if (scanpathEditor != null) {
			scanpathEditor.dispose();
		}

		scanpathEditor = getDescriptor(event.selection()).editor().get();
		scanpathEditor.addIObserver(this::updateScanpathDocument);
		scanpathEditor.setModel(document);
		scanpathEditor.createEditorPart(controls);
		publishUpdate();
	}

	private ShapeDescriptor getDescriptor(AcquisitionTemplateType shape) {
		return shapes.stream().filter(descriptor -> descriptor.shape().equals(shape)).findFirst().orElseThrow();
	}

	/**
	 * Callback for {@link ScanpathEditor}.
	 */
	private void updateScanpathDocument(Object source, Object argument) {
		if (source.equals(scanpathEditor) && argument instanceof ScanpathDocument document) {
			scanningParameters.get().setScanpathDocument(document);
			scanpathDocumentCache.cache(document);
			publishUpdate();
		}
	}

	private void publishUpdate() {
		SpringApplicationContextFacade.publishEvent(new ScanningAcquisitionChangeEvent(this, UpdatedProperty.PATH));
	}

	@Override
	public void reload() {
		scanpathDocumentCache.cache(scanningParameters.get().getScanpathDocument());
		updateSelectionFromDocument();
	}

	class ModelUpdater implements ApplicationListener<ScanningAcquisitionChangeEvent> {

		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			if (!event.getSource().equals(ShapeControls.this) &&
				event.getProperty().equals(UpdatedProperty.PATH)) {
					scanpathEditor.setModel(scanningParameters.get().getScanpathDocument());
				}
		}

	}
}
