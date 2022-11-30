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

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;
import static uk.ac.gda.ui.tool.ClientSWTElements.getImage;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.Supplier;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.swt.widgets.Widget;
import org.springframework.context.ApplicationListener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.Activator;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent.UpdatedProperty;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.region.CentredRectangleMappingRegion;
import uk.ac.diamond.daq.mapping.region.LineMappingRegion;
import uk.ac.diamond.daq.mapping.region.PointMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.gda.api.acquisition.AcquisitionTemplateType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.images.ClientImages;

public class ShapeControls implements CompositeFactory, Reloadable {

	private final Supplier<ScanningParameters> scanningParameters;

	private Map<Widget, AcquisitionTemplateType> buttonToShape;
	private Map<AcquisitionTemplateType, IMappingScanRegionShape> shapeToMappingRegion;
	private Map<AcquisitionTemplateType, Supplier<ScanpathEditor>> editors;
	private ScanpathDocumentCache scanpathDocumentCache;

	private RegionAndPathController mappingController;

	private Composite controls;
	private ScanpathEditor scanpathEditor;

	private ModelUpdater modelUpdater;

	public ShapeControls(Supplier<ScanningParameters> scanningParameters) {
		this.scanningParameters = scanningParameters;
		buttonToShape = new HashMap<>();

		shapeToMappingRegion = new EnumMap<>(AcquisitionTemplateType.class);
		shapeToMappingRegion.put(AcquisitionTemplateType.TWO_DIMENSION_POINT, new PointMappingRegion());
		shapeToMappingRegion.put(AcquisitionTemplateType.TWO_DIMENSION_GRID, new CentredRectangleMappingRegion());
		shapeToMappingRegion.put(AcquisitionTemplateType.TWO_DIMENSION_LINE, new LineMappingRegion());

		editors = new EnumMap<>(AcquisitionTemplateType.class);
		editors.put(AcquisitionTemplateType.TWO_DIMENSION_POINT, PointScanpathEditor::new);
		editors.put(AcquisitionTemplateType.TWO_DIMENSION_LINE, LineScanpathEditor::new);
		editors.put(AcquisitionTemplateType.TWO_DIMENSION_GRID, RectangleScanpathEditor::new);

		this.scanpathDocumentCache = new ScanpathDocumentCache();
	}

