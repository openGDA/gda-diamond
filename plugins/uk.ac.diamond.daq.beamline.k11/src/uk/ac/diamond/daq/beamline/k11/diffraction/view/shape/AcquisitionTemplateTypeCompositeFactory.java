/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.shape;

import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.mappingRegionShapeToShape;
import static uk.ac.gda.ui.tool.ClientMessages.CENTERED_RECTANGULAR_SHAPE_TP;
import static uk.ac.gda.ui.tool.ClientMessages.EMPTY_MESSAGE;
import static uk.ac.gda.ui.tool.ClientMessages.LINE_SHAPE_TP;
import static uk.ac.gda.ui.tool.ClientMessages.POINT_SHAPE_TP;
import static uk.ac.gda.ui.tool.ClientMessages.SHAPE;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientButton;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.BiConsumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.core.databinding.observable.value.ValueChangeEvent;
import org.eclipse.core.databinding.observable.value.ValueDiff;
import org.eclipse.jface.databinding.swt.typed.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Widget;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.helper.ScanpathDocumentHelper;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.region.CentredRectangleMappingRegion;
import uk.ac.diamond.daq.mapping.region.LineMappingRegion;
import uk.ac.diamond.daq.mapping.region.PointMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.gda.client.properties.acquisition.AcquisitionKeys;
import uk.ac.gda.client.properties.acquisition.AcquisitionPropertyType;
import uk.ac.gda.client.properties.acquisition.AcquisitionSubType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.WidgetUtilities;
import uk.ac.gda.ui.tool.document.DocumentFactory;
import uk.ac.gda.ui.tool.images.ClientImages;

/**
 * Components representing the GUI shape elements
 *
 * @author Maurizio Nagni
 */
public class AcquisitionTemplateTypeCompositeFactory implements DiffractionCompositeInterface {

	private static final String ACQUISITION_TEMPLATE_TYPE_LISTENER = "AcquisitionTemplateTypeListener";
	private static final String ACQUISITION_TEMPLATE_TYPE = "AcquisitionTemplateType";
	private static final String MAPPING_SCAN_REGION_SHAPE_TYPE = "MappingScanRegionShapeType";

	private static final Map<AcquisitionTemplateType, Class<? extends IMappingScanRegionShape>> acquisitionTemplateTypeToMappingScan
		= new HashMap<AcquisitionTemplateType, Class<? extends IMappingScanRegionShape>>() {
		{
			put(AcquisitionTemplateType.TWO_DIMENSION_POINT, PointMappingRegion.class);
			put(AcquisitionTemplateType.TWO_DIMENSION_LINE, LineMappingRegion.class);
			put(AcquisitionTemplateType.TWO_DIMENSION_GRID, CentredRectangleMappingRegion.class);
		}
	};

	public static final Predicate<? super IMappingScanRegionShape> filterRegionScan(AcquisitionTemplateType acquisitionTemplateType) {
		return mappingRegion -> acquisitionTemplateTypeToMappingScan.get(acquisitionTemplateType).isInstance(mappingRegion);
	}

	/**
	 * The selected {@link AcquisitionTemplateType}. Is valued by selecting one {@link AcquisitionTypeComposite}. This observable is propagated
	 * to all external mapping component
	 */
	private final SelectObservableValue<AcquisitionTemplateType> selectedAcquisitionTypeObservable = new SelectObservableValue<>();

	/**
	 * The selected {@link IMappingScanRegionShape}. Is valued by selecting one {@link AcquisitionTypeComposite}. This observable
	 * is internal only.
	 */
	private SelectObservableValue<IMappingScanRegionShape> selectedMappingScanRegionShape;

	private final List<Button> acquisitionTypeRadios = new ArrayList<>();

	private final DataBindingContext regionDBC = new DataBindingContext();
	private  RegionAndPathController rapController;

	private ScanpathDocumentHelper scanpathDocumentHelper;
	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	public AcquisitionTemplateTypeCompositeFactory(Supplier<ScanningAcquisition> acquisitionSupplier,
			RegionAndPathController rapController) {
		super();
		this.rapController = rapController;
		this.acquisitionSupplier = acquisitionSupplier;
		this.scanpathDocumentHelper = new ScanpathDocumentHelper(this::getScanningParameters);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		var container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.FILL, SWT.TOP).grab(true, true).applyTo(container);

