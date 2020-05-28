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

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.function.BiConsumer;
import java.util.function.Function;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.MutablePair;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Widget;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegion;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.ui.diffraction.base.DiffractionParameters;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.ShapeType;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.images.ClientImages;

/**
 * Components representing the GUI shape elements
 *
 * @author Maurizio Nagni
 */
public class ShapesTemplateFactory implements DiffractionCompositeInterface {

	/**
	 * The selected {@link ShapeType}. Is valued by selecting one {@link ShapeComposite}.
	 * This observable is propagated to all external mapping component
	 */
	private final SelectObservableValue<ShapeType> selectedShapeObservable = new SelectObservableValue<>();


	/**
	 * The selected {@link IMappingScanRegionShape}. Is valued by selecting one {@link ShapeComposite}.
	 * This observable is internal only.
	 */
	private SelectObservableValue<IMappingScanRegionShape> selectedMSRSObservable = new SelectObservableValue<>();

	private final List<ShapeComposite> shapes = new ArrayList<>();

	private final DataBindingContext regionDBC = new DataBindingContext(); // For bindings that refresh with the region
	private final List<MutablePair<Button, IMappingScanRegionShape>> buttonToRegionShape = new ArrayList<>();

	private final DataBindingContext dbc;
	private final DiffractionParameters templateData;
	private final RegionAndPathController rapController;
	private ShapeTemplateDataHelper templateHelper;

	public ShapesTemplateFactory(DataBindingContext dbc, DiffractionParameters templateData,
			RegionAndPathController rapController) {
		super();
		this.dbc = dbc;
		this.templateData = templateData;
		this.rapController = rapController;
		this.templateHelper = new ShapeTemplateDataHelper(templateData);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite container = ClientSWTElements.createComposite(parent, SWT.NONE, 1);
		ClientSWTElements.createLabel(container, SWT.NONE, ClientMessages.SHAPE);
		shapes.add(createShapeComposite(ShapeType.POINT, ClientMessages.POINT_SHAPE_TP, ClientImages.POINT));
		shapes.add(createShapeComposite(ShapeType.CENTRED_RECTANGLE, ClientMessages.CENTERED_RECTANGULAR_SHAPE_TP,
				ClientImages.CENTERED_RECTAGLE));
		shapes.add(createShapeComposite(ShapeType.LINE, ClientMessages.LINE_SHAPE_TP, ClientImages.LINE));
		shapes.stream().forEach(s -> s.createComposite(container, style));
		return parent;
	}

	@Override
	public void bindControls() {
		// loop over shapes GUI
		shapes.stream().forEach(s -> {
			bindShape(s.getShapeDefinition());
		});
		// The first shape selected is POINT because rapController is initialised so.
		updateRegionShapeBindings();

		// set up the trigger for the path re-ralculation process to update all affected views
		refreshSelectedMSRSObservable(Optional.empty());
	}

	@Override
	public void updateScanPointBindings(final IScanPointGeneratorModel newPathValue, ShapeType shapeType) {
		updateRegionShapeBindings();
	}

	@SuppressWarnings("unchecked")
	public final IObservableValue<IMappingScanRegionShape> getMappingScanRegionShapeObservableValue() {
		return BeanProperties.value("region").observe(rapController.getScanRegionFromBean());
	}

	public SelectObservableValue<ShapeType> getSelectedShape() {
		return selectedShapeObservable;
	}

	private void bindShape(ImmutablePair<ShapeType, Button> shapeDefinition) {
		selectedShapeObservable.addOption(shapeDefinition.getKey(),
				getRadioButtonSelectionObservableValue(shapeDefinition.getValue()));
		regionFromShapeType(shapeDefinition.getKey())
				.ifPresent(reg -> buttonToRegionShape.add(MutablePair.of(shapeDefinition.getValue(), reg)));
	}

	private Optional<IMappingScanRegionShape> regionFromShapeType(ShapeType shapeType) {
		if (shapeType == null)
			return Optional.empty();
		return rapController.getTemplateRegions().stream().filter(shapeType::hasMappedShape).findFirst();
	}

	/**
	 * Rewrites the bindings relating to the mapping bean's region shape so that the {@link Button}s and
	 * {@link StyledText} summary controls get linked to the correct property on the correct {@link IMappingScanRegion}
	 * when the region shape is changed by any linked views
	 */
	private void updateRegionShapeBindings() {
		IObservableValue<IMappingScanRegionShape> mbShapeObservableValue = getMappingScanRegionShapeObservableValue();
		regionDBC.bindValue(selectedShapeObservable, mbShapeObservableValue,
				UpdateValueStrategy.create(shapeToMappingRegionShape),
				UpdateValueStrategy.create(mappingRegionShapeToShape));
	}

	private IConverter shapeToMappingRegionShape = IConverter.create(ShapeType.class, IMappingScanRegionShape.class,
			shapeType -> regionFromShapeType((ShapeType) shapeType).orElse(null));

	/**
	 * Sets the state of the composite radio button observable used to set the region shape when this has happened by
	 * other means than clicking on of the buttons
	 *
	 * @param loadedShape
	 *            The new {@link IMappingScanRegionShape} to be reflected by the control
	 */
	public void refreshSelectedMSRSObservable(Optional<IMappingScanRegionShape> loadedShape) {
		if (selectedMSRSObservable != null) {
			selectedMSRSObservable.removeValueChangeListener(rapController.getRegionSelectorListener());
			selectedMSRSObservable.dispose();
		}
		selectedMSRSObservable = new SelectObservableValue<>();
		for (MutablePair<Button, IMappingScanRegionShape> pair : buttonToRegionShape) {
			if (loadedShape.isPresent() && pair.right.getClass().equals(loadedShape.get().getClass())) {
				pair.setRight(loadedShape.get());
			}
			selectedMSRSObservable.addOption(pair.right, getRadioButtonSelectionObservableValue(pair.left));
		}
		selectedMSRSObservable.addValueChangeListener(rapController.getRegionSelectorListener());
	}

	@SuppressWarnings("unchecked")
	private IObservableValue<Boolean> getRadioButtonSelectionObservableValue(Button button) {
		return WidgetProperties.selection().observe(button);
	}

	private DiffractionParameters getTemplateData() {
		return templateData;
	}

	private ShapeComposite createShapeComposite(ShapeType shapeType, ClientMessages tooltip, ClientImages icon) {
		return new ShapeCompositeBase(shapeType, tooltip, icon, selectionListener.apply(shapeType));
	}

	private BiConsumer<ShapeType, Widget> selectButton = (shapeType, radio) -> {
		if (Button.class.isInstance(radio) && Button.class.cast(radio).getSelection()) {
			templateHelper.update(shapeType);
		}
	};

	private Function<ShapeType, Listener> selectionListener = shapeType -> event -> selectButton.accept(shapeType,
			event.widget);
}