	@Override
	public Composite createComposite(Composite parent, int ignored) {
		var composite = new Composite(parent, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(3).applyTo(composite);
		GridDataFactory.fillDefaults().applyTo(composite);

		ToolBar toolBar = new ToolBar(composite, SWT.FLAT | SWT.VERTICAL);
		GridDataFactory.swtDefaults().align(SWT.LEFT, SWT.TOP).applyTo(toolBar);

		addShape(toolBar, AcquisitionTemplateType.TWO_DIMENSION_POINT, ClientImages.POINT);
		addShape(toolBar, AcquisitionTemplateType.TWO_DIMENSION_LINE, ClientImages.LINE);
		addShape(toolBar, AcquisitionTemplateType.TWO_DIMENSION_GRID, ClientImages.CENTERED_RECTAGLE);

		divider(toolBar);

		var redraw = new ToolItem(toolBar, SWT.PUSH);
		var icon = getImage(ClientImages.MAP_REDRAW);
		redraw.setImage(icon);
		redraw.setToolTipText("Redraw region in map");
		redraw.addSelectionListener(widgetSelectedAdapter(selection -> updateMappingController()));
		redraw.addDisposeListener(dispose -> icon.dispose());

		GridDataFactory.fillDefaults().align(SWT.CENTER, SWT.FILL).grab(false, true).applyTo(
				new Label(composite, SWT.VERTICAL | SWT.SEPARATOR));

		controls = new Composite(composite, SWT.NONE);
		GridLayoutFactory.fillDefaults().extendedMargins(10, 0, 0, 0).applyTo(controls);
		GridDataFactory.fillDefaults().align(SWT.FILL, SWT.TOP).grab(true, false).applyTo(controls);

		buttonToShape.keySet().stream()
			.filter(ToolItem.class::isInstance).map(ToolItem.class::cast)
			.forEach(item -> item.addSelectionListener(widgetSelectedAdapter(event -> {
				if (item.getSelection()) updateControls();
			})));

		updateSelectionFromDocument();

		initialiseMappingController();

		modelUpdater = new ModelUpdater();
		SpringApplicationContextFacade.addApplicationListener(modelUpdater);

		composite.addDisposeListener(disposeEvent -> dispose());
		return composite;
	}

	private void dispose() {
		if (scanpathEditor != null) {
			scanpathEditor.dispose();
		}
		SpringApplicationContextFacade.removeApplicationListener(modelUpdater);
	}

	private void addShape(ToolBar toolBar, AcquisitionTemplateType shape, ClientImages image) {
		var button = new ToolItem(toolBar, SWT.RADIO);
		var icon = getImage(image);
		button.setImage(icon);
		button.addDisposeListener(dispose -> icon.dispose());
		buttonToShape.put(button, shape);
	}

	@SuppressWarnings("unused")
	private void divider(ToolBar toolBar) {
		new ToolItem(toolBar, SWT.SEPARATOR);
	}

	private void updateMappingController() {
		var mappingRegion = getSelectedMappingRegion();
		mappingController.getRegionSelectorListener().handleRegionChange(mappingRegion);
		mappingController.changePath(mappingController.getValidPathsList(mappingRegion).get(0));
	}

	private void initialiseMappingController() {
		mappingController = Activator.getService(RegionAndPathController.class);
		mappingController.initialise();
	}

	private Optional<ToolItem> getSelectedButton() {
		 return buttonToShape.keySet().stream()
			.filter(ToolItem.class::isInstance).map(ToolItem.class::cast)
			.filter(ToolItem::getSelection).findFirst();
	}

	public void disableShape(AcquisitionTemplateType shape) {
		buttonToShape.entrySet().stream()
			.filter(entry -> entry.getValue() == shape)
			.map(Map.Entry::getKey)
			.filter(ToolItem.class::isInstance).map(ToolItem.class::cast)
			.findFirst().ifPresent(button -> button.setEnabled(false));
	}

	/**
	 * Call only if sure that a button is selected!
	 */
	private AcquisitionTemplateType getSelectedShape() {
		return buttonToShape.get(getSelectedButton().orElseThrow());
	}

	private IMappingScanRegionShape getSelectedMappingRegion() {
		return shapeToMappingRegion.get(getSelectedShape());
	}

	private void updateSelectionFromDocument() {

		// find button mapped to the current document's shape
		var shape = getInnerScanShape();

		var buttonToSelect = buttonToShape.entrySet().stream()
				.filter(entry -> entry.getValue().equals(shape))
				.map(Map.Entry::getKey)
				.filter(ToolItem.class::isInstance).map(ToolItem.class::cast)
				.findFirst()
				.orElseThrow(() -> new IllegalStateException("Current acquisition has unexpected shape: " + shape.toString()));


		// deselect any previous selection
		getSelectedButton().ifPresent(button -> button.setSelection(false));

		// programmatically select it and notify it's listeners
		buttonToSelect.setSelection(true);
		buttonToSelect.notifyListeners(SWT.Selection, new Event());
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
	private void updateControls() {
		var shape = getSelectedShape();
		var oldPath = scanningParameters.get().getScanpathDocument();
		var document = scanpathDocumentCache.cacheAndChangeShape(oldPath, shape);
		scanningParameters.get().setScanpathDocument(document);

		if (scanpathEditor != null) {
			scanpathEditor.dispose();
		}

		scanpathEditor = editors.get(shape).get();
		scanpathEditor.addIObserver(this::updateScanpathDocument);
		scanpathEditor.setModel(document);
		scanpathEditor.createEditorPart(controls);
		publishUpdate();
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