		var label = createClientLabel(container, style, SHAPE);
		createClientGridDataFactory().align(SWT.FILL, SWT.TOP).applyTo(label);

		acquisitionTypeRadios.add(createAcquisitionTypeRadio(container,
				AcquisitionTemplateType.TWO_DIMENSION_POINT, POINT_SHAPE_TP, ClientImages.POINT));
		acquisitionTypeRadios.add(createAcquisitionTypeRadio(container,
				AcquisitionTemplateType.TWO_DIMENSION_GRID, CENTERED_RECTANGULAR_SHAPE_TP, ClientImages.CENTERED_RECTAGLE));
		acquisitionTypeRadios.add(createAcquisitionTypeRadio(container,
				AcquisitionTemplateType.TWO_DIMENSION_LINE, LINE_SHAPE_TP, ClientImages.LINE));

		// Releases resources before dispose
		container.addDisposeListener(event -> dispose()	);
		return container;
	}

	@Override
	public void initialiseElements() {
		acquisitionTypeRadios.stream()
			.forEach(radio -> {
				boolean selected = getDataObject(radio,
					AcquisitionTemplateType.class, ACQUISITION_TEMPLATE_TYPE).equals(getSelectedAcquisitionTemplateType());
				radio.setSelection(selected);
			});
	}

	@Override
	public void initializeBinding() {
		// Executed only on composite creation
		if (selectedMappingScanRegionShape == null) {
			rapControllerListenToMappingScanRegionShape();
			acquisitionTemplateTypeCompositeListenToMappingScanRegionShape();
		}

		acquisitionTypeRadios.stream()
			.forEach(radio -> {
				if (radio.getSelection()) {
					selectedMappingScanRegionShape.setValue(getDataObject(radio, IMappingScanRegionShape.class, MAPPING_SCAN_REGION_SHAPE_TYPE));
					rapController.getRegionSelectorListener().handleValueChange(new ValueChangeEvent<>(selectedMappingScanRegionShape,
							new ValueDiff<IMappingScanRegionShape>() {

						@Override
						public IMappingScanRegionShape getOldValue() {
							return null;
						}

						@Override
						public IMappingScanRegionShape getNewValue() {
							return selectedMappingScanRegionShape.getValue();
						}
					}));
				}
		});
	}

	@SuppressWarnings("unchecked")
	public final IObservableValue<IMappingScanRegionShape> getMappingScanRegionShapeObservableValue() {
		return BeanProperties.value("region").observe(rapController.getScanRegionFromBean());
	}

	private void dispose() {
		acquisitionTypeRadios.stream()
			.forEach(r ->
				r.removeListener(SWT.SELECTED, getDataObject(r, Listener.class, ACQUISITION_TEMPLATE_TYPE_LISTENER))
			);
	}

	public SelectObservableValue<AcquisitionTemplateType> getSelectedAcquisitionType() {
		return selectedAcquisitionTypeObservable;
	}

	private IConverter shapeToMappingRegionShape = IConverter.create(AcquisitionTemplateType.class, IMappingScanRegionShape.class,
			acquisitionTemplateType -> regionFromShapeType(((AcquisitionTemplateType) acquisitionTemplateType))
				.orElse(null));

	/**
	 * Sets the state of the composite radio button observable used to set the region shape when this has happened by
	 * other means than clicking on of the buttons
	 *
	 * @param loadedShape
	 *            The new {@link IMappingScanRegionShape} to be reflected by the control
	 */
	public void refreshSelectedMSRSObservable(Optional<IMappingScanRegionShape> loadedShape) {
		acquisitionTypeRadios.stream().forEach(radio -> {
			IMappingScanRegionShape mappingScanRegionShape = getDataObject(radio, IMappingScanRegionShape.class, MAPPING_SCAN_REGION_SHAPE_TYPE);
			if (loadedShape.isPresent() && mappingScanRegionShape.getClass().equals(loadedShape.get().getClass())) {
				radio.setData(MAPPING_SCAN_REGION_SHAPE_TYPE, loadedShape.get());
				mappingScanRegionShape = loadedShape.get();
			}
		});
	}

	private Button createAcquisitionTypeRadio(Composite parent,
			AcquisitionTemplateType acquisitionTemplateType, ClientMessages tooltip, ClientImages icon) {
		var button = createClientButton(parent, SWT.RADIO, EMPTY_MESSAGE, tooltip, icon);
		ClientSWTElements.createClientGridDataFactory().applyTo(button);

		// sets the button data (the shape it refers to)
		var listener = selectionListener.apply(acquisitionTemplateType);
		button.setData(ACQUISITION_TEMPLATE_TYPE_LISTENER, listener);
		button.setData(ACQUISITION_TEMPLATE_TYPE, acquisitionTemplateType);

		WidgetUtilities.addWidgetDisposableListener(button, SWT.Selection,  listener);

		setIMappingScanRegionShape(button);
		return button;
	}

	private BiConsumer<AcquisitionTemplateType, Widget> selectButton = (acquisitionTemplateType, radio) -> {
		boolean selected = Optional.ofNullable(radio)
				.map(Button.class::cast)
				.map(Button::getSelection)
				.orElseGet(() -> false);

		if (selected) {
			getDocumentFactory()
				.buildScanpathBuilder(new AcquisitionKeys(AcquisitionPropertyType.DIFFRACTION, AcquisitionSubType.STANDARD, acquisitionTemplateType))
				.ifPresent(scanpathDocumentHelper::updateScanPathDocument);

			SpringApplicationContextFacade.publishEvent(new ScanningAcquisitionChangeEvent(this));
		}
	};

	private Function<AcquisitionTemplateType, Listener> selectionListener = acquisitionTemplateType ->
		event -> selectButton.accept(acquisitionTemplateType, event.widget);

	private Optional<IMappingScanRegionShape> regionFromShapeType(AcquisitionTemplateType acquisitionTemplateType) {
		if (acquisitionTemplateType == null)
			return Optional.empty();
		return rapController.getTemplateRegions().stream()
				.filter(filterRegionScan(acquisitionTemplateType))
				.findFirst();
	}

	private void setIMappingScanRegionShape(Button button) {
		regionFromShapeType(getDataObject(button, AcquisitionTemplateType.class, ACQUISITION_TEMPLATE_TYPE))
			.ifPresent(mappingScan ->
				button.setData(MAPPING_SCAN_REGION_SHAPE_TYPE, mappingScan)
			);
	}

	// To replace with WidgetUtilities.getDataObject when available (K11-837)
	private static <T> T getDataObject(Widget widget, Class<T> clazz, String dataKey) {
		return Optional.ofNullable(widget.getData(dataKey))
				.map(clazz::cast)
				.orElseGet(() -> null);
	}


	/**
	 * Observes the value of the radios so the rapController.regionSelectorListener can listen at it
	 */
	private void rapControllerListenToMappingScanRegionShape() {
		selectedMappingScanRegionShape = new SelectObservableValue<>();
		acquisitionTypeRadios.stream().forEach(radio -> {
			IMappingScanRegionShape mappingScanRegionShape = getDataObject(radio, IMappingScanRegionShape.class, MAPPING_SCAN_REGION_SHAPE_TYPE);
			selectedMappingScanRegionShape.addOption(mappingScanRegionShape, getRadioButtonSelectionObservableValue(radio));
		});
		selectedMappingScanRegionShape.addValueChangeListener(rapController.getRegionSelectorListener());
	}

	private void acquisitionTemplateTypeCompositeListenToMappingScanRegionShape() {
		IObservableValue<IMappingScanRegionShape> rapControllerScanRegion = getMappingScanRegionShapeObservableValue();
		rapControllerScanRegion.addValueChangeListener(ValueChangeEvent::getObservableValue);

		regionDBC.bindValue(selectedAcquisitionTypeObservable, rapControllerScanRegion,
				UpdateValueStrategy.create(shapeToMappingRegionShape),
				UpdateValueStrategy.create(mappingRegionShapeToShape));
	}

	/**
	 * Observe the selected/unselected status of a radio
	 * @param button
	 * @return
	 */
	@SuppressWarnings("unchecked")
	private IObservableValue<Boolean> getRadioButtonSelectionObservableValue(Button button) {
		return WidgetProperties.buttonSelection().observe(button);
	}

	// ------------ UTILS ----
	private ScanningAcquisition getScanningAcquisition() {
		return this.acquisitionSupplier.get();
	}

	private ScanningParameters getScanningParameters() {
		return getScanningAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();
	}

	private AcquisitionTemplateType getSelectedAcquisitionTemplateType() {
		return getScanningParameters().getScanpathDocument().getModelDocument();
	}

	private DocumentFactory getDocumentFactory() {
		return SpringApplicationContextFacade.getBean(DocumentFactory.class);
	}
}